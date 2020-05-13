from .models import Submissions
from .serializers import SubmissionSerializer
from .utils import fetch
import re
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def submission_list(request):
    if request.method == 'GET':
        submissions = Submissions.objects.all()
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

@api_view(['GET', 'POST'])
def submission_detail(request, submission_id):
    if request.method == 'GET':
        try:
            submission = Submissions.objects.get(submission_id=submission_id)
        except Submissions.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SubmissionSerializer(submission)
        return Response(serializer.data)

    elif request.method == 'POST':
        resp = fetch(submission_id)
        if 'sha256' in resp:
            submission = Submissions.objects.get(sha256=resp['sha256'])
            serializer = SubmissionSerializer(submission)
            return Response(serializer.data)
        elif resp is 'duplicate key':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

