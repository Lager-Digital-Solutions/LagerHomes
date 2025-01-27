from django.contrib import admin
from django.utils.timezone import now
from .models import *
from django.db.models import Sum
from django.urls import path
from django.template.response import TemplateResponse
from django.utils.html import format_html


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ['image']

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1

class AvailableDateInline(admin.TabularInline):
    model = AvailableDate
    extra = 1
    fields = ['date']

@admin.register(HouseListing)
class HouseListingAdmin(admin.ModelAdmin):
    inlines = [PhotoInline, VideoInline, AvailableDateInline]
    list_display = ('title', 'host', 'city', 'state', 'price_per_night', 'created_at', 'serial_number')
    list_filter = ('city', 'state', 'country', 'is_wheelchair_accessible', 'accessible_bathroom')
    search_fields = ('title', 'description', 'address', 'city', 'state', 'country', 'serial_number')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('bookingID', 'user', 'user_userID', 'check_in', 'check_out', 'days_left', 'created_at')
    search_fields = ('bookingID', 'listing__title', 'user__username', 'user__userID', 'check_in', 'check_out')
    list_filter = ('listing', 'user', 'check_in', 'check_out')

    def days_left(self, obj):
        if obj.check_out < now().date():
            return "Expired"
        return (obj.check_out - now().date()).days

    days_left.short_description = "Days Left"

    def user_userID(self, obj):
        return obj.user.userID

    user_userID.short_description = "User ID"

@admin.register(AffiliateLink)
class AffiliateLinkAdmin(admin.ModelAdmin):
    list_display = ('affiliate', 'link_code', 'created_at')
    search_fields = ('affiliate__username', 'link_code')

@admin.register(AffiliateAgreement)
class AffiliateAgreementAdmin(admin.ModelAdmin):
    list_display = ('affiliate', 'commission_percentage', 'commission_report_button')
    search_fields = ('affiliate__affiliate__username',)

    def commission_report_button(self, obj):
        """
        Add a button that redirects to the correct commission report URL.
        """
        return format_html(
            '<a class="button" href="{}" style="background-color: #007bff; color: white; padding: 5px 10px; text-decoration: none; border-radius: 5px;">View Commission Report</a>',
            "/admin/airbnb/affiliatetracking/commission-report/"
        )

    commission_report_button.short_description = "Commission Report"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'affiliate', 'formatted_commission', 'created_at')
    list_filter = ('created_at', 'affiliate')
    search_fields = ('user__username', 'affiliate__affiliate__username')

    def formatted_commission(self, obj):
        """
        Display the commission amount with high precision.
        """
        return f"{obj.commission_amount:.8f}"  # Display up to 8 decimal places

    formatted_commission.short_description = "Commission Amount"



class ReportAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('commission-report/', self.admin_site.admin_view(self.commission_report_view), name='commission-report'),
        ]
        return custom_urls + urls

    def commission_report_view(self, request):
        affiliates = AffiliateLink.objects.all()
        report = []
        for affiliate in affiliates:
            total_commission = Payment.objects.filter(affiliate=affiliate).aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
            report.append({
                'affiliate': affiliate.affiliate.username,
                'total_commission': total_commission
            })

        context = dict(
            self.admin_site.each_context(request),
            report=report,
        )
        return TemplateResponse(request, "admin/commission_report.html", context)

    def commission_report_button(self, obj):
        """
        Add a button that redirects to the commission report.
        """
        return format_html(
            '<a class="button" href="{}" style="background-color: #007bff; color: white; padding: 5px 10px; text-decoration: none; border-radius: 5px;">View Commission Report</a>',
            "/admin/airbnb/commission-report/"
        )

    commission_report_button.short_description = "Commission Report"

# Register the model with the custom ReportAdmin
admin.site.register(AffiliateTracking, ReportAdmin)

admin.site.register(Amenity)
admin.site.register(Review)
admin.site.register(PropertyType)
admin.site.register(RoomType)
admin.site.register(Photo)
admin.site.register(AvailableDate)
admin.site.register(SavedListing)
admin.site.register(Ad)
