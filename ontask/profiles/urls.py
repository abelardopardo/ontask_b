"""URLs for handling profile pages."""
from django.urls import path

from . import views

app_name = 'profiles'

urlpatterns = [
    path('me', views.ShowProfile.as_view(), name='show_self'),
    path('me/edit', views.EditProfile.as_view(), name='edit_self'),
    path('reset_token', views.reset_token, name='reset_token'),
    path('<int:pk>/reset_token/', views.delete_token, name='delete_token'),
    path('<slug:slug>', views.ShowProfile.as_view(), name='show'),
]
