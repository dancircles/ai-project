import os
import requests
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel

app = FastAPI(title="AI 问答接口",description="调 DeepSeek 回答问题的接口")

api_key = os.environ.get("DEEPSEEK_API_KEY")

class Question(BaseModel):
    text:str

@app.get("/")
def home():
    return{"message":"AI 问答接口已启动"}

@app.post("/ask")
def ask(q: Question):
    if not api_key:
        raise HTTPException(status_code=500,detail="服务器未配置密钥")

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model":"deepseek-chat",
        "messages":[
            {"role":"user","content": q.text}
        ]
    }

    try:
        response = requests.post(url,headers=headers,json=data)

        print("DeepSeek 状态码:", response.status_code)  
        print("DeepSeek 返回:", response.text)             

        if response.status_code == 401:
            raise HTTPException(status_code = 401,detail="密钥无效")
        elif response.status_code == 402:
            raise HTTPException(status_code=402,detail="余额不足")
        elif response.status_code != 200:
            raise HTTPException(status_code=502,detail="模型服务出错")

        answer = response.json()["choices"][0]["message"]["content"]
        return {"answer":answer}

    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503,detail="网络错误，稍后再试")