🤖 AI-Git-Assistant: 原生 AI 提交助手
这是一个基于 AI Native 思想构建的智能 Git 领航员。它不仅能帮你写 Commit Message，还能自主观察代码改动、扫描安全风险、并在遇到冲突时尝试自我修复。

🌟 核心特性
意图驱动：无需记忆复杂的 Git 命令，直接对话描述你的目标。

安全首门员：在提交前自动调用 security.py 扫描 Token 和密钥，拒绝危险提交。

原子化技能：所有 Git 操作被拆解为独立 Skill，由 AI 根据实时反馈（Feedback Loop）动态编排执行顺序。

自动化 Schema：利用 llm_client.py 中的装饰器，实现 Python 函数到 AI 工具描述的零成本转化。

📂 项目结构
Plaintext
AI-Git-Assistant/
├── main.py                 # 🚀 启动入口：Agent 运行循环
├── .env                    # 🔑 环境变量：存放你的 API Key
├── src/
│   ├── agent/
│   │   ├── planner.py      # 🧠 大脑：存放系统提示词 (SOP)
│   │   └── executor.py     # ⚙️ 传动：工具分发与执行逻辑
│   ├── skills/
│   │   ├── git_ops.py      # 🛠️ 手脚：Git 原子操作
│   │   ├── security.py     # 🛡️ 护盾：安全扫描逻辑
│   │   └── diff_parser.py  # 👁️ 眼睛：代码改动解析
│   └── utils/
│       └── llm_client.py   # 💓 心脏：模型连接与 @ai_tool 装饰器
└── requirements.txt
🛠️ 快速开始
1. 环境准备
确保你的机器安装了 Python 3.8+ 和 Git。

Bash
# 克隆你刚才创建的项目（假设你已经推送到本地文件夹）
cd AI-Git-Assistant

# 安装依赖
pip install openai python-dotenv
2. 配置环境变量
在项目根目录新建 .env 文件：

代码段
OPENAI_API_KEY=你的API密匙
OPENAI_BASE_URL=https://api.openai.com/v1  # 如果使用代理或国内模型请修改此处
LLM_MODEL=gpt-4o                            # 推荐使用具备强推理能力的模型
3. 运行助手
在你想要提交代码的 Git 仓库目录下运行：

Bash
python main.py
🎮 使用示例
场景 A：常规提交

用户: "帮我把刚才改的逻辑处理下。"
AI 行为:

调用 get_git_diff 看到你改了 parser.py。

调用 scan_secrets 确认没有泄露。

自动生成消息 "refactor: optimize document parsing logic"。

连续调用 git_add_all 和 git_commit。

场景 B：安全拦截

用户: "直接帮我 push 到远程。"
AI 行为:

扫描 diff 发现你新加了一行 HF_TOKEN = "hf_..."。

停止执行 git_push。

回复："⚠️ 抱歉，我在代码中发现了敏感 Token，为了安全已拦截提交流程，请处理后重试。"

🧠 开发新功能 (AI Native 范式)
如果你想让助手学会“自动生成文档”，你只需要：

在 src/skills/ 下新建函数。

加上 @ai_tool 装饰器。

Python
@ai_tool
def generate_readme_doc(content: str):
    """根据代码逻辑自动生成或更新 README 文档"""
    # 你的逻辑...
    return "README 已更新"
无需修改 main.py 或 executor.py，Agent 再次启动时会自动获得这项新技能！
