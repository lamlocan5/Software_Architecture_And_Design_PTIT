from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.IntegerField()),
                ('customer_name', models.CharField(max_length=200)),
                ('customer_email', models.CharField(blank=True, max_length=200)),
                ('shipping_address', models.TextField(blank=True)),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Chờ xác nhận'),
                        ('confirmed', 'Đã xác nhận'),
                        ('shipping', 'Đang giao'),
                        ('delivered', 'Đã giao'),
                        ('cancelled', 'Đã hủy'),
                    ],
                    default='pending',
                    max_length=20,
                )),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'orders',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.IntegerField()),
                ('product_type', models.CharField(
                    choices=[('laptop', 'Laptop'), ('mobile', 'Mobile')],
                    max_length=10,
                )),
                ('product_name', models.CharField(max_length=300)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('quantity', models.IntegerField(default=1)),
                ('order', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='orders.order',
                )),
            ],
            options={
                'db_table': 'order_items',
            },
        ),
    ]
