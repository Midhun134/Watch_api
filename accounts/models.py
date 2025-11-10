from mongoengine import Document, EmailField, StringField, BooleanField, DateTimeField
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime


class CustomUser(Document):
    """Mongoengine User Document for MongoDB storage"""
    email = EmailField(required=True, unique=True)
    password = StringField(required=True, max_length=128)
    first_name = StringField(max_length=30, blank=True)
    last_name = StringField(max_length=30, blank=True)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)
    date_joined = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField(null=True, blank=True)

    meta = {
        'indexes': ['email'],
        'index_background': True,
    }

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        """Set password hash"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check password"""
        return check_password(raw_password, self.password)

    @property
    def is_authenticated(self):
        """Always return True for authenticated users"""
        return True

    @property
    def is_anonymous(self):
        """Always return False for authenticated users"""
        return False

    def get_username(self):
        """Return the username (email)"""
        return self.email

    def has_perm(self, perm, obj=None):
        """Check if user has permission"""
        if self.is_superuser:
            return True
        return False

    def has_module_perms(self, app_label):
        """Check if user has module permissions"""
        if self.is_superuser:
            return True
        return False

    @classmethod
    def create_user(cls, email, password=None, **extra_fields):
        """Create a regular user"""
        if not email:
            raise ValueError("Email field is required")
        email = cls.normalize_email(email)
        user = cls(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    @classmethod
    def create_superuser(cls, email, password=None, **extra_fields):
        """Create a superuser"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return cls.create_user(email, password, **extra_fields)

    @staticmethod
    def normalize_email(email):
        """Normalize email address"""
        return email.lower().strip()

    def save(self, *args, **kwargs):
        """Override save to update last_login if needed"""
        if not self.date_joined:
            self.date_joined = datetime.utcnow()
        super().save(*args, **kwargs)
