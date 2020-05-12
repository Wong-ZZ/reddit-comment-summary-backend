from .models import Submissions
from .serializers import SubmissionSerializer
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

def submission_list(request):
    if request.method == 'GET':
        submissions = Submissions.objects.all()
        serializer = SubmissionSerializer(submissions, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        return HttpResponse(status=404)

def submission_detail(request, pk):
    try:
        submission = Submissions.objects.get(pk=pk)
    except Submissions.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = SubmissionSerializer(submission)
        return JsonResponse(serializer.data)
    else:
        return HttpResponse(status=404)
