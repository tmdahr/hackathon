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
    # 순서: [0:쓰레기, 1:일반, 2:멸종위기] (번호 변경됨)
    if pollution >= 80:
        # 매우 더러움
        weights = [70, 30, 0] 
    elif pollution >= 60:
        # 보통
        weights = [60, 45, 5]
    elif pollution >= 40:
        # 깨끗함
        weights = [20, 65, 15]
    else:
        # 매우 깨끗함
        weights = [5, 65, 25]

    # 2. 낚싯대 레벨에 따른 확률 보정
    if rod_level == 2:  # 카본 낚싯대
        weights[0] = max(0, weights[0] - 5) # 쓰레기 -5%
        weights[1] += 4                     # 일반 +4% (Index 1 is Normal)
        weights[2] += 1                     # 멸종위기 +1% (Index 2 is Endangered)
        # 잔여 확률 보정 생략
        
    elif rod_level >= 3: # 티타늄 낚싯대 (3레벨 이상)
        weights[0] = max(0, weights[0] - 10) # 쓰레기 -10%
        weights[1] += 7                     # 일반 +7%
        weights[2] += 3                     # 멸종위기 +3%

    # 3. 확률 기반 뽑기
    # types: 0=쓰레기, 1=일반, 2=멸종위기
    return random.choices([0, 1, 2], weights=weights, k=1)[0]


@router.post("/fish", response_model=schemas.FishResponse, summary="낚시하기", description="""
서식지(Habitat)에서 낚시를 진행합니다.
- **확률**: 오염도와 낚싯대 등급에 따라 쓰레기/일반/멸종위기종 확률이 결정됩니다.
- **로직**: 서식지에 맞는 물고기를 랜덤하게 낚습니다. 만약 해당 등급 물고기가 없으면 일반 물고기로 대체됩니다.
- **결과**: 잡은 물고기 정보와 도감 등록 여부, 유저의 상태 변화를 반환합니다.
""")
def fishing(user_id: int, habitat: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 1. 어떤 등급의 물고기가 잡힐지 결정 (이제 여기서 숫자 0,1,2가 나옵니다)
    target_type = select_species_type_by_pollution(user.pollution_level, user.rod_level)
    
    # [수정된 부분] target_type.value -> target_type 으로 변경!
    # habitat 필터 추가
    # 단, 쓰레기(type=0)는 서식지 상관없이 낚여야 함 & 낚싯대 레벨에 따른 정화가 필요할 수도 있음(기획 필요, 일단 유지)
    
    query = db.query(models.Species)
    
    if target_type == 0:
        # 쓰레기는 서식지 무관하게 모든 쓰레기 중 랜덤
        query = query.filter(models.Species.type == 0)
    else:
        # 그 외 물고기는 서식지와 등급 일치 필요
        query = query.filter(
            models.Species.type == target_type,
            models.Species.habitat == habitat
        )
        
    available_species = query.all()
    
    # [수정된 부분] 꽝 방지 로직 (Fallback)
    # 만약 해당 등급 물고기가 없는데, 타겟이 '일반(1)'이 아니라면 일반 물고기로 재시도
    if not available_species and target_type != 1 and target_type != 0:
        print(f"Fallback: No species found for type {target_type} in {habitat}. Trying Normal(1)...")
        available_species = db.query(models.Species).filter(
            models.Species.type == 1,
            models.Species.habitat == habitat
        ).all()

    if not available_species:
        return {"message": "아무것도 잡히지 않았습니다... (해당 서식지에 물고기가 없음)"}
    
    # 2. 해당 등급 내에서 랜덤으로 하나 선택
    caught_fish = random.choice(available_species)
    
    # 3. 도감(Collection)에 저장
    collection = db.query(models.Collection).filter(
        models.Collection.user_id == user.id,
        models.Collection.species_id == caught_fish.id
    ).first()
    
    is_new = False
    if not collection:
        collection = models.Collection(user_id=user.id, species_id=caught_fish.id, caught_count=1)
        db.add(collection)
        is_new = True
    else:
        collection.caught_count += 1
        collection.is_new = False # 이미 잡은 적 있으니 False
    
    # 4. 보상 지급 (돈, 오염도 변화) 및 저장
    user.money += caught_fish.price
    
    # 오염도 변화 (쓰레기 잡으면 청소됨, 아니면 그대로)
    if caught_fish.type == 0: # 쓰레기
        user.pollution_level = max(0, user.pollution_level - 5)
    
    db.commit()
    
    return {
        "message": f"낚시 성공! {caught_fish.name}을(를) 잡았습니다.",
        "fish": {
            "name": caught_fish.name,
            "type": caught_fish.type, # 0:쓰레기, 1:교란종, 2:일반, 3:멸종위기
            "price": caught_fish.price,
            "image_url": caught_fish.image_url,
            "habitat": caught_fish.habitat
        },
        "is_new": is_new,
        "user_status": {
            "money": user.money,
            "pollution_level": user.pollution_level
        }
    }

@router.post("/action", summary="낚시 후 행동 선택", description="""
낚시로 잡은 물고기에 대해 행동(판매/방생/수족관)을 선택합니다.
- **판매**: 돈을 획득합니다. (쓰레기는 오염도 감소)
- **방생**: 오염도가 감소하거나(일반/멸종위기), 증가합니다(쓰레기).
- **수족관**: 특별한 효과는 없으나 도감에 기록됩니다 (현재는 판매와 유사).
""")
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
        else:
            money_change = species.base_price
            message = f"{species.name}을(를) 팔아 {species.base_price}원을 벌었습니다."
            
    elif request.action == schemas.ActionType.RELEASE:
        # 2. 방생 (RELEASE)
        if species.type == "TRASH":
            pollution_change = 10 # 쓰레기 투기
            message = "쓰레기를 다시 버려서 바다가 더러워졌습니다..."
        elif species.type == "ENDANGERED":
            pollution_change = -10 # 생태계 회복
            money_change = 1000 # 정부 보조금
            message = "멸종위기종을 보호해주어 정부 지원금을 받았습니다!"
        else:
            pollution_change = -2 # 일반 물고기 방생은 환경에 약간 좋음
            message = f"{species.name}을(를) 방생했습니다."

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

@router.get("/collection/{user_id}", response_model=List[schemas.CollectionItem], summary="유저 도감 조회", description="유저가 잡은 물고기 도감을 조회합니다. 잡지 못한 물고기는 ???로 표시됩니다.")
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
                "is_caught": True,
                "habitat": species.habitat,
                "DstcftCn": species.description.replace("\n\n", " ") if species.description else "" # 설명 추가
            })
        else:
            # 잡은 적 없음 -> 비밀 처리
            result.append({
                "species_id": species.id,
                "name": "???",       # 이름 가리기
                "type": "알 수 없음", # 등급 가리기
                "image_url": "/static/images/question_mark.png",
                "caught_count": 0,
                "is_caught": False,
                "habitat": species.habitat,
                "DstcftCn": "" # 잡기 전에는 특징도 가림 (또는 보여줌? 일단 가림)
            })
            
    return result

# [도우미 함수] 숫자 타입(0,1,2)을 글자로 바꿔주는 함수
def get_type_name(type_code: int):
    if type_code == 0: return "쓰레기"
    if type_code == 1: return "일반 해양 생물"
    if type_code == 2: return "멸종위기종"
    return "기타"