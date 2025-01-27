# Generated by Django 5.1.4 on 2025-01-17 17:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airbnb", "0006_alter_payment_affiliate_alter_payment_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="houselisting",
            name="is_for_rent",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="houselisting",
            name="is_for_sale",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="houselisting",
            name="is_furnished",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="houselisting",
            name="property_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="airbnb.propertytype",
            ),
        ),
        migrations.AlterField(
            model_name="houselisting",
            name="room_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="airbnb.roomtype",
            ),
        ),
    ]
