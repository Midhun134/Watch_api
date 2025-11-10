from django.contrib.auth.backends import BaseBackend
from .models import CustomUser


class MongoEngineBackend(BaseBackend):
    """
    Custom authentication backend for mongoengine users
    """
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None:
            email = kwargs.get('email')
        if email is None or password is None:
            return None
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return None
        
        if user.check_password(password) and user.is_active:
            # Update last_login
            from datetime import datetime
            user.last_login = datetime.utcnow()
            user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            # Try to get user by ObjectId string
            from bson import ObjectId
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            return CustomUser.objects.get(id=user_id)
        except (CustomUser.DoesNotExist, ValueError, TypeError):
            return None

