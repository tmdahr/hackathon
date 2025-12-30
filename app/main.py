from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
# 1. 여기서 파일을 가져와야 합니다.
from .routers import game, users, shop 

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 여기서 앱에 등록(include)해야 Swagger에 뜹니다.
app.include_router(game.router)
app.include_router(users.router)
app.include_router(shop.router) 

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to Fishing Game Server"}