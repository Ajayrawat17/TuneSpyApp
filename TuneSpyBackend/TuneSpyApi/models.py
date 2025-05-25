from django.db import models

class TuneSpyModel(models.Model):
    artist_name = models.CharField(max_length=255)
    song_name = models.CharField(max_length=255)
    fingerprint = models.JSONField(blank=True, null=True)  # Store fingerprint as JSON
    album = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.song_name} by {self.artist_name}"
