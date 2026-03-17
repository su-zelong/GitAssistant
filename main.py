import os
import json
from dotenv import load_dotenv
from openai import OpenAI  # 或者是你常用的 LLM SDK
from src.skills import git_ops, security, diff_parser  # 导入你的工具函数

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. 定义工具清单 (给 AI 看的说明书)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_git_diff",
            "description": "获取当前本地代码的所有改动内容(diff)",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scan_secrets",
            "description": "检查代码改动中是否包含敏感 Token 或密码",
            "parameters": {
                "type": "object", 
                "properties": {"diff_content": {"type": "string"}},
                "required": ["diff_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit_and_push",
            "description": "执行 git add, commit 和 push 操作",
            "parameters": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"]
            }
        }
    }
]

def main():
    print("🤖 AI Git 助手已就绪...")
    user_input = input("您想做什么？(例如：帮我检查并提交代码): ")

    # 初始上下文
    messages = [
        {"role": "system", "content": "你是一个严谨的 Git 助手。提交前必须先看 diff 并检查安全隐患。"},
        {"role": "user", "content": user_input}
    ]

    # --- 核心循环 (The Agent Loop) ---
    while True:
        # A. 让 AI 思考下一步
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        messages.append(response_message)

        # B. 判断 AI 是否要调用工具
        if not response_message.tool_calls:
            # 如果 AI 不调工具了，说明它话说明白了，任务结束
            print(f"\nAI: {response_message.content}")
            break

        # C. 执行 AI 请求的工具 (The Acting)
        for tool_call in response_message.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            print(f"🛠️  AI 正在调用工具: {func_name}...")
            
            # 这里的映射可以写得更优雅，这里为了演示直观
            if func_name == "get_git_diff":
                result = diff_parser.get_git_diff()
            elif func_name == "scan_secrets":
                result = security.scan_secrets(args['diff_content'])
            elif func_name == "git_commit_and_push":
                result = git_ops.git_commit_and_push(args['message'])
            
            # D. 把工具结果反馈给 AI
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": func_name,
                "content": str(result)
            })
            
    print("\n✅ 任务处理完毕。")

if __name__ == "__main__":
    main()