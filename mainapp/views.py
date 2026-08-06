from django.http import request
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Artist, Album, Genre, Mood, Song, Playlist, Favorite



def index(request):
    artists = Artist.objects.all()
    albums = Album.objects.all()
    generes = Genre.objects.all()
    songs = Song.objects.all()
    playlists = Playlist.objects.all()
    favorites = Favorite.objects.all()
    moods = Mood.objects.all()
    songs = Song.objects.all()
    context = {
        'artists': artists,
        'albums': albums,
        'genres': generes,
        'songs': songs,
        'playlists': playlists,
        'favorites': favorites,
        'moods': moods,
        'songs': songs
    }
    return render(request, 'mainapp/index.html', context)

def search(request):
    query = request.GET.get('q', '')
    songs = Song.objects.filter(title__icontains=query) if query else []
    artists = Artist.objects.filter(name__icontains=query) if query else []
    return render(request, 'mainapp/search.html', {
        'query': query,
        'songs': songs,
        'artists': artists,
    })    
# Create your views here.
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')  # Redirect to the index page after successful login
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'mainapp/login.html')

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'mainapp/signup.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        auth_login(request, user)
        return redirect("index")
    
    return render(request, 'mainapp/signup.html')
def logout_view(request):
    logout(request)
    return redirect ('login')


@login_required
def index(request):
    playlists = Playlist.objects.filter(user=request.user)
    songs = Song.objects.all()[:6]
    return render(request, 'mainapp/index.html', {
        'playlists': playlists,
        'songs': songs,
    })


@login_required
def create_playlist(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Playlist.objects.create(name=name, user=request.user)
            return redirect('index')
    return render(request, 'mainapp/create_playlist.html')  

def see_all(request):
    all_songs = Song.objects.all()
    return render(request, 'mainapp/see_all.html', {'all_songs': all_songs})