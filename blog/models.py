from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from taggit.managers import TaggableManager
import shortuuid

BLOG_PUBLISH_STATUS = (
    ("in_review", "In Review"),
    ("published", "Published"),
    ("draft", "Draft"),
)


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = CKEditor5Field(config_name="default", blank=True, null=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:100]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to="blog/", blank=True, null=True)
    title = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=1000, unique=True, blank=True)
    excerpt = CKEditor5Field(config_name="default", blank=True, null=True)
    content = CKEditor5Field(config_name="default")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = TaggableManager(blank=True)
    status = models.CharField(choices=BLOG_PUBLISH_STATUS, max_length=100, default="in_review")
    featured = models.BooleanField(default=False)
    trending = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    pid = models.CharField(max_length=25, unique=True, editable=False, default=shortuuid.uuid)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:1000]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
