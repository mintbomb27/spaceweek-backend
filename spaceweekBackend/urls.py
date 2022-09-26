from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include

from submissions.views import ProfileView
from userauth.views import RootView
 
urlpatterns = [
    path('', RootView.as_view()),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls'), name='socialaccount_signup'),
    path('profile/', ProfileView.as_view()),
    path('api/auth/',include('userauth.urls')),
    path('api/events/',include('submissions.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
