import subprocess

def get_git_diff():
    """
    获取当前工作区（含暂存区）的所有代码改动。
    AI 将根据此内容判断修改意图并检查安全风险。
    """
    try:
        # 1. 检查当前目录是否是 Git 仓库
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"], 
            check=True, capture_output=True
        )

        # 2. 获取已暂存(staged)和未暂存(unstaged)的所有改动
        # 使用 HEAD 可以对比当前工作区与最后一次提交的区别
        cmd = ["git", "diff", "HEAD"]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        diff_text = result.stdout.strip()

        if not diff_text:
            return "提示：当前没有任何代码改动（或者改动尚未被 Git 追踪）。"

        # 3. AI Native 优化：防止 Token 爆炸
        # 如果 diff 超过 10000 字符，进行简单截断并提示 AI
        max_length = 10000
        if len(diff_text) > max_length:
            return diff_text[:max_length] + "\n\n... (内容过长，已截断) ..."

        return diff_text

    except subprocess.CalledProcessError:
        return "错误：当前目录不是一个有效的 Git 仓库，请先执行 git init。"
    except Exception as e:
        return f"执行出错：{str(e)}"