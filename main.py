import sounddevice as sd
import numpy as np
import pygame
import time
import sys

# --- CONFIGURATION ---
SOUND_FILE = "rain.mp3"  # Make sure this file exists in your folder!
SENSITIVITY = 0.015      # Lower = more sensitive to noise (Adjust this first!)
BASE_VOLUME = 0.2        # Normal volume (0.0 to 1.0)
MAX_VOLUME = 1.0         # Max masking volume
SMOOTH_FACTOR = 0.05     # How fast it fades (lower = slower/more natural)

# --- INITIALIZATION ---
pygame.mixer.init()
try:
    pygame.mixer.music.load(SOUND_FILE)
    pygame.mixer.music.play(-1) # -1 means loop forever
    pygame.mixer.music.set_volume(BASE_VOLUME)
except Exception as e:
    print(f"Error loading {SOUND_FILE}: {e}")
    sys.exit()

current_vol = BASE_VOLUME

def audio_callback(indata, frames, time_info, status):
    global current_vol
    
    # 1. Measure room volume (RMS)
    rms = np.sqrt(np.mean(indata**2))
    
    # 2. Determine target volume
    # If room noise is above threshold, we aim for MAX_VOLUME
    if rms > SENSITIVITY:
        target_vol = MAX_VOLUME
        # Visual feedback for testing
        status_msg = "🚨 MASKING ACTIVE"
    else:
        target_vol = BASE_VOLUME
        status_msg = "✅ ROOM QUIET   "

    # 3. Smooth the transition (The "Fade" effect)
    # This prevents the sound from 'snapping' and waking you up
    current_vol += (target_vol - current_vol) * SMOOTH_FACTOR
    pygame.mixer.music.set_volume(current_vol)

    # 4. Print a live dashboard
    bar = "█" * int(current_vol * 20)
    print(f"{status_msg} | Room Noise: {rms:.4f} | Masking Level: {bar:<20} {int(current_vol*100)}%", end='\r')

print("--- AuraMask Prototype Engine v1.0 ---")
print(f"Playing: {SOUND_FILE}")
print("Adjust SENSITIVITY if the masking triggers too easily or not at all.")
print("Press Ctrl+C to stop.")

try:
    with sd.InputStream(callback=audio_callback):
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopping AuraMask...")
    pygame.mixer.music.stop()
