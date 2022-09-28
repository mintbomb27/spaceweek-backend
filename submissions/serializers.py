from dataclasses import field
from .models import Event, Participant, School, Team
from rest_framework import serializers

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class EventDashSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id','name','image','date','time','location']

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id','name','standard','gender']

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'