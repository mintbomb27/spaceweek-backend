from rest_framework import generics
from thanimaBackend.helpers import GenericResponse
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from userauth.models import Registration

class EntryCheckView(generics.GenericAPIView):
    permission_classes=[IsAdminUser]

    def get(self, request, *args, **kwargs):
        reg_no = request.GET.get('reg_no', None)
        if reg_no is None:
            raise Exception(422,"Please provide Registration Number")
        try:
            user = Registration.objects.get(reg_no=reg_no)
            return GenericResponse("Entry Accepted",{"entry": True})

        except Exception as e:
            return GenericResponse("",{"entry": False})
class HadFood(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    def get(self,request,*args,**kwargs):
        reg_no = request.GET.get('reg_no', None)
        if reg_no is None:
            raise Exception(422,"Please provide Registration Number")
        try:
            registration = Registration.objects.get(reg_no=reg_no)
            if registration.payment_done == True:
                if registration.had_food == False:
                    registration.had_food = True
                    registration.save()
                    return GenericResponse("Entry Accepted",{"entry": True})
                else:
                    return GenericResponse("Had food",{"entry":False})
            else:
                return GenericResponse("Payment not done",{"entry": False})
        except Exception as e:
            return GenericResponse("Not registered in VIT portal",{"entry": False})