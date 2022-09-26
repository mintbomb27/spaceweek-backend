from userauth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField 


# class Result(models.Model):
#   result_id = models.CharField(max_length = 5 ,primary_key= True)
#   position_1 = models.ForeignKey(Participant,on_delete=models.CASCADE)
#   position_2 = models.ForeignKey(Participant,on_delete=models.CASCADE)
#   position_3 = models.ForeignKey(Participant,on_delete=models.CASCADE) 

class Event(models.Model):
    id = models.AutoField(primary_key= True)
    name = models.CharField(max_length=100)
    subname = models.CharField(max_length=100)
    description = models.TextField(null=True)
    rules = models.TextField()
    judging_criteria = models.TextField()
    #result = models.ForeignKey(Result, on_delete= models.CASCADE)     
    prize_reveal = models.BooleanField(default=False)
    prize_1 = models.IntegerField(null=True)
    prize_2 = models.IntegerField(null=True)
    prize_3 = models.IntegerField(null=True)
    type = models.CharField(max_length = 11, choices=[("Individual", "Individual"), ("Team", "Team")])
    eligible_genders = ArrayField(
            models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female")]),
            size=2
        )
    deadline = models.DateTimeField(null=True)
    file_submission = models.BooleanField(default=False)
    accepted_formats = ArrayField(
            models.CharField(max_length=10, choices=[("TIFF","TIFF"), ("JPEG", "JPEG"), ("PNG", "PNG"), ("JPG", "JPG")]),
            default=list
        )


class Participant(models.Model):
    participant_id = models.CharField(max_length= 10 ,primary_key=True)
    reg_no = models.CharField(max_length=15)
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    events = models.ManyToManyField(Event)
    remarks = models.CharField(max_length= 200)

class Teams(models.Model):
    team_id = models.CharField(max_length=5 ,primary_key=True)
    team_name = models.CharField(max_length=50)
    events = models.ManyToManyField(Event)
    members = models.ManyToManyField(Participant)

class Submission(models.Model):
    event = models.ForeignKey(Event,on_delete= models.CASCADE)
    participant = models.ForeignKey(Participant,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)
    file = models.TextField()
    