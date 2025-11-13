from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .models import Group, Event, UserProfile, User
from .serializers import (GroupSerializer, EventSerializer, GroupFullSerializer,
                          UserSerializer, UserProfileSerializer, ChangePasswordSerializer)
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['PUT'], detail=True, serializer_class=ChangePasswordSerializer)
    def change_pass(self, request, pk):
        user = User.objects.get(pk=pk)
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get('old_password')):
                return Response({'message': 'Wrong old password'},
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'message': 'Password Updated'}, status.HTTP_200_OK)


class UserProfileViewset(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class GroupViewset(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = GroupFullSerializer(instance, many=False, context={'request': request})
        return Response(serializer.data)



class EventViewset(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = response.data['token']
        user = Token.objects.get(key=token).user
        userSerializer = UserSerializer(user, many=False)
        return Response({'token': token,
                         'user': userSerializer.data})
