from django.contrib import admin

from .models import Album, Artist, Favorite, Genre, Mood, Playlist, RecentlyPlayed, Song


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'bio')
    search_fields = ('name',)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_date')
    list_filter = ('artist',)
    search_fields = ('title',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'album', 'genre', 'mood', 'duration')
    list_filter = ('genre', 'mood', 'artist')
    search_fields = ('title', 'artist__name')


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ('mood_type', 'description')


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'user__username')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'song')


@admin.register(RecentlyPlayed)
class RecentlyPlayedAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'played_at')
