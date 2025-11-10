# Note: Django admin doesn't natively support mongoengine Documents
# Admin registration for mongoengine documents is disabled
# You can manage these documents through the API or MongoDB directly

# from django.contrib import admin
# from .models import SmartWatch, WatchMetric, Alert

# If you need admin support for mongoengine documents, you would need to:
# 1. Use a third-party package like django-mongoengine-admin (if available)
# 2. Create custom admin views using Django views
# 3. Use MongoDB's native tools (MongoDB Compass, etc.)

# For now, admin is disabled for mongoengine documents
# The accounts.CustomUser model (Django ORM) can still use admin normally
