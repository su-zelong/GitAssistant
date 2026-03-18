# 🤖 AI-Git-Assistant: 原生 AI 提交助手

这是一个基于 **AI Native** 思想构建的智能 Git 领航员。它不仅能帮你写 Commit Message，还能自主观察代码改动、扫描安全风险，并在遇到冲突时尝试自我修复。
调用相关工具处理对应指令

---

## 🌟 核心特性

* **意图驱动**：无需记忆复杂的 Git 命令，直接对话描述你的目标。
* **安全首门员**：在提交前自动调用 `security.py` 扫描 Token 和密钥，拒绝危险提交。
* **原子化技能**：所有 Git 操作被拆解为独立 **Skill**，由 AI 根据实时反馈（Feedback Loop）动态编排执行顺序。
* **自动化 Schema**：利用 `llm_client.py` 中的装饰器，实现 Python 函数到 AI 工具描述的零成本转化。

---

## 📂 项目结构

```plaintext
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
