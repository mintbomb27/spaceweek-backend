from userauth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField 

# class Result(models.Model):
#   result_id = models.CharField(max_length = 5 ,primary_key= True)
#   position_1 = models.ForeignKey(Participant,on_delete=models.CASCADE)
#   position_2 = models.ForeignKey(Participant,on_delete=models.CASCADE)
#   position_3 = models.ForeignKey(Participant,on_delete=models.CASCADE) 

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    guidelines = models.TextField()
    #result = models.ForeignKey(Result, on_delete= models.CASCADE)
    eligibility = ArrayField(
            models.CharField(max_length=10, choices=[("1","1"), ("2","2"), ("3","3"), ("4","4"), ("5","5"), ("6","6"), ("7","7"), ("8","8"), ("9","9"), ("10","10"), ("11","11"), ("12","12"), ("College","College"),]),
            size=13
        )
    location = models.CharField(max_length=128)
    image = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    max_per_school = models.IntegerField(default=5)
    type = models.CharField(max_length = 11, choices=[("Individual", "Individual"), ("Team", "Team")])
    eligible_genders = ArrayField(
            models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female")]),
            size=2
        )
    deadline = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

class School(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    poc = models.ForeignKey(User,on_delete= models.CASCADE)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Participant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    standard = models.CharField(max_length=10, choices=[("1","1"), ("2","2"), ("3","3"), ("4","4"), ("5","5"), ("6","6"), ("7","7"), ("8","8"), ("9","9"), ("10","10"), ("11","11"), ("12","12"), ("College","College"),])
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
    school = models.ForeignKey(School,on_delete= models.CASCADE)
    event = models.ForeignKey(Event,on_delete= models.CASCADE)
    remarks = models.CharField(null=True,max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.event.name+':'+ self.name
