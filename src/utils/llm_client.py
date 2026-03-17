import os
import inspect
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("LLM_MODEL", "gpt-4o")
        # 核心：存放所有已注册工具的说明书
        self.tools_schema = []

    def register_tool(self, func):
        """
        [魔法装饰器] 自动解析 Python 函数并生成 OpenAI Tool Schema
        """
        # 获取函数的文档字符串 (Description)
        description = func.__doc__.strip() if func.__doc__ else "无描述"
        
        # 获取函数参数信息
        sig = inspect.signature(func)
        properties = {}
        required = []

        for name, param in sig.parameters.items():
            # 简单的类型映射
            p_type = "string"
            if param.annotation == int: p_type = "integer"
            if param.annotation == bool: p_type = "boolean"
            
            properties[name] = {
                "type": p_type,
                "description": f"参数 {name}" # 进阶版可以解析 docstring 里的参数说明
            }
            if param.default is inspect.Parameter.empty:
                required.append(name)

        # 构建 JSON Schema
        schema = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
        
        self.tools_schema.append(schema)
        return func

    def ask(self, messages, use_tools=True):
        """
        封装对话请求
        """
        params = {
            "model": self.model,
            "messages": messages,
        }
        # 如果需要调用工具，则带上 schema
        if use_tools and self.tools_schema:
            params["tools"] = self.tools_schema
            params["tool_choice"] = "auto"

        return self.client.chat.completions.create(**params)

# 全局单例，方便其他模块调用
llm_inner = LLMClient()
# 导出装饰器，让 skills 目录下的函数可以直接用 @ai_tool
ai_tool = llm_inner.register_tool