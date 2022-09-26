from asyncio import exceptions
import traceback
import random
import urllib
import os
from rest_framework.renderers import JSONRenderer
from rest_framework import exceptions
from rest_framework.exceptions import ErrorDetail
from django.forms import ValidationError
from dotenv import load_dotenv
from rest_framework.response import Response
import string

from thanimaBackend.helpers import GenericResponse

load_dotenv()

def otp_msg(otp):
    msg = f"Dear User,\nYour OTP to login is {otp}. It will be valid for next 10 minutes. Please do not share with anyone. - Thanima 2022"
    return msg

def create_otp():
    return random.randint(100000, 999999)

def exc_handler(exc, context):
    status = 400
    message = 'Unknown Error'
    detail = 'none'
    try:
        if(type(eval(str(exc))) is tuple):
            try:
                err_resp = eval(str(exc))
                if(err_resp[0]):
                    status = err_resp[0]
                message = err_resp[1]
                detail = err_resp[2]
            except Exception as e:
                if detail == 'none':
                    if message is not None and message != '':
                        detail = message
        elif type(exc) is exceptions.ValidationError:
            errors = []
            for errs in eval(str(exc)).values():
                for err in errs:
                    errors.append(str(err))
            message = 'Validation Error'
            detail = errors
        else:
            message = str(exc)
    except Exception as e:
        message = str(exc)
    print(traceback.print_exc())
    return GenericResponse(message,{
        'message':message,
        'detail':detail
    }, status=status)

def generate_password():
    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
    length = random.randint(8,12)
    random.shuffle(characters)
    password = []
    for _ in range(length):
        password.append(random.choice(characters))
    random.shuffle(password)
    return "".join(password)