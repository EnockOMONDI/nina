from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('', include('adminside.urls')),
    path('news/', include('blog.urls')),
]

admin.site.site_header = "Ziada Travel Admin"
admin.site.site_title = "Ziada Travel"
admin.site.index_title = "Site Settings"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
