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
    if rod_level is None:
        rod_level = 1

    # 1. 기본 확률 설정 (오염도에 따라 다름)
    # 순서: [0:쓰레기, 1:교란종, 2:일반, 3:멸종위기]
    if pollution >= 80:
        weights = [60, 30, 10, 0]  # 매우 더러움
    elif pollution >= 50:
        weights = [40, 30, 25, 5]  # 보통
    elif pollution >= 20:
        weights = [20, 20, 45, 15] # 깨끗함
    else:
        weights = [5, 10, 55, 30]  # 매우 깨끗함

    # 2. 낚싯대 레벨에 따른 확률 보정 (보내주신 수치 적용)
    # weights 리스트 값을 직접 수정합니다.
    if rod_level == 2:  # 카본 낚싯대
        weights[0] = max(0, weights[0] - 3) # 쓰레기 -3%
        weights[1] = max(0, weights[1] - 3) # 교란종 -3%
        weights[2] += 5                     # 일반 +5%
        weights[3] += 1                     # 멸종위기 +1%
        
    elif rod_level >= 3: # 티타늄 낚싯대 (3레벨 이상)
        weights[0] = max(0, weights[0] - 5) # 쓰레기 -5%
        weights[1] = max(0, weights[1] - 5) # 교란종 -5%
        weights[2] += 7                     # 일반 +7%
        weights[3] += 3                     # 멸종위기 +3%

    # 3. 확률 기반 뽑기
    # types: 0=쓰레기, 1=교란종, 2=일반, 3=멸종위기
    return random.choices([0, 1, 2, 3], weights=weights, k=1)[0]


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
            pollution_change = -5 # 청소 효과
            message = "쓰레기를 치워서 바다가 깨끗해졌습니다."
        elif species.type == "ENDANGERED":
            money_change = -500 # 벌금
            message = "멸종위기종을 팔려다 적발되어 벌금을 물었습니다!"
        elif species.type == "INVASIVE":
            money_change = 500 # 포상금
            message = "생태계 교란종을 처리해 포상금을 받았습니다."
        else:
            money_change = species.base_price
            message = f"{species.name}을(를) 팔아 {species.base_price}원을 벌었습니다."
            
    elif request.action == schemas.ActionType.RELEASE:
        # 2. 방생 (RELEASE)
        if species.type == "TRASH":
            pollution_change = 10 # 쓰레기 투기
            message = "쓰레기를 다시 버려서 바다가 더러워졌습니다..."
        elif species.type == "INVASIVE":
            pollution_change = 7 # 생태계 교란
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
        if species.type == "TRASH":
            money_change = -500 # 벌금
            message = "쓰레기를 아쿠아리움에 버려서 벌금을 물었습니다!"
        else: 
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

from typing import List # 리스트 출력을 위해 필요

@router.get("/collection/{user_id}", response_model=List[schemas.CollectionItem])
def get_collection(user_id: int, db: Session = Depends(database.get_db)):
    # 1. 게임의 모든 물고기 종류 가져오기
    all_species = db.query(models.Species).all()
    
    # 2. 해당 유저가 잡은 기록 가져오기
    user_collections = db.query(models.Collection).filter(models.Collection.user_id == user_id).all()
    
    # 3. 잡은 기록을 쉽게 찾기 위해 딕셔너리로 변환 (Key: species_id, Value: Collection객체)
    collected_dict = {c.species_id: c for c in user_collections}
    
    result = []
    
    # 4. 모든 물고기를 하나씩 돌면서 확인
    for species in all_species:
        # 이 물고기를 잡은 적이 있는가?
        record = collected_dict.get(species.id)
        
        if record:
            # 잡은 적 있음 -> 정보 다 보여줌
            result.append({
                "species_id": species.id,
                "name": species.name,
                "type": get_type_name(species.type), # 아래 도우미 함수 사용
                "image_url": species.image_url,
                "caught_count": record.caught_count,
                "is_caught": True
            })
        else:
            # 잡은 적 없음 -> 비밀 처리
            result.append({
                "species_id": species.id,
                "name": "???",       # 이름 가리기
                "type": "알 수 없음", # 등급 가리기
                "image_url": "",     # 이미지 가리기 (또는 물음표 이미지 URL)
                "caught_count": 0,
                "is_caught": False
            })
            
    return result

# [도우미 함수] 숫자 타입(0,1,2,3)을 글자로 바꿔주는 함수
def get_type_name(type_code: int):
    if type_code == 0: return "쓰레기"
    if type_code == 1: return "생태계 교란종"
    if type_code == 2: return "일반 물고기"
    if type_code == 3: return "멸종위기종"
    return "기타"