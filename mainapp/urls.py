from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('search/', views.search, name='search'),
    path('songs/', views.see_all, name='see_all'),
    path('artist/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    path('create_playlist/', views.create_playlist, name='create_playlist'),
    path('liked/', views.liked_songs, name='liked_songs'),
    # AJAX endpoints used by the player (like / unlike and play tracking).
    path('song/<int:song_id>/like/', views.toggle_favorite, name='toggle_favorite'),
    path('song/<int:song_id>/played/', views.mark_played, name='mark_played'),
]
