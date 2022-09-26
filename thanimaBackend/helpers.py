from rest_framework.response import Response

def GenericResponse(message, data, status = 200):
    return Response({
    "message": message,
    "data": data,
    "status": status }, status=status)