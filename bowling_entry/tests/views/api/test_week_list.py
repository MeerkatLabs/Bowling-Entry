__author__ = 'rerobins'
from django.test import TestCase
from bowling_entry import models as bowling_models
from rest_framework.test import APIClient
from django.contrib.auth import models as auth_models


class WeekListCreate(TestCase):
    fixtures = ['polarbowler']

    def setUp(self):
        self.user = auth_models.User.objects.get(pk=1)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_week_listing(self):

        league = bowling_models.League.objects.get(pk=3)

        url = league.get_absolute_weeks_url()

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)

        response_data = response.data

        self.assertEqual(len(response_data), 18)

    def test_cannot_create_week(self):

        league = bowling_models.League.objects.get(pk=3)

        url = league.get_absolute_weeks_url()

        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, 405)
