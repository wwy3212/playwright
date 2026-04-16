"""Git 辅助工具"""
import subprocess
import os


def clone_repository(git_url, target_path):
    """克隆 Git 仓库到指定路径"""
    try:
        # 确保目标目录的父目录存在
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        result = subprocess.run(
            ['git', 'clone', git_url, target_path],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            return {
                'success': False,
                'error': result.stderr or '克隆失败'
            }

        return {
            'success': True,
            'message': '仓库克隆成功',
            'path': target_path
        }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': '克隆操作超时（超过 5 分钟）'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def read_source_files(source_path, extensions=None):
    """读取源代码文件内容"""
    if extensions is None:
        extensions = ['.py', '.js', '.ts', '.vue', '.jsx', '.tsx', '.java', '.go']

    files_content = {}

    if not os.path.exists(source_path):
        return files_content

    for root, dirs, files in os.walk(source_path):
        # 跳过隐藏目录和常见不需要目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'dist', 'build']]

        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        files_content[file_path] = f.read()
                except:
                    pass

    return files_content


def get_file_tree(source_path):
    """获取源代码目录树结构"""
    tree = []

    if not os.path.exists(source_path):
        return tree

    for root, dirs, files in os.walk(source_path):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'dist', 'build']]

        rel_root = os.path.relpath(root, source_path)

        for file in files:
            rel_path = os.path.join(rel_root, file) if rel_root != '.' else file
            tree.append(rel_path)

    return sorted(tree)
