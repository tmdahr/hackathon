# app/routers/shop.py (전체 덮어쓰기)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter(
    prefix="/shop",
    tags=["shop"]
)

# 상점 아이템 목록
SHOP_ITEMS = {
    0: {"name": "기본 낚싯대 (Lv.1)", "price": 0, "level": 1, "desc": "가장 기본적인 나무 낚싯대입니다."},
    1: {"name": "카본 낚싯대 (Lv.2)", "price": 2000, "level": 2, "desc": "쓰레기 -5%, 일반 물고기 +4%, 멸종 위기종 +1%"},
    2: {"name": "티타늄 낚싯대 (Lv.3)", "price": 5000, "level": 3, "desc": "쓰레기 -10%, 일반 물고기 +7%, 멸종 위기종 +3%"}
}

@router.get("/items", summary="상점 아이템 목록 조회", description="구매 가능한 낚싯대 목록을 조회합니다. 각 낚싯대의 효과(쓰레기 감소, 좋은 물고기 확률 증가)를 확인할 수 있습니다.")
def get_items():
    items = []
    for id, data in SHOP_ITEMS.items():
        items.append({
            "item_id": id,
            "name": data["name"],
            "description": data["desc"],
            "price": data["price"],
            "rod_level": data["level"]
        })
    return items

@router.get("/inventory/{user_id}", summary="인벤토리 조회", description="유저가 보유한 낚싯대 목록을 조회합니다. 현재 장착 중인 낚싯대는 is_equipped=True로 표시됩니다.")
def get_inventory(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_inventory = db.query(models.Inventory).filter(models.Inventory.user_id == user_id).all()
    owned_ids = {item.item_id for item in user_inventory}
    owned_ids.add(0)
    
    result = []
    current_rod_level = user.rod_level
    
    for item_id in owned_ids:
        if item_id in SHOP_ITEMS:
            data = SHOP_ITEMS[item_id]
            is_equipped = (data["level"] == current_rod_level)
            
            result.append({
                "item_id": item_id,
                "name": data["name"],
                "description": data["desc"],
                "price": data["price"],
                "rod_level": data["level"],
                "is_equipped": is_equipped
            })
    
    result.sort(key=lambda x: x["rod_level"])
    return result

@router.post("/buy", summary="아이템 구매", description="돈을 사용하여 상점에서 낚싯대를 구매하고 장착합니다. 이미 보유한 아이템은 장착만 수행됩니다.")
def buy_item(request: schemas.BuyRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    item = SHOP_ITEMS.get(request.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # 1. 이미 인벤토리에 있는지 확인
    owned_item = db.query(models.Inventory).filter(
        models.Inventory.user_id == user.id,
        models.Inventory.item_id == request.item_id
    ).first()

    if owned_item:
        user.rod_level = item["level"]
        db.commit()
        db.refresh(user)
        return {
            "message": f"{item['name']}을(를) 장착했습니다! (이미 보유중)",
            "money": user.money,
            "rod_level": user.rod_level
        }

    # 2. 없는 거라면 -> 돈 내고 구매
    if user.money < item["price"]:
        raise HTTPException(status_code=400, detail="돈이 부족합니다!")
        
    user.money -= item["price"]
    user.rod_level = item["level"]
    
    new_inventory = models.Inventory(user_id=user.id, item_id=request.item_id)
    db.add(new_inventory)
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"{item['name']} 구매 성공! 낚싯대가 장착되었습니다.",
        "money": user.money,
        "rod_level": user.rod_level
    }