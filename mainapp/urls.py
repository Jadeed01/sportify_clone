from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('search/', views.search, name='search'),
    path('signup/', views.signup, name='signup'),
    path('create_playlist/', views.create_playlist, name='create_playlist'),
    path("songs/", views.see_all, name="see_all"),
]