from django.urls import path, include
from . import views

app_name = 'blogg'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('post_create', views.PostCreate.as_view(), name='post_create'),
]
