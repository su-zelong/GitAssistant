import os
import inspect
from openai import OpenAI
from dotenv import load_dotenv

# Azure/Github SDK 相关导入
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    SystemMessage, 
    UserMessage, 
    AssistantMessage,
    ToolMessage,
    ChatCompletionsToolDefinition,
    FunctionDefinition
)
from azure.core.credentials import AzureKeyCredential

load_dotenv()

class LLMClient:
    def __init__(self, client_type="OpenAI"):
        self.client_type = client_type
        self.model = os.getenv("LLM_MODEL", "gpt-4o")
        self.tools_schema = []  # 存储原始 dict 格式的 schema
        self.func_map = {}      # 存储函数名到函数对象的映射，方便后续执行

        if client_type == "Github":
            self.endpoint = "https://models.github.ai/inference"
            self.token = os.environ.get("GITHUB_TOKEN")
            self.client = ChatCompletionsClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.token),
            )
        else:
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            )

    def register_tool(self, func):
        """
        既是注册函数，也是装饰器。
        """
        # 1. 解析函数元数据
        name = func.__name__
        description = func.__doc__.strip() if func.__doc__ else f"执行 {name} 操作"
        
        sig = inspect.signature(func)
        properties = {}
        required = []

        for p_name, param in sig.parameters.items():
            # 类型映射
            type_map = {int: "integer", float: "number", bool: "boolean", str: "string"}
            p_type = type_map.get(param.annotation, "string")
            
            properties[p_name] = {
                "type": p_type,
                "description": f"参数 {p_name}" 
            }
            if param.default is inspect.Parameter.empty:
                required.append(p_name)

        # 2. 构建标准 JSON Schema (OpenAI 格式)
        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
        
        self.tools_schema.append(schema)
        self.func_map[name] = func # 存入映射表
        return func

    def _convert_to_azure_tools(self):
        """将 OpenAI 格式的字典转换为 Azure SDK 需要的对象"""
        azure_tools = []
        for s in self.tools_schema:
            f = s["function"]
            tool = ChatCompletionsToolDefinition(
                function=FunctionDefinition(
                    name=f["name"],
                    description=f["description"],
                    parameters=f["parameters"]
                )
            )
            azure_tools.append(tool)
        return azure_tools

    def ask(self, messages, use_tools=True):
        has_tools = use_tools and len(self.tools_schema) > 0

        if self.client_type == "Github":
            azure_messages = []
            for m in messages:
                # 关键修复点 1：如果是之前 AI 返回的对象，直接使用
                if hasattr(m, "role"):
                    # 确保 content 不为 None
                    if m.role == "assistant" and m.content is None:
                        m.content = ""
                    azure_messages.append(m)
                    continue

                # 关键修复点 2：处理 dict 格式的消息
                role = m.get("role")
                content = m.get("content") or "" # 确保 content 至少是空字符串 ""
                
                if role == "system":
                    azure_messages.append(SystemMessage(content=content))
                elif role == "user":
                    azure_messages.append(UserMessage(content=content))
                elif role == "assistant":
                    # 如果是 assistant 且有工具调用
                    azure_messages.append(AssistantMessage(
                        content=content, 
                        tool_calls=m.get("tool_calls")
                    ))
                elif role == "tool":
                    # 关键修复点 3：增加对 tool 角色反馈的支持
                    azure_messages.append(ToolMessage(
                        content=content, 
                        tool_call_id=m.get("tool_call_id")
                    ))
            
            return self.client.complete(
                messages=azure_messages,
                model=self.model,
                tools=self._convert_to_azure_tools() if has_tools else None,
                tool_choice="auto" if has_tools else None
            )
        else:
            # OpenAI 的逻辑比较宽容，通常不需要处理 None
            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools_schema if has_tools else None,
                tool_choice="auto" if has_tools else None
            )

# --- 初始化示例 ---
# 默认使用 OpenAI，如果想用 Github 传 client_type="Github"
llm_inner = LLMClient(client_type="Github") 
ai_tool = llm_inner.register_tool