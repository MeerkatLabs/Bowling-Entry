__author__ = 'rerobins'
from django.test import TestCase
from bowling_entry import models as bowling_models
from rest_framework.test import APIClient
from django.contrib.auth import models as auth_models


class TeamBowlerDefinitionListCreate(TestCase):
    fixtures = ['polarbowler']

    def setUp(self):
        self.user = auth_models.User.objects.get(pk=1)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_bowler_list(self):
        league_pk = 3
        team_pk = 7

        league_initial = bowling_models.League.objects.get(pk=league_pk)
        team_initial = league_initial.teams.get(pk=team_pk)

        url = team_initial.get_absolute_bowlers_url()

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), len(team_initial.bowlers.all()))

    def test_create_bowler(self):

        league_pk = 3
        team_pk = 7

        league_initial = bowling_models.League.objects.get(pk=league_pk)
        team_initial = league_initial.teams.get(pk=team_pk)

        url = team_initial.get_absolute_bowlers_url()

        data = dict(name='Some Bowler')

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('name', None), data['name'])

        bowler = bowling_models.BowlerDefinition.objects.get(pk=response.data.get('id'))

        self.assertEqual(bowler.team, team_initial)
        self.assertEqual(bowler.league, league_initial)