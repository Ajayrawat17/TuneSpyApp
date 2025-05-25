import os
import sys
import django
import librosa
import numpy as np
import hashlib
from scipy.ndimage import maximum_filter
from pydub import AudioSegment

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TuneSpyBackend.settings')
django.setup()

from TuneSpyApi.models import TuneSpyModel

PEAK_NEIGHBORHOOD_SIZE = 20
FAN_VALUE = 5
MAX_HASHES = 20000

def convert_to_wav(mp3_path):
    audio = AudioSegment.from_file(mp3_path)
    temp_wav = mp3_path + ".wav"
    audio.export(temp_wav, format="wav")
    return temp_wav

def generate_fingerprint(song_path):
    ext = os.path.splitext(song_path)[1].lower()
    if ext == ".mp3":
        wav_path = convert_to_wav(song_path)
        path_to_load = wav_path
    else:
        path_to_load = song_path

    y, sr = librosa.load(path_to_load, sr=None, mono=True)

    if ext == ".mp3":
        os.remove(wav_path)

    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    S_db = librosa.power_to_db(S, ref=np.max)

    local_max = maximum_filter(S_db, size=PEAK_NEIGHBORHOOD_SIZE)
    peaks = (S_db == local_max)
    peak_coords = np.argwhere(peaks)
    peak_coords = sorted(peak_coords, key=lambda x: x[1])

    fingerprints = []
    for i in range(len(peak_coords)):
        for j in range(1, FAN_VALUE):
            if i + j < len(peak_coords):
                f1, t1 = peak_coords[i]
                f2, t2 = peak_coords[i + j]
                dt = t2 - t1

                if 0 < dt <= 200:
                    hash_str = f"{f1}|{f2}|{dt}"
                    h = hashlib.sha1(hash_str.encode()).hexdigest()[:20]
                    fingerprints.append({"hash": h, "offset": int(t1)})

                if len(fingerprints) >= MAX_HASHES:
                    break
        if len(fingerprints) >= MAX_HASHES:
            break

    return fingerprints[:5000]  # limit size

def generate_fingerprints_from_folder(folder_path):
    for file in sorted(os.listdir(folder_path)):
        if file.lower().endswith((".mp3", ".wav", ".mpeg")):
            file_path = os.path.join(folder_path, file)
            print(f"🔍 Processing: {file}")
            try:
                fingerprints = generate_fingerprint(file_path)
                print(f"Fingerprint sample: {fingerprints[:3]}")  # Debug print

                tune = TuneSpyModel(
                    artist_name="Ajay",
                    song_name=file,
                    fingerprint=fingerprints,
                    album="Unknown"
                )
                tune.save()
                print(f"✅ Saved in DB: {file} | Fingerprints count: {len(fingerprints)}")

            except Exception as e:
                print(f" Error processing {file}: {e}")

if __name__ == "__main__":
    input_folder = "/home/ajay/songfolder"  # Change this to your folder path
    generate_fingerprints_from_folder(input_folder)
