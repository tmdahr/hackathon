from app.database import SessionLocal
from app.models import Collection, Species, FishingHistory

db = SessionLocal()
user_id = 12  # 임시테스트

# 도감 확인
collections = db.query(Collection).filter(Collection.user_id == user_id).all()
print(f'User {user_id} (임시테스트) 도감 기록: {len(collections)}건\n')

# 달랑게 확인
species_32 = db.query(Collection).filter(
    Collection.user_id == user_id,
    Collection.species_id == 32
).first()

if species_32:
    print(f'✓ 달랑게(32) 기록 발견: caught_count={species_32.caught_count}')
else:
    print('✗ 달랑게(32) 기록 없음')

# 달랑게 낚시 기록 확인
fishing_32 = db.query(FishingHistory).filter(
    FishingHistory.user_id == user_id,
    FishingHistory.species_id == 32
).all()

print(f'\n달랑게 낚시 기록: {len(fishing_32)}건')
for record in fishing_32:
    print(f'  Record {record.id}: New={record.was_new}, Invalidated={record.invalidated}, Time={record.caught_at}')

print(f'\n전체 도감 ({len(collections)}건):')
for c in collections[:10]:  # 처음 10개만
    s = db.query(Species).filter(Species.id == c.species_id).first()
    print(f'  Species {c.species_id} ({s.name if s else "Unknown"}): count={c.caught_count}')

if len(collections) > 10:
    print(f'  ... and {len(collections) - 10} more')

db.close()
