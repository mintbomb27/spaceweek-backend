from uuid import uuid4
from dj_rest_auth.views import LoginView
from dj_rest_auth.models import get_token_model
from dj_rest_auth.utils import jwt_encode
from rest_framework.response import Response
from dj_rest_auth.app_settings import create_token
from rest_framework import generics
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from submissions.serializers import SubmissionSerializer
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

class RootView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'portal/login.html'

    def get_template(self):
        if(self.request.user.is_authenticated):
            return 'portal/dashboard.html'
        else:
            return 'portal/login.html'
    
    def get(self, request, *args, **kwargs):
        return Response({})

class CustomRegisterView(generics.GenericAPIView):
    serializer_class = CustomRegisterSerializer

    def create_participant(self, user):
        last = Participant.objects.all().order_by('participant_id').last()
        if not last:
            pid = 'TMAP0001'
        else:
            last_id = int(last.participant_id.split('P')[1])
            pid = 'TMAP' + str(last_id+1).zfill(4)
        participant = Participant(user=user,participant_id=pid,reg_no=user.reg_no)
        print(participant)
        participant.save()

    def post(self, request, *args, **kwargs):
        user_data = self.get_serializer(data=request.data)
        user_data.is_valid(raise_exception=True)
        if(user_data.validate_user()):
            otp = create_otp()
            email = user_data.validated_data.get('email', None)
            password = user_data.validated_data.get('password', None)
            otp_validity = datetime.now() + timedelta(minutes=10)
            user = user_data.user_exists()
            if user is not None:
                if user.otp_validity:
                    time_diff = user.otp_validity.replace(tzinfo=None) - datetime.now()
                # if time_diff.seconds > 480 and time_diff.seconds < 600:
                #     raise Exception(429, 'otp already requested in last 2 minutes.')
                user.otp = otp
                user.password = make_password(password)
                user.otp_validity = otp_validity
                user.email_verified = True
                user.reg_complete = True
                user.save()
                self.create_participant(user)
            else:
                user = user_data.save(otp=otp, otp_validity=otp_validity, password=make_password(password))
                self.create_participant(user)
            # send_mail('Verification Mail for spaceweek Portal', otp_msg(otp), None, recipient_list=[email], fail_silently=True)
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
        send_mail('Forgot Password Request for  Portal', otp_msg(otp), None, recipient_list=[user.email], fail_silently=True)
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

class UploadRegistrations(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file is None:
                raise Exception(400, "file not passed")
        ext = file.name.split('.')[-1]
        if(ext in ['xls','xlsx']):
            filename = f"{uuid4()}.{ext}"
            dirr = default_storage.save(filename, file)
            wb = load_workbook(dirr)
            registrations = []
            for sheet in wb:
                for row in sheet.iter_rows(min_row=1, max_col=5, max_row=2000, values_only=True):
                    if not row[0]:
                        break
                    if str(row[1]) == 'Name':
                        continue
                    receipt = row[0]
                    name = row[1]
                    reg_no = row[2]
                    email = row[3]
                    contact = row[4]
                    if(len(reg_no) >= 10):
                        reg_no = reg_no.replace(' ', '')
                    # if(len(str(contact)) >= 10):
                    #     contact = str(contact).replace(' ', '')
                    # print(name, reg_no, email, contact)
                    registration = Registration(receipt=receipt, name=name, reg_no=reg_no, email=email, mobile_no=contact)
                    registrations.append(registration)
            Registration.objects.bulk_create(registrations, ignore_conflicts=True)
            delete = default_storage.delete(dirr)
            return GenericResponse("created users", "Success")
        else:
            raise Exception(400, "Invalid file")