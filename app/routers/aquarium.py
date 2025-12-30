from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter(
    prefix="/aquarium",
    tags=["aquarium"]
)

@router.get("/{user_id}", response_model=schemas.AquariumResponse, summary="아쿠아리움 목록 조회", description="유저의 아쿠아리움에 있는 물고기 목록을 조회합니다.")
def get_aquarium(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 아쿠아리움 아이템 조회 (Species 정보 포함)
    aquarium_items = db.query(models.Aquarium).filter(models.Aquarium.user_id == user_id).all()
    
    fish_list = []
    for item in aquarium_items:
        fish_list.append(schemas.AquariumItem(
            id=item.id,
            species_id=item.species_id,
            name=item.species.name,
            image_url=item.species.image_url,
            caught_at=item.caught_at
        ))
    
    return schemas.AquariumResponse(
        user_id=user.id,
        nickname=user.nickname,
        fish_list=fish_list
    )