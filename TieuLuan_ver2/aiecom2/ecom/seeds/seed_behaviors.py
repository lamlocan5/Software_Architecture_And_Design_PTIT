"""
seeds/seed_behaviors.py - Seed behavior_db cho behavior-service
Chạy từ thư mục ecom/:  python seeds/seed_behaviors.py
"""
import os, sys, csv, datetime, random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'behavior-service'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'behavior_project.settings'

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / 'behavior-service' / '.env')

import django
django.setup()

from behaviors.models import UserBehavior, UserProfile
from django.utils import timezone

FIRST = ['An','Bảo','Chi','Dũng','Phú','Giang','Hải','Khoa','Lan','Minh','Nam','Oanh','Phương','Quân','Sơn','Uyên','Vân']
LAST  = ['Nguyễn','Trần','Lê','Phạm','Hoàng','Phan','Vũ','Đặng','Bùi','Hồ','Ngô','Dương']

# Seed users
print("👤 Seeding 500 user profiles vào behavior_db...")
for uid in range(1, 501):
    UserProfile.objects.get_or_create(
        id=uid,
        defaults={
            'name': f"{random.choice(LAST)} {random.choice(FIRST)} {uid}",
            'email': f"user{uid}@ecom.vn"
        }
    )
print(f"  ✅ {UserProfile.objects.count()} users")

# Import behaviors từ CSV
csv_path = Path(__file__).parent / 'data_user500.csv'
if not csv_path.exists():
    print(f"⚠️  Không tìm thấy: {csv_path}")
    sys.exit(1)

print(f"\n📋 Import hành vi từ CSV...")
UserBehavior.objects.all().delete()

rows = []
with open(csv_path, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        try:
            ts = datetime.datetime.strptime(row['timestamp'].strip(), '%Y-%m-%d %H:%M:%S')
            ts = timezone.make_aware(ts, datetime.timezone.utc)
            pid = int(row['product_id'])
            if 1 <= pid <= 30:
                rows.append(UserBehavior(
                    user_id=int(row['user_id']),
                    product_id=pid,
                    action=row['action'].strip(),
                    timestamp=ts
                ))
        except Exception:
            continue

UserBehavior.objects.bulk_create(rows, batch_size=500)
print(f"  ✅ {len(rows)} behaviors trong behavior_db")
print("\n🎉 Seed behavior_db hoàn tất!")
