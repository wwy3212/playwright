"""测试执行和报告路由"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import PyTestCase, TestResult
from extensions import db
from services import test_runner

execution = Blueprint('execution', __name__, url_prefix='/api/execution')


@execution.route('/run/<int:test_case_id>', methods=['POST'])
@login_required
def run_test(test_case_id):
    """执行单个测试用例"""
    data = request.get_json() or {}

    # 可选：使用自定义测试内容
    test_content = data.get('test_content')

    # 获取测试用例
    py_case = PyTestCase.query.get(test_case_id)
    if not py_case:
        return jsonify({'success': False, 'message': '测试用例不存在'}), 404

    # 执行测试
    result = test_runner.run_test(test_case_id, test_content)

    if result.get('status') == 'error':
        return jsonify({
            'success': False,
            'message': result.get('message', '执行失败'),
            'result': result
        }), 500

    return jsonify({
        'success': True,
        'message': '测试执行完成',
        'result': {
            'id': result.get('result_id'),
            'status': result.get('status'),
            'duration': result.get('duration'),
            'stdout': result.get('stdout'),
            'stderr': result.get('stderr')
        }
    })


@execution.route('/run-all', methods=['POST'])
@login_required
def run_all_tests():
    """执行所有测试"""
    project_id = request.get_json().get('project_id') if request.get_json() else None

    results = test_runner.run_all_tests(project_id)

    passed = sum(1 for r in results if r.get('status') == 'passed')
    failed = sum(1 for r in results if r.get('status') == 'failed')

    return jsonify({
        'success': True,
        'message': f'测试执行完成：{passed} 通过，{failed} 失败',
        'results': results,
        'summary': {
            'total': len(results),
            'passed': passed,
            'failed': failed
        }
    })


@execution.route('/results', methods=['GET'])
@login_required
def get_results():
    """获取测试结果列表"""
    test_case_id = request.args.get('test_case_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = TestResult.query.order_by(TestResult.executed_at.desc())

    if test_case_id:
        query = query.filter_by(test_case_id=test_case_id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'results': [{
            'id': r.id,
            'test_case_id': r.test_case_id,
            'status': r.status,
            'error_message': r.error_message,
            'duration': r.duration,
            'executed_at': r.executed_at.strftime('%Y-%m-%d %H:%M:%S')
        } for r in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@execution.route('/results/<int:result_id>', methods=['GET'])
@login_required
def get_result_detail(result_id):
    """获取测试结果详情"""
    result = TestResult.query.get_or_404(result_id)

    return jsonify({
        'success': True,
        'result': {
            'id': result.id,
            'test_case_id': result.test_case_id,
            'status': result.status,
            'error_message': result.error_message,
            'duration': result.duration,
            'output_log': result.output_log,
            'executed_at': result.executed_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })


@execution.route('/results', methods=['DELETE'])
@login_required
def clear_results():
    """清空测试结果"""
    TestResult.query.delete()
    db.session.commit()
    return jsonify({'success': True, 'message': '测试结果已清空'})
