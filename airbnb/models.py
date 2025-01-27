from django.db import models
from django.contrib.auth.models import User
from src.settings import AUTH_USER_MODEL
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError

import uuid
import random
import string
from django.db import models
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name}: {self.value}" if self.value else self.name


class PropertyType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class RoomType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class HouseListing(models.Model):
    # Basic Details
    title = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=20, unique=True, blank=True)
    description = models.TextField()
    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True, blank=True)
    is_for_rent = models.BooleanField(default=False)
    is_furnished = models.BooleanField(default=False)
    is_for_sale = models.BooleanField(default=False)
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True, blank=True)

    # Location Details
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    # Pricing Details
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    cleaning_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    extra_guest_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Amenities
    amenities = models.ManyToManyField(Amenity)

    # Booking Rules
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    minimum_stay = models.PositiveIntegerField()
    maximum_stay = models.PositiveIntegerField(null=True, blank=True)
    cancellation_policy = models.CharField(max_length=50, choices=[
        ('Flexible', 'Flexible'),
        ('Moderate', 'Moderate'),
        ('Strict', 'Strict'),
    ])
    house_rules = models.TextField(blank=True)

    # Host Information
    host = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Accessibility Features
    is_wheelchair_accessible = models.BooleanField(default=False)
    has_step_free_access = models.BooleanField(default=False)
    accessible_bathroom = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_average_ratings(self):
        reviews = self.reviews.all()
        if not reviews:
            return {
                'cleanliness': 0,
                'checkin': 0,
                'value': 0,
                'overall': 0
            }

        cleanliness_avg = sum(review.cleanliness_rating for review in reviews) / len(reviews)
        checkin_avg = sum(review.checkin_rating for review in reviews) / len(reviews)
        value_avg = sum(review.value_rating for review in reviews) / len(reviews)
        overall_avg = (cleanliness_avg + checkin_avg + value_avg) / 3

        return {
            'cleanliness': round(cleanliness_avg, 1),
            'checkin': round(checkin_avg, 1),
            'value': round(value_avg, 1),
            'overall': round(overall_avg, 1)
        }

    def __str__(self):
        return self.title


class AvailableDate(models.Model):
    listing = models.ForeignKey(HouseListing, on_delete=models.CASCADE, related_name='available_dates')
    date = models.DateTimeField()

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.listing.title} - {self.date}"


class Photo(models.Model):
    listing = models.ForeignKey(HouseListing, on_delete=models.CASCADE, related_name='photo_set')
    image = models.ImageField(upload_to='photos/')

    def __str__(self):
        return f"Photo for {self.listing.title}"


class Video(models.Model):
    listing = models.ForeignKey(HouseListing, on_delete=models.CASCADE)
    video = models.FileField(upload_to='videos/', blank=True)
    youtube_url = models.URLField(default='', blank=True)

    def __str__(self):
        return f"Video for {self.listing.title}"


class Review(models.Model):
    listing = models.ForeignKey('HouseListing', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cleanliness_rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=Decimal('5.0')
    )
    checkin_rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=Decimal('5.0')
    )
    value_rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=Decimal('5.0')
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.user.role != 'customer':
            raise ValueError("Only customers can write reviews.")
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        return Decimal(sum([
            self.cleanliness_rating,
            self.checkin_rating,
            self.value_rating
        ]) / 3).quantize(Decimal('0.1'))

    def __str__(self):
        return f"Review for {self.listing.title} by {self.user.username}"


AUTH_USER_MODEL = get_user_model()

def generate_booking_id():
    """Generate a custom booking ID starting with 'LAGERHOMES'."""
    random_part = ''.join(random.choices(string.digits, k=9))  # 9-digit random number
    return f"LAGERHOMES-{random_part}"

class Booking(models.Model):
    listing = models.ForeignKey(HouseListing, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    bookingID = models.CharField(max_length=50, unique=True, editable=False, default=generate_booking_id)

    def clean(self):
        # Prevent overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            listing=self.listing,
            check_in__lt=self.check_out,
            check_out__gt=self.check_in
        ).exists()
        if overlapping_bookings:
            raise ValidationError("This listing is already booked for the selected dates.")

    def save(self, *args, **kwargs):
        # Generate a unique bookingID if not already set
        if not self.bookingID:
            self.bookingID = generate_booking_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.bookingID} - {self.listing.title} by {self.user.username}"


class SavedListing(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey(HouseListing, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')  # Prevent duplicate saves

    def __str__(self):
        return f"{self.user.username} saved {self.listing.title}"

class Ad(models.Model):
    title = models.CharField(max_length=555)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    video = models.FileField(upload_to='ads/', blank=True, null=True)
    link = models.URLField(max_length=2555, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class AffiliateLink(models.Model):
    affiliate = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="affiliate_links")
    link_code = models.CharField(max_length=50, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_link_code():
        """Generates a unique affiliate link code."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    def save(self, *args, **kwargs):
        if not self.link_code:
            self.link_code = self.generate_link_code()
        super().save(*args, **kwargs)

    def get_full_link(self):
        """Generates the full link URL."""
        base_url = "https://yourwebsite.com/register/"
        return f"{base_url}?affiliate_code={self.link_code}"

    def __str__(self):
        return f"Affiliate Link for {self.affiliate.username} - {self.link_code}"


class AffiliateTracking(models.Model):
    affiliate = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="affiliate_tracking")
    referred_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchases")
    reservation = models.ForeignKey(Booking, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Affiliate {self.affiliate.username} - Referral {self.referred_user.username}"

class AffiliateAgreement(models.Model):
    affiliate = models.OneToOneField(AffiliateLink, on_delete=models.CASCADE, related_name='agreement')
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Commission percentage for the affiliate.")

    def __str__(self):
        return f"Agreement with {self.affiliate.affiliate.username} - {self.commission_percentage}%"

class Payment(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    affiliate = models.ForeignKey('AffiliateLink', null=True, blank=True, on_delete=models.SET_NULL)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation

    def save(self, *args, **kwargs):
        # Calculate the commission amount if an affiliate is present
        if self.affiliate:
            agreement = AffiliateAgreement.objects.filter(affiliate=self.affiliate).first()
            if agreement:
                self.commission_amount = self.amount * (Decimal(agreement.commission_percentage) / Decimal(100))
            else:
                self.commission_amount = Decimal(0)  # Default to 0 if no agreement
        super().save(*args, **kwargs)

@receiver(post_save, sender=AffiliateLink)
def create_affiliate_agreement(sender, instance, created, **kwargs):
    """
    Automatically create an AffiliateAgreement for new AffiliateLinks with a default commission percentage.
    """
    if created:
        AffiliateAgreement.objects.get_or_create(
            affiliate=instance,
            defaults={'commission_percentage': Decimal('2.0')}  # Default 2% commission
        )
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    affiliate = models.ForeignKey(AffiliateLink, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate commission amount if there is an affiliate
        if self.affiliate:
            agreement = AffiliateAgreement.objects.filter(affiliate=self.affiliate).first()
            if agreement:
                self.commission_amount = self.amount * (agreement.commission_percentage / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment of ${self.amount} by {self.user.username}"