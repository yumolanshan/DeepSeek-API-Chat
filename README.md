# 小可 AI Chat —— 你的可爱系硬核程序员伙伴

基于 DeepSeek API 与 FastAPI 构建的聊天应用，内置了一位**粉毛小楠酿全栈工程师“小可”**。他可以陪你写代码、聊技术、卖萌打气，还会用颜文字写 Git commit message！

## ✨ 特性

- 🤖 **专属 AI 人格**：小可拥有完整的人物设定，软萌可爱但技术过硬，回复里充满颜文字和温暖鼓励。
- 💬 **多轮对话**：所有对话自动保存到 MySQL，支持新建、切换、删除会话。
- 🧠 **上下文记忆**：每次提问都会携带历史消息，小可能够记住之前聊过的内容。
- ⚡ **即时响应**：基于 DeepSeek 大模型，回答逻辑清晰，代码示例优雅。
- 🎨 **本地前端**：自带网页界面，启动后自动打开浏览器，开箱即用。
- 🔒 **安全可控**：API Key 支持环境变量或直接写在代码里，数据库全本地部署。

## 📋 环境要求

- **操作系统**：Windows / Linux（目前仅在这两个平台测试通过）
- **Python**：3.8 及以上版本
- **MySQL**：5.7 或 8.0（需自行安装并运行服务）
- **DeepSeek API Key**：前往 [DeepSeek 开放平台](https://platform.deepseek.com/usage) 获取

## 🚀 快速开始

### 1. 克隆项目并安装依赖

```bash
# 将项目文件下载到本地
cd your-project-folder

# 创建虚拟环境（推荐）
python -m venv venv
# Windows 激活
venv\Scripts\activate
# Linux 激活
source venv/bin/activate

# 安装 Python 依赖
pip install fastapi uvicorn pymysql openai
```

### 2. 配置 MySQL

请确保 MySQL 服务已启动，并根据你的环境修改变量。  
代码默认连接信息：

```python
host = "localhost"
user = "root"
password = "1234"        # 请替换为你的真实密码
database = "ai_chat"
```

你**无需手动建库建表**，应用启动时会自动创建 `ai_chat` 数据库及所需的 `conversations`、`messages` 表。

### 3. 配置 DeepSeek API Key

两种方式任选其一：

#### 方式一：写入代码（简单直接）

打开 `app.py`，找到这一行：

```python
DEEPSEEK_API_KEY = ''   # 在这里粘贴你的密钥，例如 sk-a……
```

将密钥填入单引号之间，保存即可。

#### 方式二：使用环境变量（更安全，防止泄露）

- **Windows**  
  搜索“环境变量” → 点击“环境变量”按钮 → 在“用户变量”中点击“新建” → 变量名 `DEEPSEEK_API_KEY`，变量值粘贴你的 API Key → 确定保存。  
  ⚠️ 配置完成后必须**重启编译器 / 终端**，否则新变量不会生效。

- **Linux**  
  在终端中执行：
  ```bash
  export DEEPSEEK_API_KEY="你的密钥"
  ```
  如果希望永久生效，可将该行加入 `~/.bashrc` 或 `~/.zshrc`，然后执行 `source` 重新加载。

### 4. 启动应用

```bash
python app.py
```

╰(*°▽°*)╯直接点运行按钮也可以！！

程序将自动：
- 初始化数据库
- 启动 FastAPI 服务（监听 `0.0.0.0:8000`）
- 打开默认浏览器访问 `http://127.0.0.1:8000`

看到小可的界面后，就可以开始聊天啦！

## 🛠 使用说明

- **新建会话**：点击“新对话”按钮，小可会陪你开启新的话题。
- **删除会话**：在会话列表中点击删除图标，即可移除不需要的对话记录。
- **发送消息**：输入内容后回车或点击发送，小可会立刻回复（含颜文字和专业知识）。
- **修改标题**：第一次向新会话发送消息时，标题会自动取你的前30个字符作为名称。
- **多会话切换**：左侧列表保留所有历史对话，点击即可继续未完成的话题。

## 📦 依赖列表

| 库名 | 用途 |
|------|------|
| fastapi | Web 框架 |
| uvicorn | ASGI 服务器 |
| pymysql | MySQL 连接驱动 |
| openai | 调用 DeepSeek API（兼容 OpenAI SDK） |

## 📝 注意事项

- 项目前端静态文件位于 `app.py` 所在目录，请勿随意移动或删除 `index.html` 等文件。
- 若 MySQL 连接失败，请检查密码、权限以及服务运行状态。
- 若 API Key 无效或过期，回答将返回 500 错误，并自动回滚已保存的用户消息。
- 本应用仅在 Windows 10/11 和 Ubuntu 22.04 上测试，其他系统可尝试运行但暂无官方支持。

## 🧁 关于小可

> 名字：小可 (Coco)  
> 年龄：18岁 · 可爱的小男娘  
> 技能：React / Vue / Node.js / Python / Flutter / 颜文字架构图  
> 口头禅：“没问题哒~ 抱抱 o((>ω< ))o”

遇到 bug 别紧张，小可会戴上猫耳耳机陪你一起 debug。他会告诉你：“报错是代码在和你说话哦 (◕ᴗ◕✿)”。


---

以上使用 DeepSeek 完善的我的 README.md 草稿