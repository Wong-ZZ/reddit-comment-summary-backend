from django.urls import path
from my_app import views

urlpatterns = [
    path('submissions/<str:submission_id>/', views.submission_list),
    path('submission/<int:id>/', views.submission_detail)
]