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
        return existing_user
    
    new_user = models.User(nickname=user.nickname)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 실제 서식지 목록 가져오기
    habitats = db.query(models.Species.habitat).distinct().all()
    # '쓰레기' 서식지는 오염도 관리 대상에서 제외
    habitat_names = [h[0] for h in habitats if h[0] and h[0] != "쓰레기"]

    for h_name in habitat_names:
        new_hp = models.HabitatPollution(
            user_id=new_user.id,
            habitat_name=h_name,
            pollution_level=80 # 기본값
        )
        db.add(new_hp)
    
    # 기본 낚싯대(ID 0) 기본 지급
    initial_inventory = models.Inventory(user_id=new_user.id, item_id=0)
    db.add(initial_inventory)
    
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
    
    # 아쿠아리움 목록을 AquariumItem 형식으로 변환
    fish_list = []
    for item in user.aquarium:
        fish_list.append(schemas.AquariumItem(
            id=item.id,
            species_id=item.species_id,
            name=item.species.name,
            image_url=item.species.image_url,
            caught_at=item.caught_at
        ))

    # 편지 목록을 FishLetterSchema 형식으로 변환
    received_letter_list = []
    for letter in user.letters:
        received_letter_list.append(schemas.FishLetterSchema(
            id=letter.id,
            species_id=letter.species_id,
            species_name=letter.species.name,
            content=letter.content,
            is_read=letter.is_read,
            created_at=letter.created_at
        ))
    
    # Pydantic 모델에 맞게 데이터 구성
    user_data = schemas.UserResponse.from_orm(user)
    user_data.aquarium_list = fish_list
    user_data.letter_list = received_letter_list
    
    return user_data