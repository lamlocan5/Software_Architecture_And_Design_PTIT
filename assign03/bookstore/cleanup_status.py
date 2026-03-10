import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookstore.settings")
django.setup()

from orders.models import OrderStatus

def clean_duplicates():
    status_name = "NEW"
    statuses = OrderStatus.objects.filter(name=status_name)
    count = statuses.count()
    
    if count > 1:
        print(f"Found {count} entries for OrderStatus '{status_name}'. Keeping one and deleting others.")
        # Keep the first one
        keep = statuses.first()
        # Exclude the one to keep and delete the rest
        OrderStatus.objects.filter(name=status_name).exclude(pk=keep.pk).delete()
        print("Duplicates deleted.")
    else:
        print(f"No duplicates found for OrderStatus '{status_name}'.")

    # Check for others just in case
    all_names = set(OrderStatus.objects.values_list('name', flat=True))
    for name in all_names:
        qs = OrderStatus.objects.filter(name=name)
        if qs.count() > 1:
             print(f"Found duplicates for '{name}', cleaning up...")
             keep = qs.first()
             qs.exclude(pk=keep.pk).delete()

if __name__ == "__main__":
    clean_duplicates()
