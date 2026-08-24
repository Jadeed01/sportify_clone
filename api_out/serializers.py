from rest_framework import serializers
from mainapp.models import Artist, Album, Genre, Song, Playlist, Favorite

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'

class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = '__all__'

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class SongSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    album = AlbumSerializer(read_only=True)
    genre = GenreSerializer(read_only=True)

    class Meta:
        model = Song
        fields = '__all__'

class PlaylistSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = '__all__'