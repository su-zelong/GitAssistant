import re

def scan_secrets(diff_content: str):
    """
    对代码改动内容进行安全扫描。
    检查是否存在 API Keys、Tokens 或硬编码的密码。
    返回: 安全报告字符串。
    """
    # 1. 定义敏感信息匹配规则 (Regex)
    rules = {
        "HuggingFace Token": r"hf_[a-zA-Z0-9]{34}",
        "OpenAI API Key": r"sk-[a-zA-Z0-9]{48}",
        "GitHub Token": r"(ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36}",
        "Generic Secret/Password": r"(password|passwd|secret|api_key|token)\s*[:=]\s*['\"]([^'\"]+)['\"]"
    }

    findings = []

    # 2. 逐行扫描 Diff 内容
    lines = diff_content.split('\n')
    for line_no, line in enumerate(lines):
        # 只检查新增的行 (以 + 开头的行)
        if not line.startswith('+'):
            continue
            
        for name, pattern in rules.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                # 提取匹配到的敏感片段（脱敏处理后显示给 AI）
                secret_guess = match.group(0)
                masked_secret = secret_guess[:6] + "..." + secret_guess[-4:]
                findings.append(f"第 {line_no} 行发现疑似 {name}: `{masked_secret}`")

    # 3. 给出扫描结论
    if not findings:
        return "✅ 安全检查通过：未在改动中发现明显的敏感信息泄露。"
    
    report = "⚠️ 安全警告！在提交内容中发现以下潜在风险：\n" + "\n".join(findings)
    report += "\n\n请删除上述敏感信息，或将其放入 .env 文件后再尝试提交。"
    return report