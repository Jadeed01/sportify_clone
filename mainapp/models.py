from django.db import models
from django.contrib.auth.models import User
# Create your models here.

MOOD = [
    ('Happy', 'Happy'),
    ('Sad', 'Sad'),
    ('Energetic', 'Energetic'),
    ('Relaxed', 'Relaxed'),
    ('Romantic', 'Romantic'),
    ('Party', 'Party'),
    ('Workout', 'Workout'),
    ('Chill', 'Chill'),
    ('Focus', 'Focus'),
    ('Sleep', 'Sleep'),
    ('Travel', 'Travel'),
    ('Study', 'Study'),
    ('Motivation', 'Motivation'),
    ('Gaming', 'Gaming'),
    ('Meditation', 'Meditation'),
]



class Mood(models.Model):
    image = models.ImageField(upload_to='moods/')
    mood_type = models.CharField(max_length=20, choices=MOOD, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True,help_text="Optional description for the mood.")


class Artist(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='artists/', blank=True, null=True)
    def __str__(self):
        return self.name

class Album(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    release_date = models.DateField()
    cover_image = models.ImageField(upload_to='albums/', blank=True, null=True)

    def __str__(self):
        return self.title      

class Genre(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Song(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, blank=True, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, blank=True, null=True)
    mood = models.ForeignKey(Mood, on_delete=models.SET_NULL, blank=True, null=True)
    duration = models.DurationField(help_text="Format: MM:SS or HH:MM:SS")
    audio_file = models.FileField(upload_to='songs/')
    image = models.ImageField(upload_to='songs/', blank=True, null=True)

    def __str__(self):
        return self.title

    
class Playlist(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song, blank=True)

    def __str__(self):
        return self.name             

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'song')

    def __str__(self):
        return f"{self.user.username} - {self.song.title}"    