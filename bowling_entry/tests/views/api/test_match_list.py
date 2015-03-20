__author__ = 'rerobins'
from django.test import TestCase
from bowling_entry import models as bowling_models
from rest_framework.test import APIClient
from django.contrib.auth import models as auth_models


class MatchListCreate(TestCase):
    fixtures = ['polarbowler']

    def setUp(self):
        self.user = auth_models.User.objects.get(pk=1)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_match_listing(self):

        league = bowling_models.League.objects.get(pk=3)
        week = league.weeks.get(pk=56)

        url = week.get_absolute_matches_url()

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)

        response_data = response.data

        self.assertEqual(len(response_data), 4)

    def test_create_match(self):

        league = bowling_models.League.objects.get(pk=3)
        week = league.weeks.get(week_number=2)

        team1 = league.teams.all()[0]
        team2 = league.teams.all()[1]

        match_create_definition = {
            'team1_definition': team1.pk,
            'team2_definition': team2.pk,
            'lanes': '1,2'
        }

        url = week.get_absolute_matches_url()

        response = self.client.post(url, match_create_definition, format='json')

        self.assertEqual(response.status_code, 201)

        self.assertEqual(response.data.get('lanes', None), match_create_definition.get('lanes'))

        id = response.data.get('id')

        match = week.matches.get(pk=id)

        self.assertIsNotNone(match)
