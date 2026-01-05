from django.shortcuts import render
from rest_framework import viewsets, status
from django.utils import timezone
from rest_framework.decorators import action
from .models import Group, Event, UserProfile, User, Member, Comment, Bet
from .serializers import (GroupSerializer, EventSerializer, GroupFullSerializer,
                          UserSerializer, UserProfileSerializer, ChangePasswordSerializer,
                          MemberSerializer, CommentSerializer, EventFullSerializer,
                          BetSerializer, PlaceBetSerializer)
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from datetime import datetime

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (AllowAny, )

    @action(methods=['PUT'], detail=True, serializer_class=ChangePasswordSerializer,
            permission_classes=[IsAuthenticated]
           )
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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

class CommentViewset(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class GroupViewset(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = GroupFullSerializer(instance, many=False, context={'request': request})
        return Response(serializer.data)



class EventViewset(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = EventFullSerializer(instance, many=False, context={'request': request})
        return Response(serializer.data)

class MemberViewset(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    @action(methods=['post'], detail=False)
    def join(self, request):
        if 'group' in request.data and 'user' in request.data:
            try:
                group = Group.objects.get(id=request.data['group'])
                user = User.objects.get(id=request.data['user'])

                member = Member.objects.create(group=group, user=user, admin=False)
                serializer = MemberSerializer(member, many=False)
                response = {'message': 'Joined group', 'results': serializer.data}
                return Response(response, status=status.HTTP_200_OK)
            except:
                response = {'message': 'Cannot join'}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {'message': 'Wrong params'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False)
    def leave(self, request):
        if 'group' in request.data and 'user' in request.data:
            try:
                group = Group.objects.get(id=request.data['group'])
                user = User.objects.get(id=request.data['user'])

                member = Member.objects.get(group=group, user=user)
                member.delete()
                response = {'message': 'Left group'}
                return Response(response, status=status.HTTP_200_OK)
            except:
                response = {'message': 'Cannot leave group'}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {'message': 'Wrong params'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

class BetViewset(viewsets.ModelViewSet):
    queryset = Bet.objects.all()
    serializer_class = BetSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        response = {'message': "Metod not allowed"}
        return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        response = {'message': "Metod not allowed"}
        return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['POST'], url_path='place_bet')
    def place_bet(self, request):
        serializer = PlaceBetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = serializer.validated_data['event']
        score1 = serializer.validated_data['score1']
        score2 = serializer.validated_data['score2']
        if event.time < timezone.now():
            return Response(
                {"message": f"You can't place a bet. Too late!"
                 },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not self.checkIfUserInGroup(event.group, request.user):
            return Response(
                {"message": "User not in group"},
                status=status.HTTP_403_FORBIDDEN
            )

        bet, created = Bet.objects.update_or_create(
            event=event,
            user=request.user,
            defaults={
                "score1": score1,
                "score2": score2
            }
        )

        response_serializer = BetSerializer(bet)

        return Response(
            {
                "message": "Bet Created" if created else "Bet Updated",
                "new": created,
                "result": response_serializer.data
            },
            status=status.HTTP_200_OK
        )

    def checkIfUserInGroup(self, group, user):
        return Member.objects.filter(user=user, group=group).exists()



class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = response.data['token']
        user = Token.objects.get(key=token).user
        userSerializer = UserSerializer(user, many=False)
        return Response({'token': token,
                         'user': userSerializer.data})


