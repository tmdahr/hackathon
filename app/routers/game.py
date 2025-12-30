from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database
import random

router = APIRouter(
    prefix="/game",
    tags=["game"]
)

# 오염도에 따른 확률 가중치 계산 함수
def select_species_type_by_pollution(pollution: int, rod_level: int):
    # 기본 타입 순서: [0:쓰레기, 1:교란종, 2:일반, 3:멸종위기]
    types = [schemas.SpeciesType.TRASH, schemas.SpeciesType.INVASIVE, schemas.SpeciesType.NORMAL, schemas.SpeciesType.ENDANGERED]
    
    # 1. 오염도에 따른 기본 확률 설정 (Base Weights)
    if pollution >= 85:   # 5단계
        weights = [70, 20, 10, 0]
    elif pollution >= 60: # 4단계
        weights = [50, 30, 20, 0]
    elif pollution >= 30: # 3단계
        weights = [30, 30, 30, 10]
    elif pollution >= 10: # 2단계
        weights = [10, 25, 45, 20]
    else:                 # 1단계
        weights = [0, 10, 55, 35]

    # 2. 낚싯대 등급에 따른 확률 보정 (Modifiers)
    # weights[0]:쓰레기, [1]:교란종, [2]:일반, [3]:멸종위기
    
    if rod_level == 2:
        # 쓰레기-3, 교란종-3, 일반+5, 멸종+1
        weights[0] -= 3
        weights[1] -= 3
        weights[2] += 5
        weights[3] += 1
        
    elif rod_level >= 3:
        # 쓰레기-5, 교란종-5, 일반+7, 멸종+3
        weights[0] -= 5
        weights[1] -= 5
        weights[2] += 7
        weights[3] += 3

    # 3. 확률이 음수가 되지 않도록 보정 (0 미만이면 0으로)
    weights = [max(0, w) for w in weights]

    return random.choices(types, weights=weights, k=1)[0]


@router.post("/fish", response_model=schemas.FishResponse)
def fishing(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # [수정됨] 확률 계산 시 유저의 rod_level도 같이 전달!
    target_type = select_species_type_by_pollution(user.pollution_level, user.rod_level)

    available_species = db.query(models.Species).filter(models.Species.type == target_type.value).all()
    
    if not available_species:
        available_species = db.query(models.Species).all()

    caught_species = random.choice(available_species)

    # ... (이하 도감 업데이트 로직은 기존과 동일) ...
    collection = db.query(models.Collection).filter(
        models.Collection.user_id == user.id,
        models.Collection.species_id == caught_species.id
    ).first()

    is_new_catch = False
    if collection:
        collection.caught_count += 1
    else:
        new_collection = models.Collection(
            user_id=user.id,
            species_id=caught_species.id,
            is_new=True,
            caught_count=1
        )
        db.add(new_collection)
        is_new_catch = True
    
    db.commit()

    return schemas.FishResponse(
        species_name=caught_species.name,
        species_type=caught_species.type,
        image_url=caught_species.image_url,
        is_new=is_new_catch,
        pollution_level=user.pollution_level
    )

@router.post("/action")
def handle_action(request: schemas.UserActionRequest, db: Session = Depends(database.get_db)):
    """
    유저가 낚시 후 선택한 행동(판매, 방생, 수족관)을 처리하는 API
    """
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    species = db.query(models.Species).filter(models.Species.id == request.species_id).first()

    if not user or not species:
        raise HTTPException(status_code=404, detail="User or Species not found")

    message = ""
    money_change = 0
    pollution_change = 0

    # 행동에 따른 로직 분기
    if request.action == schemas.ActionType.SELL:
        # 1. 판매 (SELL)
        if species.type == "TRASH":
            money_change = -50  # 쓰레기 처리 비용
            pollution_change = -5 # 청소 효과
            message = "쓰레기를 치워서 바다가 깨끗해졌지만, 처리 비용이 들었습니다."
        elif species.type == "ENDANGERED":
            money_change = -5000 # 벌금
            message = "멸종위기종을 팔려다 적발되어 벌금을 물었습니다!"
        else:
            money_change = species.base_price
            message = f"{species.name}을(를) 팔아 {species.base_price}원을 벌었습니다."
            
    elif request.action == schemas.ActionType.RELEASE:
        # 2. 방생 (RELEASE)
        if species.type == "TRASH":
            pollution_change = 5 # 쓰레기 투기
            message = "쓰레기를 다시 버려서 바다가 더러워졌습니다..."
        elif species.type == "INVASIVE":
            pollution_change = 10 # 생태계 교란
            message = "교란종을 풀어주어 생태계가 위험해졌습니다."
        elif species.type == "ENDANGERED":
            pollution_change = -10 # 생태계 회복
            money_change = 1000 # 정부 보조금
            message = "멸종위기종을 보호해주어 정부 지원금을 받았습니다!"
        else:
            pollution_change = -2 # 일반 물고기 방생은 환경에 약간 좋음
            message = "물고기를 놓아주었습니다."

    elif request.action == schemas.ActionType.AQUARIUM:
        # 3. 수족관 (AQUARIUM) -> 여기선 특별한 변화 없음 (도감엔 이미 등록됨)
        message = f"{species.name}을(를) 수족관에서 기르기로 했습니다."

    # DB 업데이트
    user.money += money_change
    user.pollution_level = max(0, min(100, user.pollution_level + pollution_change)) # 0~100 사이 유지
    
    db.commit()

    return {
        "message": message,
        "current_money": user.money,
        "current_pollution": user.pollution_level
    }