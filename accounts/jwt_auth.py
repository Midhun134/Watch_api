from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from bson import ObjectId
from .models import CustomUser


class MongoEngineRefreshToken(RefreshToken):
    """
    Custom RefreshToken that handles ObjectId conversion
    """
    @classmethod
    def for_user(cls, user):
        """
        Generate token for mongoengine user with ObjectId
        """
        token = cls()
        # Convert ObjectId to string for JWT token
        token['user_id'] = str(user.id)
        return token


class MongoEngineJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication for mongoengine users
    Handles ObjectId conversion for user lookup
    """
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                raise InvalidToken('Token contained no recognizable user identification')
            
            # Convert string to ObjectId if needed
            if isinstance(user_id, str):
                try:
                    user_id = ObjectId(user_id)
                except Exception:
                    raise InvalidToken('Token contained invalid user identification')
            
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed('User not found', code='user_not_found')
        except Exception as e:
            raise AuthenticationFailed('User lookup failed', code='user_lookup_failed')
        
        if not user.is_active:
            raise AuthenticationFailed('User is inactive', code='user_inactive')
        
        return user

