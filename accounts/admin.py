# Note: Django admin doesn't natively support mongoengine Documents
# Admin registration for mongoengine users is disabled
# You can manage users through the API or MongoDB directly

# from django.contrib import admin
# from .models import CustomUser

# If you need admin support for mongoengine users, you would need to:
# 1. Create custom admin views using Django views
# 2. Use MongoDB's native tools (MongoDB Compass, etc.)
# 3. Use the API endpoints for user management

# For now, admin is disabled for mongoengine users

