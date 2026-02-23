from django.urls import path

from . import views

urlpatterns = [
    path("", views.blog_list, name="blog-list"),
    path("search/", views.blog_search, name="blog-search"),
    path("category/<slug:slug>/", views.category_detail, name="category-detail"),
    path("post/<slug:slug>/", views.blog_detail, name="blog-detail"),
    path("p/<str:pid>/", views.blog_detail_redirect, name="blog-detail-redirect"),
    path("rss/", views.blog_rss, name="blog-rss"),
    path("sitemap/", views.blog_sitemap, name="blog-sitemap"),
]
