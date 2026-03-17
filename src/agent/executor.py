import json
from src.skills import git_ops, security, diff_parser

class ToolExecutor:
    def __init__(self):
        # 1. 建立映射表：AI 传来的名字 -> 真实的函数对象
        self.tool_map = {
            "get_git_diff": diff_parser.get_git_diff,
            "scan_secrets": security.scan_secrets,
            "git_add_all": git_ops.git_add_all,
            "git_commit": git_ops.git_commit,
            "git_push": git_ops.git_push,
        }

    def execute(self, tool_call):
        """
        解析单条 tool_call 并执行
        """
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        
        # 2. 查找函数
        func = self.tool_map.get(func_name)
        
        if not func:
            return f"错误：找不到工具 {func_name}"

        try:
            # 3. 动态调用：Python 的 ** 语法可以将字典解包为命名参数
            print(f"执行中: {func_name}({func_args})")
            result = func(**func_args)
            return str(result)
        except Exception as e:
            return f"工具执行发生异常: {str(e)}"

    def handle_tool_calls(self, tool_calls):
        """
        批量处理多个工具调用（AI 有时会一次性要求执行多个动作）
        """
        results = []
        for call in tool_calls:
            output = self.execute(call)
            results.append({
                "tool_call_id": call.id,
                "role": "tool",
                "name": call.function.name,
                "content": output
            })
        return results