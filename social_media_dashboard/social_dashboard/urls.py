# Main URL routing for the entire project
# The dashboard app handles most of our views, so we include its URLs below
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
]
