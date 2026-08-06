from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import (
    Album,
    Artist,
    Favorite,
    Genre,
    Mood,
    Playlist,
    RecentlyPlayed,
    Song,
)


def _liked_song_ids(request):
    """Return the ids of songs the current user has liked (empty for guests)."""
    if request.user.is_authenticated:
        return list(
            Favorite.objects.filter(user=request.user).values_list('song_id', flat=True)
        )
    return []


def index(request):
    """Home feed: featured songs, moods, and the user's playlists / history."""
    playlists = (
        Playlist.objects.filter(user=request.user)
        if request.user.is_authenticated
        else Playlist.objects.none()
    )
    songs = Song.objects.all()[:6]
    moods = Mood.objects.all()

    # Recently played lives per-user, so guests just see an empty section.
    recently_played = (
        [entry.song for entry in RecentlyPlayed.objects.select_related('song', 'song__artist').filter(user=request.user)[:6]]
        if request.user.is_authenticated
        else []
    )

    return render(request, 'mainapp/index.html', {
        'playlists': playlists,
        'songs': songs,
        'moods': moods,
        'recently_played': recently_played,
        'liked_song_ids': _liked_song_ids(request),
    })


def search(request):
    """Search every catalog type at once: songs, artists, albums, genres, moods."""
    query = request.GET.get('q', '').strip()
    results = {'query': query, 'liked_song_ids': _liked_song_ids(request)}
    if query:
        # Songs match on their own title OR their artist's name.
        results['songs'] = Song.objects.filter(
            Q(title__icontains=query) | Q(artist__name__icontains=query)
        ).select_related('artist')
        results['artists'] = Artist.objects.filter(name__icontains=query)
        results['albums'] = Album.objects.filter(title__icontains=query)
        results['genres'] = Genre.objects.filter(name__icontains=query)
        results['moods'] = Mood.objects.filter(mood_type__icontains=query)
    return render(request, 'mainapp/search.html', results)


def see_all(request):
    """Browse the whole catalog: every song plus all artists/albums/genres/moods."""
    return render(request, 'mainapp/see_all.html', {
        'all_songs': Song.objects.select_related('artist').all(),
        'artists': Artist.objects.all(),
        'albums': Album.objects.all(),
        'genres': Genre.objects.all(),
        'moods': Mood.objects.all(),
        'liked_song_ids': _liked_song_ids(request),
    })


def artist_detail(request, artist_id):
    """Dedicated artist page: their bio, albums, and every playable song."""
    artist = get_object_or_404(Artist, pk=artist_id)
    return render(request, 'mainapp/artist_detail.html', {
        'artist': artist,
        'albums': Album.objects.filter(artist=artist),
        'songs': Song.objects.filter(artist=artist).select_related('artist', 'album'),
        'liked_song_ids': _liked_song_ids(request),
    })


@login_required
def liked_songs(request):
    """The user's "Liked Songs" library."""
    favorites = (
        Favorite.objects.filter(user=request.user)
        .select_related('song', 'song__artist')
    )
    return render(request, 'mainapp/liked_songs.html', {
        'favorites': favorites,
        'liked_song_ids': _liked_song_ids(request),
    })


@login_required
@require_POST
def toggle_favorite(request, song_id):
    """Like/unlike a song. Returns the new state so the UI can update in place."""
    song = get_object_or_404(Song, pk=song_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, song=song)
    if not created:
        favorite.delete()
    return JsonResponse({'liked': created})


@require_POST
def mark_played(request, song_id):
    """Record that a song started playing, so it appears under "Recently played"."""
    song = get_object_or_404(Song, pk=song_id)
    if request.user.is_authenticated:
        entry, _ = RecentlyPlayed.objects.get_or_create(user=request.user, song=song)
        entry.save()  # bump played_at so the song moves to the top
    return JsonResponse({'ok': True})


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            auth_login(request, user)
            return redirect('index')
    return render(request, 'mainapp/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Send the user back where they were headed (e.g. /liked/).
            next_url = request.POST.get('next') or request.GET.get('next')
            return redirect(next_url if next_url else 'index')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'mainapp/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def create_playlist(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Playlist.objects.create(name=name, user=request.user)
            return redirect('index')
        messages.error(request, 'Playlist name cannot be empty.')
    return render(request, 'mainapp/create_playlist.html')
