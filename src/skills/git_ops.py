import subprocess

def git_add_all():
    """将当前目录下的所有改动添加到暂存区 (git add .)"""
    try:
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        return "成功：已将所有改动添加至暂存区。"
    except subprocess.CalledProcessError as e:
        return f"失败：无法添加改动。错误信息：{e.stderr.decode()}"

def git_commit(message: str):
    """
    提交暂存区的改动。
    参数:
        message: 符合语义化的提交信息 (Commit Message)
    """
    try:
        # 执行提交
        result = subprocess.run(
            ["git", "commit", "-m", message], 
            check=True, capture_output=True, text=False
        )
        return f"成功：已完成提交。详情：\n{result.stdout.decode('utf-8', errors='replace')}"
    except subprocess.CalledProcessError as e:
        # 如果没有东西可以提交，Git 会报错，我们需要把这个信息告诉 AI
        error_msg = e.stderr.decode('utf-8', errors='replace')
        if "nothing to commit" in error_msg:
            return "提示：暂存区为空，没有需要提交的内容。"
        return f"失败：提交动作出错。错误信息：{error_msg}"

def git_push(branch_name: str = "main"):
    """
    将本地提交推送到远程仓库。
    """
    try:
        # 1. 关键修改：去掉 text=True，改为使用原始字节流 (capture_output=True)
        # 这样 subprocess 就不会尝试用默认的 GBK 去读取，也就不会报错了
        result = subprocess.run(
            ["git", "push", "origin", branch_name], 
            check=True, 
            capture_output=True,
            text=False  # 显式关闭文本模式
        )
        
        # 2. 手动安全解码
        stdout = result.stdout.decode('utf-8', errors='replace')
        return f"成功：已推送到远程分支 {branch_name}。\n{stdout}"

    except subprocess.CalledProcessError as e:
        # 3. 错误处理时的解码也必须加 errors='replace'
        # Git 的 stderr 经常包含非法字节
        error_msg = e.stderr.decode('utf-8', errors='replace')
        
        if "rejected" in error_msg or "fetch first" in error_msg:
            return f"失败：远程版本超前，请先 pull。\n详情：{error_msg}"
        return f"失败：推送过程中出错。错误信息：{error_msg}"
    
    except Exception as e:
        return f"系统级错误：{str(e)}"