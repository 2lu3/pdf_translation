
from django.urls import path

from .views import modelform_upload


urlpatterns = [
    path("", modelform_upload, name="index"),

]
