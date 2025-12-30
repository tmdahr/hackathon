from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List  # 리스트 출력을 위해 필요
from .. import models, schemas, database

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# 1. 회원가입
@router.post("/", response_model=schemas.UserResponse, summary="회원가입", description="닉네임을 입력받아 새로운 사용자를 생성합니다.")
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(models.User).filter(models.User.nickname == user.nickname).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 닉네임입니다.")
    
    new_user = models.User(nickname=user.nickname)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 2. 모든 사용자 목록 보기 (랭킹 대신 변경됨)
@router.get("/list", response_model=List[schemas.UserResponse], summary="전체 유저 목록 조회", description="등록된 모든 사용자의 목록을 조회합니다.")
def get_all_users(db: Session = Depends(database.get_db)):
    # 조건(정렬) 없이 그냥 다 가져옵니다.
    users = db.query(models.User).all()
    return users

# 3. 특정 유저 정보 보기
@router.get("/{user_id}", response_model=schemas.UserResponse, summary="특정 유저 정보 조회", description="User ID를 통해 특정 사용자의 상세 정보를 조회합니다.")
def read_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user