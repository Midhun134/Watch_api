from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from .jwt_auth import MongoEngineRefreshToken
from .models import CustomUser
import re

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # No authentication required
    def validate_password(self, password):
        # At least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return "Password must contain at least one uppercase letter."
        # At least one digit
        if not re.search(r'\d', password):
            return "Password must contain at least one number."
        if not re.search(r'[a-z]', password):
            return "Password must contain at least one lowercase letter."

        # At least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return "Password must contain at least one special character."
        # Minimum length (optional but recommended)
        if len(password) < 8:
            return "Password must be at least 8 characters long."
        return None
    

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate password complexity
        password_error = self.validate_password(password)
        if password_error:
            return Response(
                {"error": password_error},
                status=status.HTTP_400_BAD_REQUEST
            )

        if CustomUser.objects(email=email).first():
            return Response(
                {"error": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create user
        user = CustomUser.create_user(email=email, password=password)

        # Generate JWT tokens for the new user
        #refresh = RefreshToken.for_user(user)

        return Response(
             {
                 "message": "User created successfully",

             },
            status=status.HTTP_201_CREATED
        )
class LoginView(APIView):
    permission_classes = [AllowAny]  # No authentication required for login
    authentication_classes = []  # Disable JWT authentication on this endpoint

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens for the user
        refresh = MongoEngineRefreshToken.for_user(user)
        
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Login successful"
        })


# Create your views here.
