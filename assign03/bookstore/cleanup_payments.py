import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookstore.settings")
django.setup()

from payments.models import PaymentMethod

def clean_duplicates():
    methods = ["COD", "CC"]
    for name in methods:
        qs = PaymentMethod.objects.filter(name=name)
        count = qs.count()
        
        if count > 1:
            print(f"Found {count} entries for PaymentMethod '{name}'. Keeping one and deleting others.")
            keep = qs.first()
            qs.exclude(pk=keep.pk).delete()
            print("Duplicates deleted.")
        else:
            print(f"No duplicates found for PaymentMethod '{name}'.")

    # Check generically
    all_names = set(PaymentMethod.objects.values_list('name', flat=True))
    for name in all_names:
        qs = PaymentMethod.objects.filter(name=name)
        if qs.count() > 1:
             print(f"Found generic duplicates for '{name}', cleaning up...")
             keep = qs.first()
             qs.exclude(pk=keep.pk).delete()

if __name__ == "__main__":
    clean_duplicates()
