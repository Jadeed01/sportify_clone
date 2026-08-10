/**
 * Spotify-style audio player.
 *
 * Any element with the class `song-item` and a `data-audio` attribute becomes
 * playable: clicking it loads the track into the shared <audio> element and
 * starts playback. The player bar (buttons, progress slider, volume) is driven
 * through stable ids so the same script works on every page.
 */

(function () {
  const audio = document.getElementById('main-audio-player');
  if (!audio) return; // not a page with a player

  // ---- shared UI element lookups -------------------------------------------
  const els = {
    playPause: document.querySelector('.playPause'),
    prev: document.querySelector('.anterior'),
    next: document.querySelector('.proximo'),
    shuffle: document.querySelector('.aleatorio'),
    repeat: document.querySelector('.repetir'),
    progress: document.querySelector('#barraDeProgresso input[type=range]'),
    currentTime: document.getElementById('current-time'),
    totalTime: document.getElementById('total-time'),
    volume: document.getElementById('volume-range'),
    mute: document.getElementById('btn-mute'),
    nowImage: document.getElementById('now-image'),
    nowTitle: document.getElementById('now-title'),
    nowArtist: document.getElementById('now-artist'),
  };

  // The ids of songs the current user has liked, injected by each template.
  const likedIds = new Set(window.LIKED_SONG_IDS || []);

  let queue = [];       // playable songs currently on the page
  let currentIndex = -1;
  let shuffle = false;
  let repeat = false;
  let previousVolume = 1;

  // Play / pause icons swapped into the play button while a track plays.
  const ICON_PLAY =
    '<svg role="img" height="24" width="24" viewBox="0 0 24 24">' +
    '<path d="M7.05 3.606l13.49 7.788a.7.7 0 010 1.212L7.05 20.394A.7.7 0 016 19.788V4.212a.7.7 0 011.05-.606z"></path></svg>';
  const ICON_PAUSE =
    '<svg role="img" height="24" width="24" viewBox="0 0 24 24">' +
    '<path d="M5.7 3a.7.7 0 00-.7.7v16.6a.7.7 0 00.7.7h2.6a.7.7 0 00.7-.7V3.7a.7.7 0 00-.7-.7H5.7zm10 0a.7.7 0 00-.7.7v16.6a.7.7 0 00.7.7h2.6a.7.7 0 00.7-.7V3.7a.7.7 0 00-.7-.7h-2.6z"></path></svg>';

  // ---- helpers -------------------------------------------------------------

  function formatTime(seconds) {
    if (!Number.isFinite(seconds)) return '00:00';
    seconds = Math.floor(seconds);
    const m = String(Math.floor(seconds / 60)).padStart(2, '0');
    const s = String(seconds % 60).padStart(2, '0');
    return `${m}:${s}`;
  }

  function csrfToken() {
    // The token lives either in a rendered {% csrf_token %} field or a cookie.
    const field = document.querySelector('input[name=csrfmiddlewaretoken]');
    if (field) return field.value;
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }

  // Report a played song to the server so it shows up under "Recently played".
  function markPlayed(id) {
    fetch(`/song/${id}/played/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken() },
      credentials: 'same-origin',
    }).catch(() => {});
  }

  // ---- liking --------------------------------------------------------------

  function setLiked(button, liked) {
    const songId = Number(button.dataset.like);
    if (liked) likedIds.add(songId);
    else likedIds.delete(songId);
    button.classList.toggle('active', liked);
    button.title = liked ? 'Remove from Liked Songs' : 'Add to Liked Songs';
  }

  function toggleLike(button) {
    const songId = Number(button.dataset.like);
    fetch(`/song/${songId}/like/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken() },
      credentials: 'same-origin',
    })
      .then((res) => {
        if (res.status === 403 || res.status === 401) {
          window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
          throw new Error('not logged in');
        }
        return res.json();
      })
      .then((data) => setLiked(button, data.liked))
      .catch(() => {});
  }

  // Every page shows like hearts inside song cards (and one next to the
  // current track); a single delegated listener handles them all.
  document.addEventListener('click', (event) => {
    const button = event.target.closest('[data-like]');
    if (button) {
      event.stopPropagation();
      toggleLike(button);
    }
  });

  // ---- playback ------------------------------------------------------------

  function updatePlayButton(playing) {
    if (!els.playPause) return;
    els.playPause.innerHTML = playing ? ICON_PAUSE : ICON_PLAY;
    els.playPause.classList.toggle('active', playing);
  }

  function loadSong(song, index) {
    currentIndex = index;
    audio.src = song.audio;
    audio.play().catch(() => {}); // browsers may block autoplay until a user gesture
    if (els.nowTitle) els.nowTitle.textContent = song.title;
    if (els.nowArtist) els.nowArtist.textContent = song.artist;
    if (els.nowImage) els.nowImage.src = song.image || '';

    // Keep the now-playing heart in sync with the liked state.
    const nowLike = document.querySelector('#musicaPlay [data-like]');
    if (nowLike) nowLike.dataset.like = song.id;
    if (nowLike) setLiked(nowLike, likedIds.has(Number(song.id)));

    document.querySelectorAll('.song-item').forEach((item, i) => {
      item.classList.toggle('playing', i === index);
    });
    markPlayed(song.id);
  }

  function playIndex(index) {
    if (!queue.length) return;
    loadSong(queue[index], index);
  }

  function nextTrack() {
    if (!queue.length) return;
    if (shuffle) {
      playIndex(Math.floor(Math.random() * queue.length));
    } else {
      playIndex((currentIndex + 1) % queue.length);
    }
  }

  function prevTrack() {
    if (!queue.length) return;
    // Restart the current track if it has already been playing for a while,
    // otherwise jump to the previous one.
    if (audio.currentTime > 3) {
      audio.currentTime = 0;
      return;
    }
    playIndex((currentIndex - 1 + queue.length) % queue.length);
  }

  // Clicking anywhere on a song card (that isn't a button) plays that song.
  document.addEventListener('click', (event) => {
    const card = event.target.closest('.song-item');
    if (!card || event.target.closest('button')) return;
    const items = Array.from(document.querySelectorAll('.song-item'));
    queue = items.map(toSong);
    playIndex(items.indexOf(card));
  });

  function toSong(item) {
    return {
      id: item.dataset.id,
      title: item.dataset.title,
      artist: item.dataset.artist,
      audio: item.dataset.audio,
      image: item.dataset.image || '',
    };
  }

  // ---- control wiring ------------------------------------------------------

  if (els.playPause) {
    els.playPause.addEventListener('click', () => {
      if (!audio.src) return; // nothing loaded yet
      if (audio.paused) audio.play();
      else audio.pause();
    });
  }
  if (els.next) els.next.addEventListener('click', nextTrack);
  if (els.prev) els.prev.addEventListener('click', prevTrack);

  if (els.shuffle) {
    els.shuffle.addEventListener('click', () => {
      shuffle = !shuffle;
      els.shuffle.classList.toggle('active', shuffle);
    });
  }
  if (els.repeat) {
    els.repeat.addEventListener('click', () => {
      repeat = !repeat;
      els.repeat.classList.toggle('active', repeat);
    });
  }

  // Progress bar: update while playing, and seek when the user drags it.
  if (els.progress) {
    audio.addEventListener('timeupdate', () => {
      if (!els.progress.dataset.seeking) {
        els.progress.value = audio.currentTime;
        els.currentTime.textContent = formatTime(audio.currentTime);
      }
    });
    audio.addEventListener('loadedmetadata', () => {
      els.progress.max = audio.duration || 0;
      els.totalTime.textContent = formatTime(audio.duration);
    });
    els.progress.addEventListener('input', () => {
      els.progress.dataset.seeking = true;
      audio.currentTime = Number(els.progress.value);
      els.currentTime.textContent = formatTime(audio.currentTime);
    });
    els.progress.addEventListener('change', () => {
      delete els.progress.dataset.seeking;
    });
  }

  // Volume slider + mute button (shared across all pages).
  if (els.volume) {
    els.volume.addEventListener('input', (e) => {
      const value = parseFloat(e.target.value);
      audio.volume = value;
      audio.muted = value === 0;
    });
  }
  if (els.mute) {
    els.mute.addEventListener('click', () => {
      if (audio.muted) {
        audio.muted = false;
        audio.volume = previousVolume || 0.5;
        els.volume.value = audio.volume;
      } else {
        previousVolume = audio.volume;
        audio.muted = true;
        els.volume.value = 0;
      }
    });
  }

  // Fullscreen mode for the player controls (only present on the home footer).
  const btnFullScreen = document.getElementById('full-screen');
  if (btnFullScreen) {
    btnFullScreen.addEventListener('click', () => {
      const container = document.getElementById('configAudio');
      if (!document.fullscreenElement && container) {
        const enter = container.requestFullscreen || container.webkitRequestFullscreen;
        if (enter) enter.call(container);
      } else if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    });
  }

  // Play/pause state changes always refresh the button icon.
  audio.addEventListener('play', () => updatePlayButton(true));
  audio.addEventListener('pause', () => updatePlayButton(false));

  // When a track finishes, either repeat it or advance to the next one.
  audio.addEventListener('ended', () => {
    if (repeat) audio.currentTime = 0;
    else nextTrack();
  });
})();
