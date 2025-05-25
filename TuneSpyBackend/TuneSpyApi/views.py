import os
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .ml_model import process_audio_from_frontend
from django.conf import settings

@api_view(['POST'])
def recognize_audio(request):
    audio_file = request.FILES.get('audio_file')

    if not audio_file:
        return Response({
            'status': 'failure',
            'message': 'No audio file provided.'
        })

    # Save uploaded audio file temporarily
    ext = os.path.splitext(audio_file.name)[1].lower()
    temp_path = f"/tmp/{audio_file.name}"
    with open(temp_path, 'wb') as f:
        for chunk in audio_file.chunks():
            f.write(chunk)

    try:
        matched_song = process_audio_from_frontend(temp_path)

        if matched_song:
            return Response({
                'status': 'success',
                'song_name': matched_song.get("song_name"),
                'artist': matched_song.get("artist_name", "Unknown Artist"),
                'match_count': matched_song.get("match_count", 0)
            })
        else:
            return Response({
                'status': 'failure',
                'message': 'No matching song found.'
            })
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
