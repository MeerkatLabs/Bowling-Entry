__author__ = 'rerobins'
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import models as auth_models
from bowling_entry import models as bowling_models
from rest_framework.test import APIClient


class LeagueListCreate(TestCase):
    fixtures = ['polarbowler']

    def setUp(self):
        self.user = auth_models.User.objects.get(pk=1)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_league(self):

        url = reverse('bowling_entry_leagues')

        data = dict(name='League Name')

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201, 'Verify that status code is create')

        response_data = response.data

        self.assertEqual(data.get('name'), response_data.get('name', None))
        self.assertIsNotNone(response_data.get('id', None))

        league_id = response_data.get('id')
        league = bowling_models.League.objects.get(pk=league_id)

        self.assertEqual(league.secretary, self.user, 'Verify that the secretary is the logged in user')
