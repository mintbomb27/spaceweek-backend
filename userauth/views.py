from uuid import uuid4
from dj_rest_auth.views import LoginView
from dj_rest_auth.models import get_token_model
from dj_rest_auth.utils import jwt_encode
from rest_framework.response import Response
from dj_rest_auth.app_settings import create_token
from rest_framework import generics
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from submissions.models import School
from spaceweekBackend.helpers import GenericResponse
from userauth.utils import otp_msg, create_otp
from rest_framework.renderers import TemplateHTMLRenderer
from datetime import timedelta
from django.conf import settings
from userauth.serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from pathlib import Path
from openpyxl import *
from django.core.files.storage import default_storage
from django.db.utils import OperationalError
from django.db import connections

class RootView(APIView):
    def get(self, request, *args, **kwargs):
        db_conn = connections['default']
        try:
            c = db_conn.cursor()
        except OperationalError as e:
            return GenericResponse('DB Connection failed',str(e), status=500)
        else:
            return GenericResponse('Server is up!',"")

class CustomRegisterView(generics.GenericAPIView):
    serializer_class = CustomRegisterSerializer

    def create_participant(self, user):
        last = Participant.objects.all().order_by('participant_id').last()
        if not last:
            pid = 'SPWK000001'
        else:
            last_id = int(last.participant_id.split('P')[1])
            pid = 'SPWK' + str(last_id+1).zfill(6)
        participant = Participant(user=user,participant_id=pid,reg_no=user.reg_no)
        participant.save()

    def validate_user(self,email,contact,password):
        #Input Validation
        email_rx = "[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
        pass_rx = '^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*]).{8,}$'
        if(email is not None and re.search(email_rx, email) is None):
            raise Exception(422, 'Invalid email address')
        if(password is not None and re.search(pass_rx,password) is None):
            raise Exception(422, 'Password should be min. 8 characters, contain a lowercase, an uppercase, a number, and a special character.')
        if(contact and len(str(contact)) < 10):
            raise Exception(422, 'Invalid Phone Number')

        #DB Checks
        UserModel = get_user_model()
        if contact is not None and contact != '':
            try:
                user = UserModel.objects.get(contact=contact, reg_complete=True)
                raise Exception(400, 'contact already exists')
            except UserModel.DoesNotExist:
                if email is not None and email != '':
                    try:
                        user = UserModel.objects.get(email=email, email_verified=True, reg_complete=True)
                        raise Exception(400, 'email already exists')
                    except UserModel.DoesNotExist:
                        return True
                else:
                    return True
        else:
            raise Exception('contact is not provided')

    def post(self, request, *args, **kwargs):
        school_name = request.data.get('school_name', None)
        school_address = request.data.get('school_address', None)
        email = request.data.get('email', None)
        contact = request.data.get('contact', None)
        password = request.data.get('password', None)
        name = request.data.get('name', None)
        if(not(school_name and school_name.strip())):
            raise Exception(400, "School Name not provided")
        if(not(school_address and school_address.strip())):
            raise Exception(400, "School Address not provided")
        try:
            school = School.objects.get(name=school_name)
            raise Exception('400', 'school name already exists.')
        except School.DoesNotExist as e:
            pass
        if(self.validate_user(email, contact, password)):
            otp = create_otp()
            otp_validity = datetime.now() + timedelta(minutes=10)
            user = get_user_model()(name=name, contact=contact, email=email, otp=otp, otp_validity=otp_validity, password=make_password(password),email_verified=True, reg_complete=True)
            user.save()
            school = School(name=school_name, poc=user, address=school_address)
            school.save()
            # send_mail('Verification Mail for Thanima Portal', otp_msg(otp), None, recipient_list=[email], fail_silently=True)
            return GenericResponse('Registered. OTP Sent.','Success')

class OTPVerifyView(LoginView):
    serializer_class = OTPSerializer
    permission_classes = []

    def get_response(self):
        response = super().get_response()
        if response is not None:
            return GenericResponse("Logged in successfully", response.data)
        else:
            raise Exception(500, 'failed to create response')

    def login(self):
        self.user = self.serializer.validated_data['user']
        token_model = get_token_model()

        if getattr(settings, 'REST_USE_JWT', False):
            self.access_token, self.refresh_token = jwt_encode(self.user)
        elif token_model:
            self.token = create_token(token_model, self.user, self.serializer)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        self.login()
        return self.get_response()

class CustomLoginView(LoginView):
    serializer_class = CustomLoginSerializer
    permission_classes = []

    def get_response(self):
        response = super().get_response()
        if response is not None:
            return GenericResponse("Success", response.data)
        else:
            raise Exception(500, 'failed to create response')

    def post(self, request, *args, **kwargs):
        self.request = request

        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()

class ForgotPasswordRequest(generics.GenericAPIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        if email is None:
            raise Exception(422, 'email not passed')
        user = get_user_model().objects.get(email=email, reg_complete=True)
        if user.otp_validity:
            time_diff =  user.otp_validity.replace(tzinfo=None) - datetime.now()
            if time_diff.seconds > 480 and time_diff.seconds < 600:
                raise Exception(429, 'otp already requested in last 2 minutes.', 'too many requests')
        otp = create_otp()
        user.otp = otp
        user.otp_validity = datetime.now() + timedelta(minutes=10)
        send_mail('Forgot Password Request for Thanima Portal', otp_msg(otp), None, recipient_list=[user.email], fail_silently=True)
        user.save()
        return GenericResponse('OTP sent', '')

class VerifyForgotPasswordOTP(generics.GenericAPIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        otp = request.data.get('otp', None)
        if email is None:
            raise Exception('email not passed')
        if otp is None:
            raise Exception('otp not passed')
        user = get_user_model().objects.get(email=email, reg_complete=True)
        time_diff = user.otp_validity.replace(tzinfo=None) - datetime.now()
        if(time_diff.seconds <= 600): 
            if(user.otp == otp): # otp valid
                verification_id = uuid4()
                user.verification_id = verification_id
                user.verification_validity = datetime.now() + timedelta(minutes=15)
                user.save()
                return GenericResponse({'verification_id':verification_id}, '')
            else:
                raise Exception(403, 'Invalid OTP')
        else:
            raise Exception(403, 'OTP Timed Out')

class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        password = request.data.get('password', None)
        confirm_password = request.data.get('confirm_password', None)
        verification_id = request.data.get('verification_id', None)
        if password is None or confirm_password is None:
            raise Exception(400, 'passwords not passed')
        elif verification_id is None:
            raise Exception(400, 'verification_id not passed')
        if(password == confirm_password):
            user = get_user_model().objects.get(verification_id=verification_id, reg_complete=True)
            time_diff = user.verification_validity.replace(tzinfo=None) - datetime.now()
            if(time_diff.seconds < 900):
                user.password = make_password(password)
                user.save()
                return GenericResponse('password updated','')
            else:
                raise Exception(400, 'OTP expired', 'request OTP again.')
        else:
            raise Exception(422, 'passwords do not match.')