import librosa
import numpy as np
import hashlib
from scipy.ndimage import maximum_filter
from pydub import AudioSegment
import tempfile
import os
from pymongo import MongoClient
from collections import defaultdict, Counter

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

# === Updated Match Fingerprint Function === #
def match_fingerprint(input_fingerprints):
    if not input_fingerprints:
        return None

    input_hash_map = defaultdict(list)
    for fp in input_fingerprints:
        input_hash_map[fp["hash"]].append(fp["offset"])

    all_songs = songs_collection.find()
    best_match = None
    best_match_score = 0
    best_confidence = 0
    best_match_offset = None

    for song in all_songs:
        song_fingerprints = song.get("fingerprint", [])
        song_hash_map = defaultdict(list)
        for fp in song_fingerprints:
            song_hash_map[fp["hash"]].append(fp["offset"])

        offset_diff_counter = Counter()

        match_counter = 0

        for h in input_hash_map:
            if h in song_hash_map:
                for input_offset in input_hash_map[h]:
                    for song_offset in song_hash_map[h]:
                        offset_diff = song_offset - input_offset
                        offset_diff_counter[offset_diff] += 1
                        match_counter += 1

        if not offset_diff_counter:
            continue

        most_common_offset, most_common_count = offset_diff_counter.most_common(1)[0]
        confidence = most_common_count / len(input_fingerprints)

        MIN_MATCH_COUNT = 15
        MIN_CONFIDENCE = 0.15

        if most_common_count >= MIN_MATCH_COUNT and confidence >= MIN_CONFIDENCE:
            if most_common_count > best_match_score:
                best_match_score = most_common_count
                best_match = song
                best_confidence = confidence
                best_match_offset = most_common_offset

    if best_match:
        return {
            "song_name": best_match.get("song_name"),
            "artist_name": best_match.get("artist_name", "Unknown Artist"),
            "match_count": best_match_score,
            "offset_difference": best_match_offset,
            "confidence": round(best_confidence, 3)
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
        match_result = match_fingerprint(fingerprints)
        return match_result
    finally:
        # Delete temp WAV only if it was created
        if wav_path != audio_path and os.path.exists(wav_path):
            os.remove(wav_path)

# === Main test call example (local file) === #
if __name__ == "__main__":
    test_audio_path = "test_song.mp3"  # Replace with actual path uploaded from frontend
    result = process_audio_from_frontend(test_audio_path)
    if result:
        print(f"Matched Song: {result['song_name']} by {result['artist_name']}")
        print(f"Match Count: {result['match_count']}, Confidence: {result['confidence']:.2f}")
        print(f"Offset Difference: {result['offset_difference']}")
    else:
        print("No matching song found.")
