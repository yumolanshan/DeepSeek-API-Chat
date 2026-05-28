# DeepSeek-API-聊天调用
使用DeepSeek API调用进行聊天

首先你要先有一个DeepSeek的API密钥。

api_key=os.environ.get('DEEPSEEK_API_KEY')：用于获取环境变量，防止 api 泄露。

Windows环境配置步骤：
- 搜索 “环境变量” —— > 环境变量 —— > 新建 —— > 输入变量名 DEEPSEEK_API_KEY ，值为 你的deepseek api密钥 
- 补：配置好环境变量后要重启编译器，加载最新的环境变量。
  
