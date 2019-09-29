
from django.contrib import admin
from django.urls import path, include
from pro import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # path('suka/', views.index),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

