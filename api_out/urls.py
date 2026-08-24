from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('artists', views.ArtistViewSet)
router.register('albums', views.AlbumViewSet)
router.register('genres', views.GenreViewSet)
router.register('songs', views.SongViewSet)
router.register('playlists', views.PlaylistViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
