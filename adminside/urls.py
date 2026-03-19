from django.urls import path

from . import views
from users.views import (
    career_application_submit_view,
    contact_view,
    corporate_view,
    hotel_quote_view,
    inquiry_success_view,
    package_quote_view,
    trip_feedback_view,
)

urlpatterns = [
    path('', views.home, name='home'),
    path('packages/', views.packages, name='packages'),
    path('package/<slug:slug>/', views.package_detail, name='package-detail'),
    path('hotels/', views.hotels, name='hotels'),
    path('careers/', views.careers, name='careers'),
    path('careers/apply/', career_application_submit_view, name='career-apply'),
    path('careers/<slug:slug>/', views.career_detail, name='career-detail'),
    path('destinations/', views.destinations, name='destinations'),
    path('about/', views.about, name='about'),
    path('admin-tutorial/', views.admin_tutorial, name='admin-tutorial'),
    path('corporates/', corporate_view, name='corporates'),
    path('inquiry-success/', inquiry_success_view, name='inquiry-success'),
    path('contact/', contact_view, name='contact'),
    path('trip-feedback/', trip_feedback_view, name='trip-feedback'),
    path('quote/package/', package_quote_view, name='package-quote'),
    path('quote/hotel/', hotel_quote_view, name='hotel-quote'),
]
