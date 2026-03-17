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
            check=True, capture_output=True, text=True
        )
        return f"成功：已完成提交。详情：\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        # 如果没有东西可以提交，Git 会报错，我们需要把这个信息告诉 AI
        error_msg = e.stderr.decode()
        if "nothing to commit" in error_msg:
            return "提示：暂存区为空，没有需要提交的内容。"
        return f"失败：提交动作出错。错误信息：{error_msg}"

def git_push(branch_name: str = "main"):
    """
    将本地提交推送到远程仓库。
    参数:
        branch_name: 远程分支名称，默认为 main
    """
    try:
        # 尝试推送
        result = subprocess.run(
            ["git", "push", "origin", branch_name], 
            check=True, capture_output=True, text=True
        )
        return f"成功：已推送到远程分支 {branch_name}。"
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode()
        # 这里体现 AI Native 的价值：把详细报错传回给 AI
        if "rejected" in error_msg or "fetch first" in error_msg:
            return f"失败：远程版本超前，建议先执行 pull (git pull --rebase)。\n原始报错：{error_msg}"
        return f"失败：推送过程中出错。错误信息：{error_msg}"