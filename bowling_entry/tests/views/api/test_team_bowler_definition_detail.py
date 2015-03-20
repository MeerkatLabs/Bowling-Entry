__author__ = 'rerobins'

from django.test import TestCase
from bowling_entry import models as bowling_models
from rest_framework.test import APIClient


class BowlerDefinitionView(TestCase):
    fixtures = ['polarbowler']

    def setUp(self):
        self.client = APIClient()
        self.client.login(username='username', password='pass')

    def test_retrieve_bowler(self):
        league_pk = 3
        team_pk = 7
        bowler_pk = 40

        league_initial = bowling_models.League.objects.get(pk=league_pk)
        team_initial = league_initial.teams.get(pk=team_pk)
        bowler_initial = team_initial.bowlers.get(pk=bowler_pk)

        url = bowler_initial.get_absolute_url()

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)

    def test_delete_bowler(self):
        league_pk = 3
        team_pk = 7
        bowler_pk = 40

        league_initial = bowling_models.League.objects.get(pk=league_pk)
        team_initial = league_initial.teams.get(pk=team_pk)
        bowler_initial = team_initial.bowlers.get(pk=bowler_pk)

        url = bowler_initial.get_absolute_url()

        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, 204)

        with self.assertRaises(bowling_models.BowlerDefinition.DoesNotExist):
            bowling_models.BowlerDefinition.objects.get(pk=40)

    def test_move_bowler_to_substitute(self):
        league_pk = 3
        team_pk = 7
        bowler_pk = 40

        league_initial = bowling_models.League.objects.get(pk=league_pk)
        team_initial = league_initial.teams.get(pk=team_pk)
        bowler_initial = team_initial.bowlers.get(pk=bowler_pk)

        url = bowler_initial.get_absolute_url()

        response = self.client.patch('%s?removeTeam' % url, data={}, format='json')

        self.assertEqual(response.status_code, 200)

        bowler = bowling_models.BowlerDefinition.objects.get(pk=bowler_pk)

        self.assertIsNone(bowler.team)


