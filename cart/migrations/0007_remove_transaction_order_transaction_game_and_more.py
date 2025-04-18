# Generated by Django 5.0 on 2025-04-13 14:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0006_remove_order_quantity'),
        ('games', '0005_alter_game_stripe_price_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='order',
        ),
        migrations.AddField(
            model_name='transaction',
            name='game',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='games.game'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='session_id',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('completed', 'Completed'), ('failed', 'Failed')], default='failed', max_length=10),
        ),
    ]
