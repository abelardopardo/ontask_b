# -*- coding: utf-8 -*-


from django.urls import path

from ontask.accounts import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name="login"),

    path('logout/', views.LogoutView.as_view(), name='logout'),

    path(
        'password-change/',
        views.PasswordChangeView.as_view(),
        name='password-change'),
]
