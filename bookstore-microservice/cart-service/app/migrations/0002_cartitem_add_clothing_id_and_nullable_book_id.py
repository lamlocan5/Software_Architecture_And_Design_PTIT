from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='book_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='clothing_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

