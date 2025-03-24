from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views as token_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('todos.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', token_views.obtain_auth_token),
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
]