"""需求文件管理路由"""
import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import Requirement, Project

requirements = Blueprint('requirements', __name__, url_prefix='/api/requirements')

# 允许的文件类型
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'md', 'ppt', 'pptx'}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_size(file):
    """获取文件大小"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size


@requirements.route('', methods=['GET'])
@login_required
def get_requirements():
    """获取项目的需求文件列表"""
    project_id = request.args.get('project_id', type=int)

    query = Requirement.query.order_by(Requirement.uploaded_at.desc())

    if project_id:
        query = query.filter_by(project_id=project_id)

    reqs = query.all()

    return jsonify({
        'success': True,
        'requirements': [{
            'id': r.id,
            'project_id': r.project_id,
            'project_name': r.project.name if r.project else '',
            'filename': r.filename,
            'file_size': r.file_size,
            'file_type': r.file_type,
            'uploader': r.uploader.username if r.uploader else '未知',
            'uploaded_at': r.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if r.uploaded_at else '',
            'updated_at': r.updated_at.strftime('%Y-%m-%d %H:%M:%S') if r.updated_at else ''
        } for r in reqs]
    })


@requirements.route('/upload', methods=['POST'])
@login_required
def upload_requirement():
    """上传需求文件"""
    project_id = request.form.get('project_id', type=int)
    file = request.files.get('file')

    if not project_id:
        return jsonify({'success': False, 'message': '请选择项目'}), 400

    if not file:
        return jsonify({'success': False, 'message': '请选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': '不支持的文件类型'}), 400

    # 检查项目是否存在
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'success': False, 'message': '项目不存在'}), 404

    # 安全文件名
    original_filename = secure_filename(file.filename) if file.filename else 'unknown'
    ext = original_filename.rsplit('.', 1)[1] if '.' in original_filename else ''
    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    # 保存文件
    upload_folder = current_app.config.get('REQUIREMENTS_FOLDER') or ''
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)

    # 获取文件信息
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    file_type = ext.lower()

    # 保存到数据库
    req = Requirement(
        project_id=project_id,
        filename=original_filename,
        file_path=unique_filename,
        file_size=file_size,
        file_type=file_type,
        uploader_id=current_user.id
    )
    db.session.add(req)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '文件上传成功',
        'requirement': {
            'id': req.id,
            'filename': req.filename,
            'file_size': req.file_size,
            'file_type': req.file_type,
            'uploader': current_user.username,
            'uploaded_at': req.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })


@requirements.route('/<int:req_id>/download', methods=['GET'])
@login_required
def download_requirement(req_id):
    """下载需求文件"""
    req = Requirement.query.get_or_404(req_id)

    upload_folder = current_app.config.get('REQUIREMENTS_FOLDER') or ''
    file_path = os.path.join(upload_folder, req.file_path)

    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': '文件不存在'}), 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=req.filename
    )


@requirements.route('/<int:req_id>', methods=['PUT'])
@login_required
def update_requirement(req_id):
    """更新需求文件（元数据或替换文件）"""
    req = Requirement.query.get_or_404(req_id)

    # 处理文件替换
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            # 删除旧文件
            upload_folder = current_app.config.get('REQUIREMENTS_FOLDER') or ''
            old_path = os.path.join(upload_folder, req.file_path)
            if os.path.exists(old_path):
                os.remove(old_path)

            # 保存新文件
            original_filename = secure_filename(file.filename) if file.filename else 'unknown'
            ext = original_filename.rsplit('.', 1)[1] if '.' in original_filename else ''
            unique_filename = f"{uuid.uuid4().hex}.{ext}"

            upload_folder = current_app.config.get('REQUIREMENTS_FOLDER') or ''
            new_path = os.path.join(upload_folder, unique_filename)
            file.save(new_path)

            req.filename = original_filename
            req.file_path = unique_filename
            req.file_size = get_file_size(file) if hasattr(file, 'seek') else os.path.getsize(new_path)
            req.file_type = ext.lower()

    # 处理项目变更
    if 'project_id' in request.form:
        new_project_id = request.form.get('project_id', type=int)
        if new_project_id and Project.query.get(new_project_id):
            req.project_id = new_project_id

    req.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '文件更新成功'
    })


@requirements.route('/<int:req_id>', methods=['DELETE'])
@login_required
def delete_requirement(req_id):
    """删除需求文件"""
    req = Requirement.query.get_or_404(req_id)

    # 删除物理文件
    upload_folder = current_app.config.get('REQUIREMENTS_FOLDER') or ''
    file_path = os.path.join(upload_folder, req.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    # 删除数据库记录
    db.session.delete(req)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '文件已删除'
    })
