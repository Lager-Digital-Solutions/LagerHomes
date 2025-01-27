from django.urls import path
from . import views

app_name = 'airbnb'

urlpatterns = [
    path('', views.index, name='index'),
    path('save-listing/<int:listing_id>/', views.save_listing, name='save_listing'),
    path('unsave-listing/<int:listing_id>/', views.unsave_listing, name='unsave_listing'),
    path('saved-listings/', views.saved_listings, name='saved_listings'),
    path('listing/<int:listing_id>/', views.listing_detail, name='listing_detail'),  
    path('listing/<int:listing_id>/add-review/', views.add_review, name='add_review'),  
    path('dashboard/', views.customer_dashboard, name='dashboard'),
    path('host_dashboard/', views.host_dashboard, name='host_dashboard'),
    path('terms/', views.terms_of_service, name='terms'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('listing/<int:listing_id>/reviews/', views.all_reviews, name='all_reviews'),
    path('listing/<int:listing_id>/initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('check-availability/<int:listing_id>/', views.check_availability, name='check_availability'),
    path('payment-failure/', views.payment_failure, name='payment_failure'),
    path('faq/', views.faq, name='faq'),
    path('policy/', views.policy, name='policy'),
]
