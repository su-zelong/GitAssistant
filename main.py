import os
import json
from dotenv import load_dotenv
from src.utils.llm_client import LLMClient
from src.agent.executor import ToolExecutor  # 导入执行器
from src.agent.planner import get_planner_config  # 导入规划器配置

load_dotenv()

def main():
    # 1. 初始化大脑 (LLM) 和 手 (Executor)
    client_type = os.getenv("CLIENT_TYPE", "Github")
    llm_client = LLMClient(client_type=client_type)
    executor = ToolExecutor() # 内部已经映射好了函数

    # 2. 注册工具到 LLM 助手（让 AI 知道有哪些工具可用）
    # 我们可以直接遍历 executor 的 map 来注册，避免重复写代码
    for func in executor.tool_map.values():
        llm_client.register_tool(func)

    # --- 核心循环 (增强版：支持干预) ---
    while True:
        print("🤖 AI Git 助手已就绪...")
        user_input = input("User: ")
        # 每次让用户输入都增加提示词模板
        messages = [
            get_planner_config(), # 加载prompt
            {"role": "user", "content": user_input}
        ]
        if user_input.lower() in ["exit", "quit", "退出"]:
            break

        messages.append({"role": "user", "content": user_input})

        while True:
            response = llm_client.ask(messages)
            response_message = response.choices[0].message
            messages.append(response_message)

            # ai没有工具调用，此时跳出当前循环，等待用户下一步输入
            if not getattr(response_message, "tool_calls", None):
                print(f"\nAI: {response_message.content}")
                break

            # 2. 处理工具调用
            for tool_call in response_message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                # --- 🚀 关键：人工干预逻辑 ---
                # 定义哪些工具需要用户“点头”
                risky_tools = ["git_push", "git_commit", "git_add_all"]
                
                if func_name in risky_tools:
                    print(f"\n⚠️  AI 计划执行高风险操作: {func_name}")
                    print(f"   参数: {args}")
                    confirm = input("👉 是否允许执行？(y/n/或输入修改意见): ").lower()

                    if confirm == 'n':
                        # 给 AI 一个“拒绝”的反馈，让它重新规划
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": func_name,
                            "content": "用户拒绝了该操作，请停止执行或询问用户接下来的打算。"
                        })
                        continue # 跳过本次执行
                    elif confirm != 'y':
                        # 如果用户输入了具体意见（例如：换个分支推送）
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": func_name,
                            "content": f"用户取消了操作并给出反馈：'{confirm}'。请根据反馈调整计划。"
                        })
                        continue

                # --- 执行允许的工具 ---
                # 等于y 代表用户同意直接执行
                print(f"⚙️  正在执行: {func_name}...")
                output = executor.execute(tool_call) # 使用你的 ToolExecutor
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": func_name,
                    "content": output
                })

            # 继续下一轮“思考”，AI 会根据工具结果或你的拒绝反馈来决定下一句话

        print("\n✅ 任务处理完毕。")

if __name__ == "__main__":
    main()