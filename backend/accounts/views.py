from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import RegisterSerializer

# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "username": request.user.username,
            "email": request.user.email,
            "role": request.user.role
        })
    
class PromoteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'Admin':
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user.role = 'Admin'
        user.save()
        return Response({"message": f"User {user.username} has been promoted to admin."})