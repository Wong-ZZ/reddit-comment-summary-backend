from .models import Submissions
from .serializers import SubmissionSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def submission_list(request):
    if request.method == 'GET':
        submissions = Submissions.objects.all()
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def submission_detail(request, pk):
    try:
        submission = Submissions.objects.get(pk=pk)
    except Submissions.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SubmissionSerializer(submission)
        return Response(serializer.data)
