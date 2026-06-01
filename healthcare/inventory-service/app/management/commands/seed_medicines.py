from decimal import Decimal

from django.core.management.base import BaseCommand

from app.models import Medicine


SEED_MEDICINES = [
    {"name": "Paracetamol 500mg",    "unit": "viên",  "stock": 1000, "unit_price": Decimal("2000.00")},
    {"name": "Amoxicillin 500mg",    "unit": "viên",  "stock": 500,  "unit_price": Decimal("5000.00")},
    {"name": "Omeprazole 20mg",      "unit": "viên",  "stock": 400,  "unit_price": Decimal("8000.00")},
    {"name": "Metformin 500mg",      "unit": "viên",  "stock": 600,  "unit_price": Decimal("3000.00")},
    {"name": "Amlodipine 5mg",       "unit": "viên",  "stock": 300,  "unit_price": Decimal("6000.00")},
    {"name": "Azithromycin 250mg",   "unit": "viên",  "stock": 200,  "unit_price": Decimal("12000.00")},
    {"name": "Ibuprofen 400mg",      "unit": "viên",  "stock": 500,  "unit_price": Decimal("4000.00")},
    {"name": "Vitamin C 1000mg",     "unit": "viên",  "stock": 800,  "unit_price": Decimal("2500.00")},
    {"name": "Loratadine 10mg",      "unit": "viên",  "stock": 350,  "unit_price": Decimal("5000.00")},
    {"name": "Betadine 10% 90ml",    "unit": "chai",  "stock": 100,  "unit_price": Decimal("45000.00")},
]


class Command(BaseCommand):
    help = "Seed 10 loại thuốc phổ biến vào database inventory."

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for med_data in SEED_MEDICINES:
            obj, created = Medicine.objects.get_or_create(
                name=med_data["name"],
                defaults={
                    "unit": med_data["unit"],
                    "stock": med_data["stock"],
                    "unit_price": med_data["unit_price"],
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Tạo: {obj.name}"))
                created_count += 1
            else:
                self.stdout.write(f"  - Bỏ qua (đã tồn tại): {obj.name}")
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSeed hoàn tất: {created_count} tạo mới, {skipped_count} đã tồn tại."
            )
        )
