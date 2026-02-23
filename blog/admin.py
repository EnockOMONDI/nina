from django.contrib import admin

from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "active", "created")
    list_filter = ("active", "created")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "status", "category", "user", "featured", "trending", "views", "created")
    list_editable = ("status", "category", "featured", "trending")
    list_filter = ("category", "status", "featured", "trending", "created", "updated")
    search_fields = ("title", "content", "excerpt", "slug")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Basic Info", {"fields": ("title", "slug", "excerpt", "category", "tags", "image")}),
        ("Content", {"fields": ("content",)}),
        ("Publishing", {"fields": ("status", "featured", "trending", "user")}),
    )
