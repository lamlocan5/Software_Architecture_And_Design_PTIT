from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_cartitem_add_clothing_id_and_nullable_book_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='electronic_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

