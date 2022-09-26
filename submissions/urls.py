from django.urls import path, include
from .views import *

urlpatterns = [
    path('all/',AllEventsView.as_view()),
    path('',EventView.as_view()),
    path('add/',CreateEventView.as_view()),
    path('register/',RegisterForEventView.as_view()),
    # path('profile/', MyProfileView.as_view(), name='profile'),
    # path('submissions/<event>/',GetSubmissionsView.as_view())
]