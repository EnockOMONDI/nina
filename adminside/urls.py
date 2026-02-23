from django.urls import path

from . import views
from users.views import contact_view, corporate_view, inquiry_success_view, package_quote_view

urlpatterns = [
    path('', views.home, name='home'),
    path('packages/', views.packages, name='packages'),
    path('package/<slug:slug>/', views.package_detail, name='package-detail'),
    path('hotels/', views.hotels, name='hotels'),
    path('destinations/', views.destinations, name='destinations'),
    path('about/', views.about, name='about'),
    path('corporates/', corporate_view, name='corporates'),
    path('inquiry-success/', inquiry_success_view, name='inquiry-success'),
    path('contact/', contact_view, name='contact'),
    path('quote/package/', package_quote_view, name='package-quote'),
]
