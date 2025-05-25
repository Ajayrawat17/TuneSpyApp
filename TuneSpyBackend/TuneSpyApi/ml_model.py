import librosa
import numpy as np
import hashlib
from scipy.ndimage import maximum_filter
from pydub import AudioSegment
import tempfile
import os
from pymongo import MongoClient

# === Constants === #
PEAK_NEIGHBORHOOD_SIZE = 20
FAN_VALUE = 5
MAX_HASHES = 20000

# === MongoDB Atlas Connection === #
mongo_uri = "mongodb+srv://Ajay7983:Ajay7983%40@tunespyapp.ymufret.mongodb.net/?retryWrites=true&w=majority&appName=TuneSpyApp"
client = MongoClient(mongo_uri)
db = client['tunecollection']
songs_collection = db['songs']

# === Convert MPEG to WAV === #
def convert_mpeg_to_wav(mpeg_path):
    try:
        sound = AudioSegment.from_file(mpeg_path)
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        sound.export(temp_wav.name, format="wav")
        return temp_wav.name
    except Exception as e:
        print(f"[ERROR] Failed to convert MPEG to WAV: {e}")
        return None

# === Generate Fingerprint from Audio === #
def generate_fingerprint(audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=None, mono=True)
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
        S_db = librosa.power_to_db(S, ref=np.max)

        local_max = maximum_filter(S_db, size=PEAK_NEIGHBORHOOD_SIZE)
        peaks = (S_db == local_max)
        peak_coords = np.argwhere(peaks)
        peak_coords = sorted(peak_coords, key=lambda x: x[1])  # sort by time

        fingerprints = []
        for i in range(len(peak_coords)):
            for j in range(1, FAN_VALUE):
                if i + j < len(peak_coords):
                    f1 = peak_coords[i][0]
                    t1 = peak_coords[i][1]
                    f2 = peak_coords[i + j][0]
                    t2 = peak_coords[i + j][1]
                    dt = t2 - t1

                    if 0 < dt <= 200:
                        hash_str = f"{f1}|{f2}|{dt}"
                        h = hashlib.sha1(hash_str.encode()).hexdigest()[:20]
                        fingerprints.append({
                            "hash": h,
                            "offset": int(t1)
                        })

                    if len(fingerprints) >= MAX_HASHES:
                        break
            if len(fingerprints) >= MAX_HASHES:
                break

        return fingerprints
    except Exception as e:
        print(f"[ERROR] Fingerprint generation failed: {e}")
        return None

# === Match Fingerprint with MongoDB === #
def match_fingerprint(input_fingerprints):
    if not input_fingerprints:
        return None

    input_hashes = set(fp["hash"] for fp in input_fingerprints)
    all_songs = songs_collection.find()

    best_match = None
    best_match_count = 0

    for song in all_songs:
        db_hashes = set(fp["hash"] for fp in song.get("fingerprint", []))
        common_hashes = input_hashes.intersection(db_hashes)
        count = len(common_hashes)

        if count > best_match_count:
            best_match_count = count
            best_match = song

    if best_match and best_match_count > 5:
        return {
            "song_name": best_match.get("song_name"),
            "artist_name": best_match.get("artist_name", "Unknown Artist"),
            "match_count": best_match_count
        }
    else:
        return None

# === Process Audio File Uploaded from Frontend === #
def process_audio_from_frontend(audio_path):
    ext = os.path.splitext(audio_path)[1].lower()
    wav_path = convert_mpeg_to_wav(audio_path) if ext in [".mp3", ".mpeg", ".mp4"] else audio_path

    if not wav_path or not os.path.exists(wav_path):
        print("[ERROR] Failed to prepare audio file.")
        return None

    try:
        fingerprints = generate_fingerprint(wav_path)
        return match_fingerprint(fingerprints)
    finally:
        # Delete temp WAV only if it was created
        if wav_path != audio_path and os.path.exists(wav_path):
            os.remove(wav_path)
