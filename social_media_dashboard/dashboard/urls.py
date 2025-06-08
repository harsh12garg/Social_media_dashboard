# Import Django's path function and all our view functions
from django.urls import path
from .views import (
    dashboard_view, config_view, analytics_view,
    login_view, register_view, logout_view, platform_select_view,
    twitter_dashboard_view, twitter_config_view, twitter_analytics_view
)

# Map URLs to their corresponding view functions
# Each path() defines what happens when a user visits that URL
urlpatterns = [
    path('', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('platform/', platform_select_view, name='platform_select'),
    path('facebook/', dashboard_view, name='dashboard'),
    path('facebook/config/', config_view, name='config'),
    path('facebook/analytics/', analytics_view, name='analytics'),
    path('twitter/', twitter_dashboard_view, name='twitter_dashboard'),
    path('twitter/config/', twitter_config_view, name='twitter_config'),
    path('twitter/analytics/', twitter_analytics_view, name='twitter_analytics'),
] 