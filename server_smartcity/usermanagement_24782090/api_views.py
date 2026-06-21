from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import User 
from .serializers import RegisterSerializer 
from drf_spectacular.utils import extend_schema


@extend_schema(exclude=True)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "message": "Registrasi akun Citizen berhasil dilakukan.",
            "user": serializer.data["username"]
        }, status=status.HTTP_201_CREATED)