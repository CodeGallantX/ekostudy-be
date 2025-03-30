from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Authentication API",
        default_version='v1',
        description="API documentation for authentication system",
        terms_of_service="https://your-terms-url.com/",
        contact=openapi.Contact(email="contact@yourdomain.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/auth/', include('auth_app.urls')),
    path('api/', include('marketplace.urls')),
    
    # Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]