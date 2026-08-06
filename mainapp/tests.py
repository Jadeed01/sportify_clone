from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Artist, Favorite, Genre, Mood, RecentlyPlayed, Song


class BaseTestCase(TestCase):
    """Shared setup: one user, one artist, one playable song."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester', password='secret123'
        )
        self.artist = Artist.objects.create(name='Test Artist')
        self.genre = Genre.objects.create(name='Rock')
        self.mood = Mood.objects.create(
            mood_type='Happy', image='moods/happy.jpg'
        )
        self.song = Song.objects.create(
            title='Test Song',
            artist=self.artist,
            genre=self.genre,
            mood=self.mood,
            duration=timedelta(minutes=3, seconds=30),
            audio_file='songs/test.mp3',
            image='songs/test.jpg',
        )


class PageTests(BaseTestCase):
    def test_index_renders_for_guests(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_search_returns_matching_songs(self):
        response = self.client.get(reverse('search'), {'q': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Song')

    def test_search_with_no_hits_shows_message(self):
        response = self.client.get(reverse('search'), {'q': 'zzzznotfound'})
        self.assertContains(response, 'No results found')

    def test_see_all_lists_the_whole_catalog(self):
        response = self.client.get(reverse('see_all'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Song')

    def test_artist_page_lists_their_songs(self):
        response = self.client.get(
            reverse('artist_detail', args=[self.artist.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Artist')
        self.assertContains(response, 'Test Song')

    def test_liked_songs_requires_login(self):
        response = self.client.get(reverse('liked_songs'))
        self.assertEqual(response.status_code, 302)  # redirects to login


class PlayerEndpointTests(BaseTestCase):
    def test_like_then_unlike(self):
        self.client.login(username='tester', password='secret123')
        url = reverse('toggle_favorite', args=[self.song.id])

        first = self.client.post(url)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json(), {'liked': True})
        self.assertTrue(Favorite.objects.filter(user=self.user).exists())

        second = self.client.post(url)
        self.assertEqual(second.json(), {'liked': False})
        self.assertFalse(Favorite.objects.filter(user=self.user).exists())

    def test_mark_played_records_recently_played(self):
        self.client.login(username='tester', password='secret123')
        url = reverse('mark_played', args=[self.song.id])

        response = self.client.post(url)
        self.assertEqual(response.json(), {'ok': True})
        self.assertEqual(
            RecentlyPlayed.objects.filter(user=self.user).count(), 1
        )

    def test_like_requires_login(self):
        response = self.client.post(reverse('toggle_favorite', args=[self.song.id]))
        self.assertEqual(response.status_code, 302)  # redirected to login
