from django.db import models
from django.contrib.auth.models import User

# Store user-specific settings and API keys
class UserProfile(models.Model):
    # Link to the main Django user account
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Twitter API credentials for each user
    twitter_api_key = models.CharField(max_length=255, blank=True, null=True)
    twitter_api_secret = models.CharField(max_length=255, blank=True, null=True)
    twitter_access_token = models.CharField(max_length=255, blank=True, null=True)
    twitter_access_secret = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.user.username
