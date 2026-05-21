from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from django.utils import timezone
from datetime import timedelta
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from api.permission import IsGroupAdminForEventCreate
from api.models import User, Group, Member, Event, Bet
from api.views import EventViewset


class TestIsGroupAdminForEvent(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.admin_user = User.objects.create_user(username="admin", password="Test1234")
        self.normal_user = User.objects.create_user(username="user", password="Test12")

        self.group = Group.objects.create(name="Group_first", location="Poland", description="Some desc")

        self.member_admin = Member.objects.create(group=self.group, user=self.admin_user, admin=True)
        self.member_user = Member.objects.create(group=self.group, user=self.normal_user, admin=False)

        self.future_event = Event.objects.create(
            team1="Poland", team2="Germany", time=timezone.now() + timedelta(days=20), group=self.group
        )
        self.past_event = Event.objects.create(
            team1="Spain", team2="France", time=timezone.now() - timedelta(days=15), group=self.group
        )

        self.permission = IsGroupAdminForEventCreate()

    def test_get_allowed_for_any_user(self):
        request = self.factory.get("/events/")
        force_authenticate(request, user=self.normal_user)
        drf_request = Request(request)
        assert self.permission.has_permission(drf_request, None)

    def test_put_allowed_if_event_finished_and_admin(self):
        request = self.factory.put("/events/{}/".format(self.past_event.id))
        request.user = self.admin_user
        assert self.permission.has_object_permission(request, None, self.past_event)

    def test_put_denied_if_event_not_finished(self):
        request = self.factory.put("/events/{}/".format(self.future_event.id))
        request.user = self.admin_user
        assert not self.permission.has_object_permission(request, None, self.future_event)

    def test_post_allowed_for_admin(self):
        request = self.factory.post("/events/", {"group": self.group.id}, format='json')
        force_authenticate(request, user=self.admin_user)
        drf_request = Request(request, parsers=[JSONParser()])
        assert self.permission.has_permission(drf_request, None)

    def test_post_denied_without_group_even_for_admin(self):
        request = self.factory.post("/events/", {}, format='json')
        force_authenticate(request, user=self.admin_user)
        drf_request = Request(request, parsers=[JSONParser()])
        assert not self.permission.has_permission(drf_request, None)


class TestEventCalculatePoints(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="User_test", password="Pol123")
        self.group = Group.objects.create(
            name="Group",
            location="Poland",
            description="Test_desc"
        )

        Member.objects.create(
            user=self.user,
            group=self.group,
            admin=True
        )

        self.event = Event.objects.create(
            team1="Poland",
            team2="Germany",
            time=timezone.now() - timedelta(days=1),
            group=self.group,
            score1=2,
            score2=1
        )


    def test_exact_score_gives_3_points(self):
        bet = Bet.objects.create(user=self.user, event=self.event, score1=2, score2=1)

        self.event.calculate_points()

        bet.refresh_from_db()
        self.assertEqual(bet.points, 3)

    def test_correct_result_gives_1_point(self):
        bet = Bet.objects.create(user=self.user, event=self.event, score1=3, score2=1)

        self.event.calculate_points()

        bet.refresh_from_db()
        self.assertEqual(bet.points, 1)

    def test_wrong_result_gives_0_points(self):
        bet = Bet.objects.create(user=self.user, event=self.event, score1=1, score2=2)

        self.event.calculate_points()

        bet.refresh_from_db()
        self.assertEqual(bet.points, 0)


