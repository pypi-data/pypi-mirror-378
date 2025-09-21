#!/usr/bin/env python3

# Imports
import math
import numpy as np
import sounddevice as sd
import wave
import argparse

# 1 = long (3 unit)
# 0 = short (1 unit)
# 2 = silent (1 unit)

# Space between parts of same letter - 1 unit
# Space between letters - 3 units
# Space between words - 7 units

# Data
morseChart = {
    'a': [0, 1], 'b': [1, 0, 0, 0], 'c': [1, 0, 1, 0], 'd': [1, 0, 0],
    'e': [0], 'f': [0, 0, 1, 0], 'g': [1, 1, 0], 'h': [0, 0, 0, 0],
    'i': [0, 0], 'j': [0, 1, 1, 1], 'k': [1, 0, 1], 'l': [0, 1, 0, 0],
    'm': [1, 1], 'n': [1, 0], 'o': [1, 1, 1], 'p': [0, 1, 1, 0],
    'q': [1, 1, 0, 1], 'r': [0, 1, 0], 's': [0, 0, 0], 't': [1],
    'u': [0, 0, 1], 'v': [0, 0, 0, 1], 'w': [0, 1, 1], 'x': [1, 0, 0, 1],
    'y': [1, 0, 1, 1], 'z': [1, 1, 0, 0], '1': [0, 1, 1, 1, 1],
    '2': [0, 0, 1, 1, 1], '3': [0, 0, 0, 1, 1], '4': [0, 0, 0, 0, 1],
    '5': [0, 0, 0, 0, 0], '6': [1, 0, 0, 0, 0], '7': [1, 1, 0, 0, 0],
    '8': [1, 1, 1, 0, 0], '9': [1, 1, 1, 1, 0], '0': [1, 1, 1, 1, 1],
    ' ': [2, 2, 2, 2, 2, 2, 2], '&': [0, 1, 0, 0, 0], '\'': [0, 1, 1, 1, 1, 0],
    '@': [0, 1, 1, 0, 1, 0], ')': [1, 0, 1, 1, 0, 1], '(': [1, 0, 1, 1, 0],
    ':': [1, 1, 1, 0, 0, 0], ',': [1, 1, 0, 0, 1, 1], '=': [1, 0, 0, 0, 1],
    '!': [1, 0, 1, 0, 1, 1], '.': [0, 1, 0, 1, 0, 1], '-': [1, 0, 0, 0, 0, 1],
    '%': [1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1], '+': [0, 1, 0, 1, 0],
    '\"': [0, 1, 0, 0, 1, 0], '?': [0, 0, 1, 1, 0, 0], '/': [1, 0, 0, 1, 0]
}

# =========================
# === ARGUEMENT PARSING ===
# =========================
parser = argparse.ArgumentParser(
    description="Convert text to morse code, play it, and save it to a WAV file",
    usage="%(prog)s {-i | -o <filename> <text>}"
)

group = parser.add_mutually_exclusive_group(required=True)

group.add_argument(
    "-i", "--interactive", action="store_true",
    help="Run in interactive mode to prompt for input."
)

group.add_argument(
    "-o",
    "--output",
    nargs=2,
    metavar=('<filename>', '<text>'),
    help="Provide a filename and text directly."
)

args = parser.parse_args()
interactive = args.interactive
text = ""
file_name = ""

if interactive:
    text = input("Enter text to convert to morse code: ")
    file_name = input("Enter a filename to save the WAV file (e.g., 'morse_code.wav'): ")
else:
    file_name = args.output[0]
    text = args.output[1]

# ============================
# === CONVERSION FUNCTIONS ===
# ============================

def ConvertToMorse(text: str):
    """
    Converts a string to arrays of morse code signals for processing
    Args:
        text (str): The text to convert
    Returns:
        list[int]
    """
    data = []
    for char in text.lower():
        if char in morseChart:
            data.extend(morseChart[char])
            if char != ' ':  data.extend([2, 2, 2])
        else: pass

    return data

# =========================
# === ENVELOPE FUNCTION ===
# =========================

def apply_envelope(signal, window_size_ratio=0.1):
    """
    Applies a Hann window envelope to a signal to minimize clicks.
    
    Args:
        signal (np.ndarray): The input audio signal.
        window_size_ratio (float): The ratio of the signal length to use for the fade-in/out.
    
    Returns:
        np.ndarray: The enveloped signal.
    """
    signal_length = len(signal)
    window_length = int(signal_length * window_size_ratio)
    
    if window_length == 0: return signal
    
    # Create the Hann window
    window = np.hanning(2 * window_length)
    
    # Split the window into fade-in and fade-out parts
    fade_in = window[:window_length]
    fade_out = window[window_length:]
    
    # Create the full envelope array
    envelope = np.ones(signal_length)
    envelope[:window_length] = fade_in
    envelope[signal_length - window_length:] = fade_out
    
    return signal * envelope

# ======================================
# === VARIABLES FOR SOUND GENERATION ===
# ======================================
frequency = 440
sample_rate = 44100
duration = 0.06
amplitude = 0.5

t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
sine_wave = (amplitude * np.sin(2 * math.pi * frequency * t)).astype(np.float32)

silent_wave = np.zeros(int(sample_rate * duration), dtype=np.float32)

data = ConvertToMorse(text)
full_audio_data = []

print("Generating audio data...")

# Apply the envelope to the base sine wave
enveloped_sine_wave = apply_envelope(sine_wave)

# ================================
# === FINAL CONTENT GENERATION ===
# ================================

for i in data:
    if i == 0:
        full_audio_data.append(enveloped_sine_wave)
        full_audio_data.append(silent_wave)
    elif i == 1:
        # Create a longer enveloped tone by concatenating
        long_tone_duration = duration * 3
        t_long = np.linspace(0, long_tone_duration, int(sample_rate * long_tone_duration), endpoint=False)
        long_sine_wave = (amplitude * np.sin(2 * math.pi * frequency * t_long)).astype(np.float32)
        enveloped_long_tone = apply_envelope(long_sine_wave)

        full_audio_data.append(enveloped_long_tone)
        full_audio_data.append(silent_wave)
    elif i == 2:
        full_audio_data.append(silent_wave)

# Concatenate all segments into one large array
combined_audio = np.concatenate(full_audio_data)


# ================
# === SAVE WAV ===
# ================
print(f"Saving to {file_name}...")
with wave.open(file_name, 'wb') as wavfile:
    wavfile.setnchannels(1)
    wavfile.setsampwidth(combined_audio.astype(np.int16).dtype.itemsize)
    wavfile.setframerate(sample_rate)
    wavfile.writeframes((combined_audio * 32767).astype(np.int16).tobytes())

print(f"Morse code audio has been saved to {file_name}")

# ================
# === PLAY WAV ===
# ================
print("Playing the saved audio...")
sd.play(combined_audio, sample_rate)
sd.wait()