from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from datetime import date
from .models import *
from django.db.models.signals import pre_save
from django.dispatch import receiver
import datetime
from django.contrib import messages
# from .forms import ProfilePictureForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import CustomUserChangeForm

import json
import time
import random
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from jose import jwt
import requests
from django.shortcuts import redirect, render
from django.conf import settings

from django.db import transaction
from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404
from django.db import transaction
from .models import Booking, HouseListing
import random
from .models import generate_booking_id
import json
from django.utils.dateparse import parse_date

from datetime import date

from django.core.mail import send_mail
from django.contrib import messages
from django.http import HttpResponseRedirect

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# from .forms import AdditionalUserInfoForm

import random
import time
import json
import requests
from django.shortcuts import redirect, render
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend

from django.core.mail import send_mail
from django.shortcuts import render
from .forms import ContactForm
from dateutil.relativedelta import relativedelta
from datetime import timedelta

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
from datetime import timedelta, date
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.utils.dateparse import parse_date
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

import logging

# Set up logger
logger = logging.getLogger(__name__)


class SantimpaySDK:
    URL = "https://services.santimpay.com/api/v1/gateway"

    def __init__(self, merchant_id, private_key):
        self.private_key = private_key
        self.merchant_id = merchant_id

    def generate_signed_token(self, amount, payment_reason):
        current_time = int(time.time())
        data = {
            'amount': amount,
            'paymentReason': payment_reason,
            'merchantId': self.merchant_id,
            'generated': current_time
        }

        try:
            private_key = serialization.load_pem_private_key(
                self.private_key.encode(),
                password=None,
                backend=default_backend()
            )
        except ValueError as e:
            raise ValueError(f"Error loading private key: {e}")

        jwt_token = jwt.encode(data, private_key, algorithm='ES256')

        return jwt_token

    def generate_payment_url(self, _id, amount, payment_reason, success_redirect_url, failure_redirect_url,
                             notify_url, phone_number="", cancel_redirect_url=None):
        token = self.generate_signed_token(amount, payment_reason)
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        body = {
            'id': _id,
            'amount': amount,
            'reason': payment_reason,
            'merchantId': self.merchant_id,
            'signedToken': token,
            'successRedirectUrl': success_redirect_url,
            'failureRedirectUrl': failure_redirect_url,
            'notifyUrl': notify_url,
            'cancelRedirectUrl': cancel_redirect_url
        }

        if phone_number and len(phone_number) > 1:
            body['phoneNumber'] = phone_number

        try:
            response = requests.post(f"{self.URL}/initiate-payment",
                                     headers=headers, data=json.dumps(body))
            response_content = response.content.decode('utf-8')
            response_content = response_content.replace("\\u0026", "&")
            return response_content
        except Exception as e:
            return f"Error: {e}"


def initiate_payment(request, listing_id):
    if request.method == "POST":
        # Collect form data
        pricing_mode = request.POST.get("pricing_mode")
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")
        total_price = request.POST.get("total_price")
        phone_number = request.POST.get("phone_number", "")

        print("Received POST data:", {
            "pricing_mode": pricing_mode,
            "check_in": check_in,
            "check_out": check_out,
            "total_price": total_price,
            "phone_number": phone_number,
        })

        # Validate total_price
        try:
            total_price = float(total_price)
            if total_price <= 0:
                raise ValueError("Invalid total price")
        except ValueError as e:
            return render(request, "airbnb/error.html", {"error": f"Invalid price: {e}"})

        # Initialize Santimpay client
        PRIVATE_KEY_IN_PEM = """\
-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIF1FiolOiNt9VZga7Xv2Hnc9ogec+n17oAC7vtls3fBuoAoGCCqGSM49
AwEHoUQDQgAEEcfE9DYOz/pkenjJ4Abdgr2BsYB5zhh+3RxlHA+ZDlQ63+RTJS2B
A2vqUeASic2BPMd+LqrAlo+5nCLqdBm//g==
-----END EC PRIVATE KEY-----
"""
        MERCHANT_ID = '9e2dab64-e2bb-4837-9b85-d855dd878d2b'

        client = SantimpaySDK(MERCHANT_ID, PRIVATE_KEY_IN_PEM)

        # Generate payment ID and URLs
        payment_id = str(random.randint(1, 1000000000))
        success_redirect_url = request.build_absolute_uri(
            f'/payment-success/?payment_id={payment_id}&listing_id={listing_id}&check_in={check_in}&check_out={check_out}&amount={total_price}'
        )
        failure_redirect_url = request.build_absolute_uri('/payment-failure/')
        notify_url = request.build_absolute_uri('/payment-notify/')
        cancel_redirect_url = request.build_absolute_uri('/payment-cancel/')

        print("Generating payment URL...")
        response = client.generate_payment_url(
            payment_id, total_price, f"Payment for listing {listing_id} ({pricing_mode})",
            success_redirect_url, failure_redirect_url, notify_url, phone_number, cancel_redirect_url
        )

        try:
            payment_data = json.loads(response)
            payment_url = payment_data.get("url")
            if payment_url:
                return redirect(payment_url)
            else:
                error_message = payment_data.get("message", "Unknown error")
                return render(request, "airbnb/error.html", {"error": error_message})
        except json.JSONDecodeError as e:
            return render(request, "airbnb/error.html", {"error": "Invalid response from Santimpay API"})
    else:
        return redirect("/")


def payment_success(request):
    logger.info("Payment success view started")
    payment_id = request.GET.get("payment_id")
    listing_id = request.GET.get("listing_id")
    check_in = request.GET.get("check_in")
    check_out = request.GET.get("check_out")
    amount = request.GET.get("amount")

    logger.info(f"Received parameters: payment_id={payment_id}, listing_id={listing_id}, "
               f"check_in={check_in}, check_out={check_out}, amount={amount}")

    if not amount:
        logger.error("Payment amount is missing")
        return render(request, "airbnb/error.html", {"error": "Payment amount is missing."})

    try:
        amount = Decimal(amount)
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid payment amount: {str(e)}")
        return render(request, "airbnb/error.html", {"error": "Invalid payment amount."})

    listing = get_object_or_404(HouseListing, id=listing_id)
    user = request.user
    logger.info(f"User: {user.email}, Listing: {listing.title}")

    # Handle missing check-in and check-out dates
    if not check_in or not check_out:
        today = date.today()
        check_in = today.isoformat()
        check_out = (today + timedelta(days=1)).isoformat()
        logger.info("Using default dates for check-in/check-out")

    try:
        check_in_date = parse_date(check_in)
        check_out_date = parse_date(check_out)
        if not check_in_date or not check_out_date or check_out_date <= check_in_date:
            raise ValueError("Invalid check-in or check-out dates.")
    except ValueError as e:
        logger.error(f"Date parsing error: {str(e)}")
        return render(request, "airbnb/error.html", {"error": f"Date error: {e}"})

    total_days = (check_out_date - check_in_date).days
    logger.info(f"Total days: {total_days}")

    with transaction.atomic():
        try:
            booking = Booking.objects.create(
                listing=listing,
                user=user,
                check_in=check_in_date,
                check_out=check_out_date
            )
            logger.info(f"Booking created successfully: {booking.id}")

            listing.is_available = False
            listing.days_left = total_days
            listing.save()
            logger.info("Listing updated successfully")

            # Email configuration
            from_email = settings.DEFAULT_FROM_EMAIL
            admin_email = "contact@lagerhomes.com"

            logger.info(f"Email configuration: from_email={from_email}, admin_email={admin_email}")

            # Common context for all emails
            email_context = {
                'booking': booking,
                'listing': listing,
                'user': user,
                'amount': amount,
                'payment_id': payment_id,
                'check_in': check_in_date,
                'check_out': check_out_date,
                'total_days': total_days,
            }

            # 1. Email to the user
            try:
                logger.info(f"Attempting to send email to user: {user.email}")
                user_html_message = render_to_string('airbnb/email/booking_confirmation_user.html', email_context)
                user_plain_message = strip_tags(user_html_message)
                send_mail(
                    subject='Lager Homes: Your Booking Confirmation',
                    message=user_plain_message,
                    html_message=user_html_message,
                    from_email=from_email,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                logger.info("User email sent successfully")
            except Exception as e:
                logger.error(f"Failed to send user email: {str(e)}", exc_info=True)

            # 2. Email to the host
            try:
                logger.info(f"Attempting to send email to host: {listing.host.email}")
                host_html_message = render_to_string('airbnb/email/booking_notification_host.html', email_context)
                host_plain_message = strip_tags(host_html_message)
                send_mail(
                    subject='Lager Homes: New Booking for Your Property',
                    message=host_plain_message,
                    html_message=host_html_message,
                    from_email=from_email,
                    recipient_list=[listing.host.email],
                    fail_silently=False,
                )
                logger.info("Host email sent successfully")
            except Exception as e:
                logger.error(f"Failed to send host email: {str(e)}", exc_info=True)

            # 3. Email to admin
            try:
                logger.info("Attempting to send email to admin")
                admin_html_message = render_to_string('airbnb/email/booking_notification_admin.html', email_context)
                admin_plain_message = strip_tags(admin_html_message)
                send_mail(
                    subject='Lager Homes: New Booking Notification',
                    message=admin_plain_message,
                    html_message=admin_html_message,
                    from_email=from_email,
                    recipient_list=[admin_email],
                    fail_silently=False,
                )
                logger.info("Admin email sent successfully")
            except Exception as e:
                logger.error(f"Failed to send admin email: {str(e)}", exc_info=True)

        except Exception as e:
            logger.error(f"Transaction error: {str(e)}", exc_info=True)
            raise

    logger.info("Payment success view completed successfully")
    return render(request, "airbnb/payment_success.html", {"booking": booking})



def payment_failure(request):
    reason = request.GET.get("reason", "unknown")
    error_message = "Your transaction was canceled or failed. Please try again."
    if reason == "timeout":
        error_message = "The payment timed out. Please try again."
    elif reason == "canceled":
        error_message = "You canceled the transaction. Please try again."

    context = {"error_message": error_message}
    return render(request, "airbnb/payment_failure.html", context)



def santim_payment(request, listing_id):
    if request.method == "POST":
        # Collect data from the form
        national_id = request.POST.get("national_id")
        selfie = request.FILES.get("selfie")

        # Validate data
        if not national_id or not selfie:
            messages.error(request, "National ID and Selfie are required.")
            return redirect("airbnb:additional_user_info", listing_id=listing_id)

        # Save National ID to user's profile if it doesn't already exist or is updated
        if request.user.national_id != national_id:
            request.user.national_id = national_id
            request.user.save()

        # Save booking details to the host's dashboard
        listing = get_object_or_404(HouseListing, id=listing_id)
        host = listing.host

        Booking.objects.create(
            listing=listing,
            user=request.user,
            check_in=request.POST.get("check_in"),
            check_out=request.POST.get("check_out"),
        )

        # Redirect to payment gateway (SantimPay integration)
        PRIVATE_KEY_IN_PEM = """\
-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIBnRbzjuhU5rdu9f9ZCgOdVOyyVztQuvs1Bj/UmtE3XqoAoGCCqGSM49
AwEHoUQDQgAEr0R59UmCtzUjFYbpLw1d5iyH7StI0uYs1mtGCEU5mFzKzGfQZt09
WlHtGQU4W2p8PQ4hxCOTWhEmN5GQqKOWFg==
-----END EC PRIVATE KEY-----
"""
        MERCHANT_ID = "9e2dab64-e2bb-4837-9b85-d855dd878d2b"

        client = SantimpaySDK(MERCHANT_ID, PRIVATE_KEY_IN_PEM)

        payment_id = f"PAY-{random.randint(1000, 9999)}"
        success_redirect_url = request.build_absolute_uri(
            f"/payment-success/?payment_id={payment_id}&listing_id={listing_id}"
        )
        failure_redirect_url = request.build_absolute_uri("/payment-failure/")
        notify_url = request.build_absolute_uri("/payment-notify/")

        total_price = float(request.POST.get("total_price"))

        # Generate payment URL
        payment_url = client.generate_payment_url(
            payment_id,
            total_price,
            f"Booking for {listing.title}",
            success_redirect_url,
            failure_redirect_url,
            notify_url,
        )

        return redirect(payment_url)

    return redirect("/")

def check_availability(request, listing_id):
    if request.method == "GET":
        check_in = request.GET.get("check_in")
        check_out = request.GET.get("check_out")

        if not check_in or not check_out:
            return JsonResponse({"available": False, "message": "Please select valid check-in and check-out dates."}, status=400)

        # Convert string dates to datetime objects
        check_in = datetime.datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out = datetime.datetime.strptime(check_out, "%Y-%m-%d").date()

        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            listing_id=listing_id,
            check_in__lt=check_out,
            check_out__gt=check_in
        ).exists()

        if overlapping_bookings:
            return JsonResponse({"available": False, "message": "This listing is already booked for the selected dates."})

        return JsonResponse({"available": True, "message": "This listing is available for booking."})


def index(request):
    # Fetch all listings, property types, room types, and amenities
    listings = HouseListing.objects.all()
    property_types = PropertyType.objects.all()
    room_types = RoomType.objects.all()
    amenities = Amenity.objects.all()
    ads = Ad.objects.filter(featured=True)

    # --- Existing Filters ---
    property_type = request.GET.get('property_type')
    if property_type:
        listings = listings.filter(property_type_id=property_type)

    room_type = request.GET.get('room_type')
    if room_type:
        listings = listings.filter(room_type_id=room_type)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        listings = listings.filter(price_per_night__gte=min_price)
    if max_price:
        listings = listings.filter(price_per_night__lte=max_price)

    selected_amenities = request.GET.getlist('amenities')
    if selected_amenities:
        listings = listings.filter(amenities__id__in=selected_amenities).distinct()

    location = request.GET.get('location')
    if location:
        listings = listings.filter(
            Q(city__icontains=location) |
            Q(country__icontains=location) |
            Q(state__icontains=location) |
            Q(address__icontains=location)
        )

    # --- NEW FILTERS ---
    if request.GET.get('filter_by') == 'rent':
        listings = listings.filter(is_for_rent=True)
    elif request.GET.get('filter_by') == 'furnished':
        listings = listings.filter(is_furnished=True)
    elif request.GET.get('filter_by') == 'sale':
        listings = listings.filter(is_for_sale=True)

    country_filter = request.GET.get('country')
    if country_filter == 'ethiopia':
        listings = listings.filter(country__iexact='Ethiopia')
    elif country_filter == 'usa':
        listings = listings.filter(country__iexact='USA')

    # Pagination Setup
    page = request.GET.get('page', 1)  # Default to the first page
    paginator = Paginator(listings, 10)  # Show 20 listings per page

    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        listings = paginator.page(1)
    except EmptyPage:
        listings = paginator.page(paginator.num_pages)

    # --- Availability and Photos ---
    today = date.today()
    for listing in listings:
        listing.total_photos = listing.photo_set.count()
        if not request.user.is_authenticated:
            # listing.limited_photos = listing.photo_set.all()[:2]
            listing.limited_photos = listing.photo_set.all()

        else:
            listing.limited_photos = listing.photo_set.all()

        bookings = Booking.objects.filter(listing=listing, check_out__gte=today).order_by('check_out')
        if bookings.exists():
            next_booking = bookings.first()
            if next_booking.check_in <= today < next_booking.check_out:
                listing.days_left = (next_booking.check_out - today).days
                listing.is_available = False
            else:
                listing.days_left = None
                listing.is_available = True
        else:
            listing.days_left = None
            listing.is_available = True

        if request.user.is_authenticated:
            listing.is_saved = SavedListing.objects.filter(user=request.user, listing=listing).exists()
        else:
            listing.is_saved = False

    # --- Context for Template ---
    context = {
        'listings': listings,
        'is_authenticated': request.user.is_authenticated,
        'property_types': property_types,
        'room_types': room_types,
        'amenities': amenities,
        'selected_filters': request.GET,
        'ads': ads,
    }
    return render(request, 'airbnb/index.html', context)

# Save Listing Function
def save_listing(request, listing_id):
    if request.user.is_authenticated:
        listing = get_object_or_404(HouseListing, id=listing_id)
        saved_listing, created = SavedListing.objects.get_or_create(user=request.user, listing=listing)
        if created:
            return JsonResponse({'status': 'saved'})
        return JsonResponse({'status': 'already_saved'})
    return JsonResponse({'status': 'unauthenticated'})

# Unsave Listing Function
def unsave_listing(request, listing_id):
    if request.method == "POST" and request.user.is_authenticated:
        listing = get_object_or_404(HouseListing, id=listing_id)
        SavedListing.objects.filter(user=request.user, listing=listing).delete()

        # Return success response for AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if it's an AJAX request
            return JsonResponse({'status': 'unsaved'})
        else:
            # Redirect if not an AJAX request
            return redirect('airbnb:saved_listings')

    # If not authenticated, redirect to login
    return redirect('login')

def saved_listings(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Get all saved listings for the logged-in user
    saved_listings = SavedListing.objects.filter(user=request.user).select_related('listing')

    # Calculate availability for each listing
    today = date.today()
    for saved in saved_listings:
        # Add photos to each listing
        saved.listing.photos = saved.listing.photo_set.all()

        # Check for bookings and availability
        bookings = Booking.objects.filter(
            listing=saved.listing,
            check_out__gte=today
        ).order_by('check_out')

        if bookings.exists():
            next_booking = bookings.first()
            if next_booking.check_in <= today <= next_booking.check_out:
                # Listing is currently booked
                saved.listing.days_left = (next_booking.check_out - today).days
                saved.listing.is_available = False
            else:
                # Listing is available
                saved.listing.days_left = 0
                saved.listing.is_available = True
        else:
            # No bookings, listing is available
            saved.listing.days_left = 0
            saved.listing.is_available = True

    context = {
        'saved_listings': saved_listings,
        'is_authenticated': request.user.is_authenticated
    }
    return render(request, 'airbnb/saved_listings.html', context)


# @login_required
def listing_detail(request, listing_id):
    listing = get_object_or_404(HouseListing, id=listing_id)

    # Get all photos and total count
    all_photos = listing.photo_set.all()
    total_photos = all_photos.count()
    display_photos = all_photos[:5]

    all_reviews = Review.objects.all().filter(listing=listing)
    reviews = listing.reviews.all().order_by('-created_at')[:3]
    average_ratings = listing.get_average_ratings()

    # Get associated video (if any)
    video = listing.video_set.first()
    youtube_url = None
    if video and video.youtube_url:
        video_id = video.youtube_url.split('v=')[-1]
        youtube_url = f"https://www.youtube.com/embed/{video_id}"

    # Check availability and calculate days left
    today = date.today()
    bookings = Booking.objects.filter(
        listing=listing,
        check_out__gte=today  # Ensure it overlaps with today or the future
    ).order_by('check_in')

    if bookings.exists():
        # If the listing is booked, calculate days left
        next_booking = bookings.first()
        is_available = False
        days_left = (next_booking.check_out - today).days
    else:
        # If no bookings exist, the listing is available
        is_available = True
        days_left = None

    context = {
        'listing': listing,
        'photos': display_photos,
        'all_photos': all_photos,
        'total_photos': total_photos,
        'reviews': reviews,
        'youtube_url': youtube_url,
        'video_id': video_id if video and video.youtube_url else None,
        'average_ratings': average_ratings,
        'all_reviews': all_reviews,
        'is_available': is_available,  # Pass availability status to the template
        'days_left': days_left,        # Pass days left to the template
    }
    return render(request, 'airbnb/listing_detail.html', context)

@login_required
def all_reviews(request, listing_id):
    listing = get_object_or_404(HouseListing, id=listing_id)
    reviews = listing.reviews.all().order_by('-created_at')
    context = {
        'listing': listing,
        'reviews': reviews,
    }
    return render(request, 'airbnb/all_reviews.html', context)

@receiver(pre_save, sender=HouseListing)
def generate_serial_number(sender, instance, **kwargs):
    if not instance.serial_number:  # Generate only if serial_number is not provided
        current_year = datetime.datetime.now().year
        # Get the highest current serial number
        last_listing = HouseListing.objects.filter(serial_number__startswith=f'LH-{current_year}-').order_by('-serial_number').first()
        if last_listing:
            # Extract the numeric part of the serial number
            last_serial = int(last_listing.serial_number.split('-')[-1])
            new_serial = last_serial + 1
        else:
            new_serial = 1
        # Generate the new serial number
        instance.serial_number = f'LH-{current_year}-{new_serial:06d}'

def add_review(request, listing_id):
    if request.method == 'POST':
        listing = get_object_or_404(HouseListing, id=listing_id)

        if request.user.role != 'customer':
            messages.error(request, "Only customers can write reviews.")
            return redirect('airbnb:listing_detail', listing_id=listing_id)

        cleanliness_rating = request.POST.get('cleanliness_rating')
        checkin_rating = request.POST.get('checkin_rating')
        value_rating = request.POST.get('value_rating')
        comment = request.POST.get('comment')

        try:
            review = Review.objects.create(
                listing=listing,
                user=request.user,
                cleanliness_rating=cleanliness_rating,
                checkin_rating=checkin_rating,
                value_rating=value_rating,
                comment=comment
            )
            messages.success(request, "Review added successfully.")
        except ValueError as e:
            messages.error(request, str(e))

        return redirect('airbnb:listing_detail', listing_id=listing_id)

@login_required
def customer_dashboard(request):
    if request.user.role != "customer":
        return redirect("airbnb:host_dashboard")

    if request.method == "POST" and "profile_form" in request.POST:
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
        else:
            messages.error(request, "Failed to update profile. Please correct the errors below.")
    else:
        form = CustomUserChangeForm(instance=request.user)

    password_form = PasswordChangeForm(user=request.user, data=request.POST if "password_form" in request.POST else None)
    if request.method == "POST" and "password_form" in request.POST:
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
        else:
            messages.error(request, "Failed to change password. Please correct the errors below.")

    saved_listings = request.user.savedlisting_set.all()

    context = {
        "form": form,
        "password_form": password_form,
        "saved_listings": saved_listings,
    }
    return render(request, "users/customer_dashboard.html", context)

@login_required
def host_dashboard(request):
    if request.user.role != 'host':
        return redirect('airbnb:customer_dashboard')  # Redirect non-hosts

    # Handle profile updates (including name and email)
    if request.method == 'POST' and 'profile_form' in request.POST:
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
        else:
            messages.error(request, "Failed to update profile. Please correct the errors below.")
    else:
        form = CustomUserChangeForm(instance=request.user)

    # Handle password change
    password_form = PasswordChangeForm(user=request.user, data=request.POST if 'password_form' in request.POST else None)
    if request.method == 'POST' and 'password_form' in request.POST:
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Prevents logging out after password change
            messages.success(request, "Password changed successfully.")
        else:
            messages.error(request, "Failed to change password. Please fix the errors below.")

    # Get the host's listings
    listings = HouseListing.objects.filter(host=request.user)

    context = {
        'form': form,
        'password_form': password_form,
        'listings': listings,
    }
    return render(request, 'users/host_dashboard.html', context)

def terms_of_service(request):
    return render(request, 'airbnb/terms_of_service.html')

def about(request):
    return render(request, 'airbnb/about.html')

def contact(request):
    success = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Extract data from the form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Compose the email
            subject = f"Contact Form Submission from {name}"
            body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            to_email = 'lagerhomes@gmail.com'  # Replace with your email address

            # Send email
            send_mail(subject, body, email, [to_email])

            # Indicate success
            success = True
    else:
        form = ContactForm()

    return render(request, 'airbnb/contact.html', {'form': form, 'success': success})


def faq(request):
    return render(request, 'airbnb/faq.html')

def policy(request):
    return render(request, 'airbnb/policy.html')

