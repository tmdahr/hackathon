from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class SpeciesType(str, Enum):
    TRASH = "TRASH"
    INVASIVE = "INVASIVE"
    NORMAL = "NORMAL"
    ENDANGERED = "ENDANGERED"

# 낚시 결과 반환용
class FishResponse(BaseModel):
    species_name: str
    species_type: SpeciesType
    image_url: Optional[str] = None
    is_new: bool
    pollution_level: int # 현재 오염도도 같이 주면 프론트가 편함

    class Config:
        from_attributes = True

# 유저 행동 요청용 (판매/방생/수족관)
class ActionType(str, Enum):
    SELL = "SELL"
    RELEASE = "RELEASE"
    AQUARIUM = "AQUARIUM"

class UserActionRequest(BaseModel):
    user_id: int
    species_id: int
    action: ActionType

# --- User 관련 ---
class UserCreate(BaseModel):
    nickname: str

class UserResponse(BaseModel):
    id: int
    nickname: str
    money: int
    pollution_level: int
    
    class Config:
        from_attributes = True

# --- Shop 관련 ---
class ShopItem(BaseModel):
    item_id: int
    name: str
    description: str
    price: int
    rod_level: int

class BuyRequest(BaseModel):
    user_id: int
    item_id: int

class CollectionItem(BaseModel):
    species_id: int
    name: str          # 잡았으면 이름, 못 잡았으면 "???"
    type: str          # 물고기 등급 (일반, 희귀 등)
    image_url: str     # 이미지 주소
    caught_count: int  # 잡은 횟수 (없으면 0)
    is_caught: bool    # 잡은 적 있는지 여부
    
    class Config:
        from_attributes = True