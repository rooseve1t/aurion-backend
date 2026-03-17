from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Aurion OS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

users_db = {}

class RegisterData(BaseModel):
    email: str
    username: str
    password: str

class LoginData(BaseModel):
    email: str
    password: str

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/api/v1/auth/register")
async def register(data: RegisterData):
    users_db[data.email] = {"email": data.email, "username": data.username}
    return {"access_token": f"token_{data.email}", "refresh_token": "refresh", "token_type": "bearer"}

@app.post("/api/v1/auth/token")
async def login(data: LoginData):
    return {"access_token": f"token_{data.email}", "refresh_token": "refresh", "token_type": "bearer"}

@app.get("/api/v1/auth/me")
async def me():
    return {"id": 1, "email": "demo@aurionai.ru", "username": "demo", "is_active": True}
