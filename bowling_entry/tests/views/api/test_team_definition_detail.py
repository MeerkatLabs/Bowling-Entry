__author__ = 'rerobins'
from django.test import TestCase
from bowling_entry import models as bowling_models
from rest_framework.test import APIClient
from django.contrib.auth import models as auth_models


class TeamDefinitionDetail(TestCase):
    fixtures = ['polarbowler']

    def setUp(self):
        self.user = auth_models.User.objects.get(pk=1)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_details(self):
        league_pk = 3
        team_pk = 7

        league = bowling_models.League.objects.get(pk=league_pk)
        team = league.teams.get(pk=team_pk)

        url = team.get_absolute_url()

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)

        response_data = response.data

        self.assertEqual(response_data.get('id', None), team_pk)
        self.assertEqual(response_data.get('name', None), team.name)

    def test_update_team_details(self):
        league_pk = 3
        team_pk = 7

        league = bowling_models.League.objects.get(pk=league_pk)
        team = league.teams.get(pk=team_pk)

        url = team.get_absolute_url()

        data = dict(name='New Team Name')

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, 200)

        response_data = response.data

        self.assertEqual(response_data.get('id', None), team_pk)
        self.assertEqual(response_data.get('name', None), data.get('name'))

    def test_delete_team(self):
        league_pk = 3
        team_pk = 7

        league = bowling_models.League.objects.get(pk=league_pk)
        team = league.teams.get(pk=team_pk)

        url = team.get_absolute_url()

        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, 204)

        with self.assertRaises(bowling_models.TeamDefinition.DoesNotExist):
            league.teams.get(pk=team_pk)

        with self.assertRaises(bowling_models.TeamDefinition.DoesNotExist):
            bowling_models.TeamDefinition.objects.get(pk=team_pk)
