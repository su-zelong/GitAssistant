import os
import json
import inspect
from dotenv import load_dotenv
from src.skills import git_ops, security, diff_parser 
from src.utils.llm_client import LLMClient

load_dotenv()

# 配置切换：如果是 "Github" 会走 Azure SDK，否则走 OpenAI SDK
CLIENT_TYPE = "Github" 

def main():
    # 1. 初始化客户端
    llm_client = LLMClient(client_type=CLIENT_TYPE)
    
    # 2. 自动化注册工具 (不再需要手写 TOOLS 字典)
    # 只要你的函数写了 docstring，register_tool 就会自动生成说明书
    modules = [git_ops, security, diff_parser]
    for module in modules:
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith("_"):  # 过滤私有函数
                print(f"🔧 注册工具: {name}")
                llm_client.register_tool(func)

    print("\n🤖 AI Git 助手已就绪...")
    user_input = input("您想做什么？(例如：帮我检查并提交代码): ")

    # 3. 初始上下文
    messages = [
        {"role": "system", "content": "你是一个严谨的 Git 助手。提交前必须先看 diff 并检查安全隐患。"},
        {"role": "user", "content": user_input}
    ]

    # --- 核心循环 (The Agent Loop) ---
    while True:
        # A. 让 AI 思考下一步
        response = llm_client.ask(messages)
        
        # 统一处理 Github/OpenAI 的响应结构
        if CLIENT_TYPE == "Github":
            # Github SDK 返回的是对象，需要提取 message
            response_message = response.choices[0].message
            # 为了后续保持 messages 数组一致性，转为 dict 或保持对象
            # 建议将 response_message 存入，后面根据 SDK 要求处理
        else:
            response_message = response.choices[0].message

        # 将 AI 的回复加入对话历史
        messages.append(response_message)

        # B. 判断 AI 是否要调用工具
        if not response_message.tool_calls:
            print(f"\nAI: {response_message.content}")
            break

        # C. 执行 AI 请求的工具 (The Acting)
        for tool_call in response_message.tool_calls:
            func_name = tool_call.function.name
            # 解析参数
            args = json.loads(tool_call.function.arguments)
            
            print(f"🛠️  AI 正在调用工具: {func_name}({args})...")
            
            # 【关键改进】：直接从 llm_client 的映射表中查找并运行函数
            if func_name in llm_client.func_map:
                try:
                    target_func = llm_client.func_map[func_name]
                    # 自动将解包后的参数传给函数
                    result = target_func(**args)
                except Exception as e:
                    result = f"Error executing tool: {str(e)}"
            else:
                result = "Error: Tool not found."

            # D. 把工具结果反馈给 AI
            # 注意：Github/Azure 模式下 role 需匹配其 ToolMessage 逻辑
            # 这里统一使用标准格式，LLMClient 内部会处理转换
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": func_name,
                "content": str(result)
            })
            
    print("\n✅ 任务处理完毕。")

if __name__ == "__main__":
    main()