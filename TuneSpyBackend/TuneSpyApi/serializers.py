from rest_framework import serializers
from .models import TuneSpyModel

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = TuneSpyModel
        fields = '__all__'
