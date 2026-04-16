"""项目管理路由"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import Project, NLTestCase, PyTestCase, TestResult
from extensions import db
from utils.git_helper import clone_repository, get_file_tree, read_source_files

projects = Blueprint('projects', __name__, url_prefix='/api/projects')


@projects.route('', methods=['GET'])
@login_required
def get_projects():
    """获取所有项目"""
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return jsonify({
        'success': True,
        'projects': [{
            'id': p.id,
            'name': p.name,
            'source_path': p.source_path,
            'source_type': p.source_type,
            'git_url': p.git_url,
            'created_at': p.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for p in projects]
    })


@projects.route('', methods=['POST'])
@login_required
def create_project():
    """创建项目"""
    data = request.get_json()

    name = data.get('name')
    source_type = data.get('source_type', 'local')
    source_path = data.get('source_path')
    git_url = data.get('git_url')

    if not name:
        return jsonify({'success': False, 'message': '项目名称不能为空'}), 400

    # 如果是 Git 类型，需要克隆仓库
    if source_type == 'git' and git_url:
        from config import Config
        target_path = os.path.join(Config.PROJECTS_FOLDER, name)
        result = clone_repository(git_url, target_path)
        if not result['success']:
            return jsonify({'success': False, 'message': result['error']}), 400
        source_path = target_path

    project = Project(
        name=name,
        source_type=source_type,
        source_path=source_path,
        git_url=git_url
    )
    db.session.add(project)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '项目创建成功',
        'project': {
            'id': project.id,
            'name': project.name
        }
    })


@projects.route('/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """删除项目"""
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'success': True, 'message': '项目已删除'})


@projects.route('/<int:project_id>/files', methods=['GET'])
@login_required
def get_project_files(project_id):
    """获取项目文件树"""
    project = Project.query.get_or_404(project_id)

    if not project.source_path or not os.path.exists(project.source_path):
        return jsonify({'success': False, 'message': '源码路径不存在'}), 404

    files = get_file_tree(project.source_path)
    return jsonify({
        'success': True,
        'files': files
    })


@projects.route('/<int:project_id>/files/content', methods=['POST'])
@login_required
def get_file_content(project_id):
    """获取指定文件内容"""
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    file_path = data.get('file_path')

    if not file_path:
        return jsonify({'success': False, 'message': '文件路径不能为空'}), 400

    full_path = os.path.join(project.source_path, file_path)

    if not os.path.exists(full_path):
        return jsonify({'success': False, 'message': '文件不存在'}), 404

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({
            'success': True,
            'content': content,
            'file_path': file_path
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# 需要导入 os 模块
import os
