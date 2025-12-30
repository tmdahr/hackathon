# app/routers/shop.py (전체 덮어쓰기)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(
    prefix="/shop",
    tags=["shop"]
)

# 상점 아이템 목록 (낚싯대)
SHOP_ITEMS = {
    1: {"name": "카본 낚싯대 (Lv.2)", "price": 1000, "level": 2, "desc": "쓰레기 -3%, 생태계 교란종 -3%, 일반 물고기 +5%, 멸종 위기종 +1%"},
    2: {"name": "티타늄 낚싯대 (Lv.3)", "price": 5000, "level": 3, "desc": "쓰레기 -5%, 생태계 교란종 -5%, 일반 물고기 +7%, 멸종 위기종 +3%"}
}

@router.get("/items")
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

@router.post("/buy")
def buy_item(request: schemas.BuyRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    item = SHOP_ITEMS.get(request.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # 이미 더 좋거나 같은 낚싯대를 가지고 있는지 확인
    if user.rod_level >= item["level"]:
        raise HTTPException(status_code=400, detail="이미 같거나 더 좋은 낚싯대를 가지고 있습니다.")

    # 돈 확인
    if user.money < item["price"]:
        raise HTTPException(status_code=400, detail="돈이 부족합니다!")
        
    # 구매 처리 (돈 차감, 낚싯대 레벨 업)
    user.money -= item["price"]
    user.rod_level = item["level"] # 낚싯대 교체
    
    db.commit()
    
    return {
        "message": f"{item['name']} 구매 성공! 낚시 확률이 좋아졌습니다.",
        "current_money": user.money,
        "current_rod_level": user.rod_level
    }