from django.urls import path, include
from .views import *

urlpatterns = [
    path('',AllEventsView.as_view()),
    path('add/',CreateEventView.as_view()),
    path('profile/', MyProfileView.as_view(), name='profile'),
    path('submit/',CreateSubmissionView.as_view()),
    path('submissions/<event>/',GetSubmissionsView.as_view())
]