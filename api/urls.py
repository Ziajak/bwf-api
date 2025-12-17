from api import views
from rest_framework import routers
from django.conf.urls import include
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
router.register(r'groups', views.GroupViewset)
router.register(r'events', views.EventViewset)
router.register(r'members', views.MemberViewset)
router.register(r'comments', views.CommentViewset)
router.register(r'users', views.UserViewSet)
router.register(r'profile', views.UserProfileViewset)


urlpatterns = [
    path(r'', include(router.urls)),
    path('authenticate/', views.CustomObtainAuthToken.as_view())
]