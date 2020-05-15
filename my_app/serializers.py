from rest_framework import serializers
from .models import Submissions

class SubmissionSerializer(serializers.ModelSerializer):
    past_queries = serializers.SerializerMethodField()

    class Meta:
        model = Submissions
        fields = [
            'id', 'title', 'poster', 'subreddit', 'queried_at',
            'submission_id', 'wordcloud_url', 'num_comments', 'past_queries'
        ]

    def get_past_queries(self, obj):
        past_queries = list(Submissions.objects.filter(submission_id=obj.submission_id))
        def get_past_query_info(query):
            return {'queried_at': query.queried_at, 'id': query.id}
        past_queries_info = map(get_past_query_info, past_queries)
        return past_queries_info

