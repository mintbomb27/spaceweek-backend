from rest_framework import serializers
from django.core import exceptions
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from dj_rest_auth.serializers import LoginSerializer
from datetime import datetime
import re

from submissions.models import Participant

GENDER_CHOICES = [('Male','Male'),('Female','Female'),('Other','Other')]

class CustomRegisterSerializer(serializers.Serializer):
    contact = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True, allow_blank=False)
    name = serializers.CharField(required=True, allow_blank=False, max_length=128)
    password = serializers.CharField(required=True, allow_blank=False, max_length=128)
    
    def user_exists(self):
        email = self.validated_data.get('email', None)
        contact = self.validated_data.get('contact', None)
        UserModel = get_user_model()
        if contact is not None and contact != '':
            try:
                user = UserModel.objects.get(contact=contact)
                return user
            except UserModel.DoesNotExist:
                if email is not None and email != '':
                    try:
                        user = UserModel.objects.get(email=email)
                        return user
                    except UserModel.DoesNotExist:
                        return None
                else:
                    return None
        else:
            return None

    def validate_user(self):
        password = self.validated_data.get('password', None)
        contact = self.validated_data.get('contact', None)
        email = self.validated_data.get('email', None)

        #Input Validation
        pass_rx = '^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*]).{8,}$'
        if(password is not None and re.search(pass_rx,password) is None):
            raise Exception(422, 'Password should contain a lowercase, an uppercase character, a number, and a special character.')
        if(contact and len(str(contact)) < 10):
            raise Exception(422, 'Invalid Phone Number')

        #DB Checks
        UserModel = get_user_model()
        if contact is not None and contact != '':
            try:
                user = UserModel.objects.get(contact=contact, reg_complete=True)
                raise Exception('contact already exists')
            except UserModel.DoesNotExist:
                if email is not None and email != '':
                    try:
                        user = UserModel.objects.get(email=email, email_verified=True, reg_complete=True)
                        raise Exception('email already exists')
                    except UserModel.DoesNotExist:
                        return True
                else:
                    return True
        else:
            raise Exception('contact is not provided')
        
    def create(self, validated_data):
        User = get_user_model()

        name = validated_data.get('name', None)
        password = validated_data.get('password', None)
        email = validated_data.get('email', None)
        contact = validated_data.get('contact', None)
        user = User(name=name, password=password,email=email,contact=contact)
        return User.objects.create(**validated_data)

class CustomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.CharField(required=False, allow_blank=False)
    password = serializers.CharField(required=False, allow_blank=False, style={'input_type': 'password'})

    def get_auth_user_using_allauth(self, username, email, password):
        return self.authenticate(email=email, password=password)

class OTPSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True, allow_blank=False, max_length=6)
    email = serializers.CharField(required=True, allow_blank=False, max_length=128)
    
    def create_participant(self, user):
        last = Participant.objects.all().order_by('participant_id').last()
        if not last:
            pid = 'TMAP0001'
        else:
            last_id = int(last.split('P'))
            pid = 'TMAP' + str(last_id+1).zfill(4)
        participant = Participant(user=user,participant_id=pid,reg_no=user.reg_no)
        participant.save()

    def _validate_otp(self, otp, email):
        if otp and email:
            UserModel = get_user_model()
            user = UserModel.objects.get(email=email)
            if user is None:
                raise exceptions.ObjectDoesNotExist(_('User does not exist.'))
            time_diff = user.otp_validity.replace(tzinfo=None) - datetime.now()
            if(time_diff.seconds <= 600): # otp valid
                if(user.otp == otp):
                    if(user.email_verified == False):
                        user.email_verified = True
                        user.reg_complete = True
                        user.save()
                        # Create Participant Automatically
                        self.create_participant(user)
                    return user
                else:
                    raise exceptions.PermissionDenied(_('Invalid OTP'))
            else:
                raise exceptions.PermissionDenied(_('OTP Timed Out'))
        else:
            raise exceptions.BadRequest(_('Both "otp" and "email" should be provided.'))
    
    def validate(self, attrs):
        otp = attrs.get('otp')
        email = attrs.get('email')
        user = self._validate_otp(otp, email)
        attrs['user'] = user
        return attrs
