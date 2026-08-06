// DOM Elements
const audioPlayer = document.getElementById('main-audio-player');
const volumeRange = document.getElementById('volume-range');
const btnMute = document.getElementById('btn-mute');
const btnFullScreen = document.getElementById('full-screen');

let previousVolume = 1;

// 1. Sync Volume Slider with Audio Player
volumeRange.addEventListener('input', (e) => {
  const val = parseFloat(e.target.value);
  audioPlayer.volume = val;
  audioPlayer.muted = (val === 0);
});

// 2. Mute / Unmute Toggle Button
btnMute.addEventListener('click', () => {
  if (audioPlayer.muted) {
    audioPlayer.muted = false;
    audioPlayer.volume = previousVolume || 0.5;
    volumeRange.value = audioPlayer.volume;
  } else {
    previousVolume = audioPlayer.volume;
    audioPlayer.muted = true;
    volumeRange.value = 0;
  }
});

// 3. Fullscreen Controller
btnFullScreen.addEventListener('click', () => {
  const playerContainer = document.getElementById('configAudio');
  if (!document.fullscreenElement) {
    if (playerContainer.requestFullscreen) {
      playerContainer.requestFullscreen();
    } else if (playerContainer.webkitRequestFullscreen) {
      playerContainer.webkitRequestFullscreen();
    }
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  }
});

// 4. Toggle function for SVG icon clicks
function enabledisable(element) {
  element.classList.toggle('active');
}