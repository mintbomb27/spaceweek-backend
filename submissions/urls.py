from django.urls import path, include
from .views import *

urlpatterns = [
    path('all/',AllEventsView.as_view()),
    path('',DetailView.as_view()),
    path('add/',CreateEventView.as_view()),
    path('participant/',ParticipantView.as_view()),
    path('participants/',ParticipantsView.as_view()),
    path('dashboard/',DashboardView.as_view())
    # path('profile/', MyProfileView.as_view(), name='profile'),
    # path('submissions/<event>/',GetSubmissionsView.as_view())
]