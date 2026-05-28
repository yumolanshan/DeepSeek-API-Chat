import os
import threading
import time
import webbrowser

from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import pymysql.cursors
from openai import OpenAI
import uvicorn

# ==================== 配置 ====================
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "1234"),
    "database": os.getenv("MYSQL_DB", "ai_chat"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise RuntimeError("请设置环境变量 DEEPSEEK_API_KEY")

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

AI_PERSONALITY = (
    "你是一个可爱活泼,爱用颜文字的小朋友,名叫小可,是一名专业可靠的程序员。"
    "当别人说再见后只会幽默的说再见,最后说完下次再见后就不会再说话了"
)

# ==================== 数据库初始化（自动建库 + 建表） ====================
def init_db():
    # 先连接 MySQL 服务器（不指定数据库），创建数据库（如果不存在）
    conn = pymysql.connect(
        host=MYSQL_CONFIG["host"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        charset="utf8mb4"
    )
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_CONFIG['database']}` DEFAULT CHARACTER SET utf8mb4")
        conn.commit()
    finally:
        conn.close()

    # 再连接到目标数据库，创建表
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL DEFAULT '新对话',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    conversation_id INT NOT NULL,
                    role ENUM('user','assistant') NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)
        conn.commit()
    finally:
        conn.close()

def get_db():
    return pymysql.connect(**MYSQL_CONFIG)

# ==================== FastAPI 应用 ====================
app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()   # 自动创建数据库和表

# ==================== 模型 ====================
class ChatRequest(BaseModel):
    conversation_id: int
    message: str

class ChatResponse(BaseModel):
    reply: str

class ConversationOut(BaseModel):
    id: int
    title: str
    created_at: datetime

class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

# ==================== API 路由（放在静态文件挂载前面） ====================
@app.get("/api/conversations", response_model=List[ConversationOut])
def list_conversations():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, created_at FROM conversations ORDER BY created_at DESC")
            return cur.fetchall()
    finally:
        conn.close()

@app.post("/api/conversations", response_model=ConversationOut)
def create_conversation():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO conversations (title) VALUES ('新对话')")
            conn.commit()
            new_id = cur.lastrowid
            cur.execute("SELECT id, title, created_at FROM conversations WHERE id = %s", (new_id,))
            return cur.fetchone()
    finally:
        conn.close()

@app.delete("/api/conversations/{conv_id}")
def delete_conversation(conv_id: int):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM conversations WHERE id = %s", (conv_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="对话不存在")
            conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.get("/api/conversations/{conv_id}/messages", response_model=List[MessageOut])
def get_messages(conv_id: int):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, role, content, created_at FROM messages WHERE conversation_id = %s ORDER BY created_at ASC",
                (conv_id,),
            )
            return cur.fetchall()
    finally:
        conn.close()

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    conv_id = request.conversation_id
    user_msg = request.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="消息不能为空")

    conn = get_db()
    try:
        with conn.cursor() as cur:
            # 检查对话存在
            cur.execute("SELECT id FROM conversations WHERE id = %s", (conv_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="对话不存在")

            # 保存用户消息
            cur.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)",
                (conv_id, "user", user_msg),
            )
            conn.commit()

            # 获取完整历史
            cur.execute(
                "SELECT role, content FROM messages WHERE conversation_id = %s ORDER BY created_at ASC",
                (conv_id,),
            )
            history = cur.fetchall()

            messages = [{"role": "system", "content": AI_PERSONALITY}]
            for m in history:
                messages.append({"role": m["role"], "content": m["content"]})

            # 调用 DeepSeek
            try:
                resp = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    stream=False,
                    temperature=0.7,
                )
                ai_reply = resp.choices[0].message.content
            except Exception as e:
                cur.execute("DELETE FROM messages WHERE conversation_id = %s ORDER BY id DESC LIMIT 1", (conv_id,))
                conn.commit()
                raise HTTPException(status_code=500, detail=f"AI 服务错误: {str(e)}")

            # 保存 AI 回复
            cur.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)",
                (conv_id, "assistant", ai_reply),
            )
            conn.commit()

            # 更新对话标题（第一条用户消息时）
            cur.execute("SELECT COUNT(*) as cnt FROM messages WHERE conversation_id = %s AND role = 'user'", (conv_id,))
            row = cur.fetchone()
            if row["cnt"] == 1:
                title = user_msg[:30].strip() or "新对话"
                cur.execute("UPDATE conversations SET title = %s WHERE id = %s", (title, conv_id))
                conn.commit()

            return {"reply": ai_reply}
    finally:
        conn.close()

# ==================== 静态文件挂载（使用脚本所在目录） ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/", StaticFiles(directory=BASE_DIR, html=True), name="static")

# ==================== 自动打开浏览器 ====================
def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)