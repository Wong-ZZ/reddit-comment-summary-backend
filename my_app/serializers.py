from rest_framework import serializers
from .models import Submissions

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submissions
        fields = ['id', 'title', 'poster', 'subreddit', 'queried_at']
