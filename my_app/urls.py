from django.urls import path
from my_app import views

urlpatterns = [
    path('submissions/', views.submission_list),
    path('submissions/<int:pk>/', views.submission_detail),
]