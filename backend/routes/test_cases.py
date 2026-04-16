"""测试用例路由"""
import os
from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import Project, NLTestCase, PyTestCase, StructuredTestCase
from extensions import db
from services import claude_service

test_cases = Blueprint('test_cases', __name__, url_prefix='/api/test-cases')


@test_cases.route('/nl', methods=['POST'])
@login_required
def generate_nl():
    """生成自然语言测试用例"""
    data = request.get_json()

    project_id = data.get('project_id')
    function_id = data.get('function_id')
    description = data.get('description')
    selected_files = data.get('selected_files', [])

    if not project_id or not function_id or not description:
        return jsonify({'success': False, 'message': '缺少必要参数'}), 400

    project = Project.query.get(project_id)
    if not project:
        return jsonify({'success': False, 'message': '项目不存在'}), 404

    # 读取选中的文件内容，如果没有选择文件，则自动读取所有源码
    source_code = ""
    if project.source_path:
        if selected_files:
            # 用户选择了特定文件
            for file_path in selected_files:
                full_path = os.path.join(project.source_path, file_path)
                if os.path.exists(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            source_code += f"\n# 文件：{file_path}\n{f.read()}\n"
                    except:
                        pass
        else:
            # 自动读取项目中的所有源码文件
            source_code = read_all_project_files(project.source_path)

    # 调用 Claude 服务生成自然语言测试用例
    nl_content = claude_service.analyze_code_and_generate_nl(
        source_code, function_id, description
    )

    # 保存到数据库
    nl_test_case = NLTestCase(
        project_id=project_id,
        function_id=function_id,
        description=description,
        nl_content=nl_content
    )
    db.session.add(nl_test_case)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '自然语言测试用例生成成功',
        'nl_test_case': {
            'id': nl_test_case.id,
            'function_id': nl_test_case.function_id,
            'nl_content': nl_content,
            'created_at': nl_test_case.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })


def read_all_project_files(source_path, max_size=500000):
    """读取项目中所有源码文件，限制总大小"""
    import os
    source_code = ""
    total_size = 0
    extensions = ['.py', '.js', '.ts', '.vue', '.jsx', '.tsx', '.java']
    file_count = 0
    max_files = 20  # 最多读取 20 个文件

    for root, dirs, files in os.walk(source_path):
        # 跳过隐藏目录和常见不需要目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'dist', 'build']]

        for file in files:
            if file_count >= max_files or total_size >= max_size:
                break

            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_path)

                # 检查文件大小
                try:
                    file_size = os.path.getsize(file_path)
                    if total_size + file_size > max_size:
                        continue

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 限制单个文件最大大小
                    if len(content) > 50000:
                        content = content[:50000] + "\n# ... (文件内容被截断)"

                    source_code += f"\n# ========== 文件：{rel_path} ==========\n{content}\n\n"
                    total_size += len(content.encode('utf-8'))
                    file_count += 1
                except:
                    pass

    return source_code


@test_cases.route('/nl', methods=['GET'])
@login_required
def get_nl_list():
    """获取自然语言测试用例列表"""
    project_id = request.args.get('project_id', type=int)

    query = NLTestCase.query.order_by(NLTestCase.created_at.desc())
    if project_id:
        query = query.filter_by(project_id=project_id)

    nl_cases = query.all()

    return jsonify({
        'success': True,
        'test_cases': [{
            'id': tc.id,
            'project_id': tc.project_id,
            'function_id': tc.function_id,
            'description': tc.description,
            'created_at': tc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'has_py_code': tc.py_test_cases.count() > 0
        } for tc in nl_cases]
    })


@test_cases.route('/nl/<int:nl_id>', methods=['GET'])
@login_required
def get_nl_detail(nl_id):
    """获取自然语言测试用例详情"""
    nl_case = NLTestCase.query.get_or_404(nl_id)

    return jsonify({
        'success': True,
        'test_case': {
            'id': nl_case.id,
            'project_id': nl_case.project_id,
            'function_id': nl_case.function_id,
            'description': nl_case.description,
            'nl_content': nl_case.nl_content,
            'created_at': nl_case.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'py_test_cases': [{
                'id': py.id,
                'file_path': py.file_path,
                'created_at': py.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for py in nl_case.py_test_cases.all()]
        }
    })


@test_cases.route('/nl/<int:nl_id>', methods=['PUT'])
@login_required
def update_nl(nl_id):
    """更新自然语言测试用例"""
    nl_case = NLTestCase.query.get_or_404(nl_id)
    data = request.get_json()

    if 'nl_content' in data:
        nl_case.nl_content = data['nl_content']
    if 'description' in data:
        nl_case.description = data['description']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '测试用例已更新'
    })


@test_cases.route('/nl/<int:nl_id>', methods=['DELETE'])
@login_required
def delete_nl(nl_id):
    """删除自然语言测试用例"""
    nl_case = NLTestCase.query.get_or_404(nl_id)
    db.session.delete(nl_case)
    db.session.commit()
    return jsonify({'success': True, 'message': '测试用例已删除'})


@test_cases.route('/py/generate', methods=['POST'])
@login_required
def generate_py():
    """根据自然语言生成 Python 测试代码"""
    data = request.get_json()

    nl_id = data.get('nl_id')
    page_object_code = data.get('page_object_code')

    if not nl_id:
        return jsonify({'success': False, 'message': '缺少自然语言用例 ID'}), 400

    nl_case = NLTestCase.query.get(nl_id)
    if not nl_case:
        return jsonify({'success': False, 'message': '自然语言用例不存在'}), 404

    # 调用 Claude 服务生成 Python 代码
    py_content = claude_service.generate_pytest_code(
        nl_case.nl_content,
        page_object_code
    )

    # 保存到数据库
    py_test_case = PyTestCase(
        nl_case_id=nl_id,
        py_content=py_content,
        file_path=f'test_{nl_case.function_id}.py'
    )
    db.session.add(py_test_case)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Python 测试代码生成成功',
        'test_case': {
            'id': py_test_case.id,
            'nl_case_id': py_test_case.nl_case_id,
            'py_content': py_content,
            'file_path': py_test_case.file_path
        }
    })


@test_cases.route('/py/<int:py_id>', methods=['GET'])
@login_required
def get_py_detail(py_id):
    """获取 Python 测试代码详情"""
    py_case = PyTestCase.query.get_or_404(py_id)

    return jsonify({
        'success': True,
        'test_case': {
            'id': py_case.id,
            'nl_case_id': py_case.nl_case_id,
            'py_content': py_case.py_content,
            'file_path': py_case.file_path,
            'created_at': py_case.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })


@test_cases.route('/py/<int:py_id>', methods=['PUT'])
@login_required
def update_py(py_id):
    """更新 Python 测试代码"""
    py_case = PyTestCase.query.get_or_404(py_id)
    data = request.get_json()

    if 'py_content' in data:
        py_case.py_content = data['py_content']
    if 'file_path' in data:
        py_case.file_path = data['file_path']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '测试代码已更新'
    })


# ==================== 结构化测试用例管理接口 ====================

@test_cases.route('/list', methods=['GET'])
@login_required
def get_structured_list():
    """获取结构化测试用例列表（分页）"""
    project_id = request.args.get('project_id', type=int)
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = StructuredTestCase.query.order_by(StructuredTestCase.created_at.desc())

    if project_id:
        query = query.filter_by(project_id=project_id)

    if search:
        # 搜索功能 ID 或场景名称
        query = query.filter(
            db.or_(
                StructuredTestCase.function_id.like(f'%{search}%'),
                StructuredTestCase.scenario.like(f'%{search}%')
            )
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'cases': [{
            'id': tc.id,
            'project_id': tc.project_id,
            'function_id': tc.function_id,
            'scenario': tc.scenario,
            'precondition': tc.precondition,
            'steps': tc.steps,
            'expected': tc.expected,
            'status': tc.status,
            'created_at': tc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': tc.updated_at.strftime('%Y-%m-%d %H:%M:%S') if tc.updated_at else None
        } for tc in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@test_cases.route('/list', methods=['POST'])
@login_required
def create_structured_case():
    """创建结构化测试用例"""
    data = request.get_json()

    project_id = data.get('project_id')
    function_id = data.get('function_id')
    scenario = data.get('scenario')
    precondition = data.get('precondition', '')
    steps = data.get('steps')
    expected = data.get('expected')
    status = data.get('status', 'draft')

    # 验证必填字段
    if not project_id or not function_id or not scenario or not steps or not expected:
        return jsonify({'success': False, 'message': '缺少必填字段'}), 400

    # 验证项目存在
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'success': False, 'message': '项目不存在'}), 404

    # 创建用例
    test_case = StructuredTestCase(
        project_id=project_id,
        function_id=function_id,
        scenario=scenario,
        precondition=precondition,
        steps=steps,
        expected=expected,
        status=status
    )
    db.session.add(test_case)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '测试用例创建成功',
        'case': {
            'id': test_case.id,
            'project_id': test_case.project_id,
            'function_id': test_case.function_id,
            'scenario': test_case.scenario,
            'precondition': test_case.precondition,
            'steps': test_case.steps,
            'expected': test_case.expected,
            'status': test_case.status,
            'created_at': test_case.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })


@test_cases.route('/list/<int:case_id>', methods=['GET'])
@login_required
def get_structured_case(case_id):
    """获取结构化测试用例详情"""
    test_case = StructuredTestCase.query.get_or_404(case_id)

    return jsonify({
        'success': True,
        'case': {
            'id': test_case.id,
            'project_id': test_case.project_id,
            'function_id': test_case.function_id,
            'scenario': test_case.scenario,
            'precondition': test_case.precondition,
            'steps': test_case.steps,
            'expected': test_case.expected,
            'status': test_case.status,
            'created_at': test_case.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': test_case.updated_at.strftime('%Y-%m-%d %H:%M:%S') if test_case.updated_at else None
        }
    })


@test_cases.route('/list/<int:case_id>', methods=['PUT'])
@login_required
def update_structured_case(case_id):
    """更新结构化测试用例"""
    test_case = StructuredTestCase.query.get_or_404(case_id)
    data = request.get_json()

    # 更新字段
    if 'function_id' in data:
        test_case.function_id = data['function_id']
    if 'scenario' in data:
        test_case.scenario = data['scenario']
    if 'precondition' in data:
        test_case.precondition = data['precondition']
    if 'steps' in data:
        test_case.steps = data['steps']
    if 'expected' in data:
        test_case.expected = data['expected']
    if 'status' in data:
        test_case.status = data['status']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '测试用例已更新',
        'case': {
            'id': test_case.id,
            'function_id': test_case.function_id,
            'scenario': test_case.scenario,
            'status': test_case.status
        }
    })


@test_cases.route('/list/<int:case_id>', methods=['DELETE'])
@login_required
def delete_structured_case(case_id):
    """删除结构化测试用例"""
    test_case = StructuredTestCase.query.get_or_404(case_id)
    db.session.delete(test_case)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '测试用例已删除'
    })


import os
