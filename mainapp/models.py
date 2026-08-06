from django.contrib.auth.models import User
from django.db import models


class Mood(models.Model):
    MOOD_CHOICES = [
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

    image = models.ImageField(upload_to='moods/')
    mood_type = models.CharField(max_length=20, choices=MOOD_CHOICES, unique=True)
    description = models.CharField(
        max_length=200, blank=True, null=True,
        help_text='Optional description for the mood.',
    )

    def __str__(self):
        return self.mood_type


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
    duration = models.DurationField(help_text='Format: MM:SS or HH:MM:SS')
    audio_file = models.FileField(upload_to='songs/')
    image = models.ImageField(upload_to='songs/', blank=True, null=True)

    def __str__(self):
        return self.title


class Playlist(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song, blank=True)
    cover_image = models.ImageField(upload_to='playlists/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'song')
        ordering = ['user']

    def __str__(self):
        return f'{self.user.username} - {self.song.title}'


class RecentlyPlayed(models.Model):
    """Tracks which songs a user has listened to, for the "Recently played" feed."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    # auto_now updates the timestamp every time the row is saved, so replaying
    # a song bumps it to the top of the list.
    played_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-played_at']
        # A user can only have one row per song; replaying updates it in place.
        constraints = [
            models.UniqueConstraint(fields=['user', 'song'], name='unique_recently_played'),
        ]

    def __str__(self):
        return f'{self.user.username} played {self.song.title}'
