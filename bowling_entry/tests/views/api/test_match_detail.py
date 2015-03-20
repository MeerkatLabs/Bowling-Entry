__author__ = 'rerobins'
from django.test import TestCase
from bowling_entry import models as bowling_models
from rest_framework.test import APIClient
from django.contrib.auth import models as auth_models


class SubstituteListCreate(TestCase):
    fixtures = ['polarbowler']

    def setUp(self):
        self.user = auth_models.User.objects.get(pk=1)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_details(self):
        league_pk = 3
        week_pk = 56
        match_pk = 3

        league = bowling_models.League.objects.get(pk=league_pk)
        week = league.weeks.get(pk=week_pk)
        match = week.matches.get(pk=match_pk)

        url = match.get_absolute_url()

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)

        response_data = response.data

        self.assertEqual(response_data.get('id', None), match_pk)

    def test_update_details(self):
        league_pk = 3
        week_pk = 56
        match_pk = 3

        league = bowling_models.League.objects.get(pk=league_pk)
        week = league.weeks.get(pk=week_pk)
        match = week.matches.get(pk=match_pk)

        url = match.get_absolute_url()

        data = dict(lanes='11,12')

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, 200)

        response_data = response.data

        self.assertEqual(response_data.get('id', None), match_pk)
        self.assertEqual(response_data.get('lanes', None), data['lanes'])

    def test_delete_team(self):
        league_pk = 3
        week_pk = 56
        match_pk = 3

        league = bowling_models.League.objects.get(pk=league_pk)
        week = league.weeks.get(pk=week_pk)
        match = week.matches.get(pk=match_pk)

        url = match.get_absolute_url()

        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, 204)

        with self.assertRaises(bowling_models.Match.DoesNotExist):
            week.matches.get(pk=match_pk)

        with self.assertRaises(bowling_models.Match.DoesNotExist):
            bowling_models.Match.objects.get(pk=match_pk)