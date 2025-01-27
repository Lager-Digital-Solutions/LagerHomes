# Generated by Django 5.1.4 on 2025-01-13 08:44

import airbnb.models
import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=555)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='ads/')),
                ('video', models.FileField(blank=True, null=True, upload_to='ads/')),
                ('link', models.URLField(blank=True, max_length=2555, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('featured', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Amenity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AvailableDate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in', models.DateField()),
                ('check_out', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('bookingID', models.CharField(default=airbnb.models.generate_booking_id, editable=False, max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='HouseListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('serial_number', models.CharField(blank=True, max_length=20, unique=True)),
                ('description', models.TextField()),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('price_per_month', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('price_per_night', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cleaning_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('security_deposit', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('extra_guest_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('check_in_time', models.DateTimeField(blank=True, null=True)),
                ('check_out_time', models.DateTimeField(blank=True, null=True)),
                ('minimum_stay', models.PositiveIntegerField()),
                ('maximum_stay', models.PositiveIntegerField(blank=True, null=True)),
                ('cancellation_policy', models.CharField(choices=[('Flexible', 'Flexible'), ('Moderate', 'Moderate'), ('Strict', 'Strict')], max_length=50)),
                ('house_rules', models.TextField(blank=True)),
                ('is_wheelchair_accessible', models.BooleanField(default=False)),
                ('has_step_free_access', models.BooleanField(default=False)),
                ('accessible_bathroom', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='photos/')),
            ],
        ),
        migrations.CreateModel(
            name='PropertyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cleanliness_rating', models.DecimalField(decimal_places=1, default=Decimal('5.0'), max_digits=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('checkin_rating', models.DecimalField(decimal_places=1, default=Decimal('5.0'), max_digits=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('value_rating', models.DecimalField(decimal_places=1, default=Decimal('5.0'), max_digits=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RoomType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SavedListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(blank=True, upload_to='videos/')),
                ('youtube_url', models.URLField(blank=True, default='')),
            ],
        ),
    ]
