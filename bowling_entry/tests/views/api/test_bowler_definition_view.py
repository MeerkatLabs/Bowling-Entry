__author__ = 'rerobins'

from django.test import TestCase
from django.core.urlresolvers import reverse
from bowling_entry import models as bowling_models
from rest_framework.test import APIClient


class BowlerDefinitionView(TestCase):
    fixtures = ['polarbowler']

    def setUp(self):
        self.client = APIClient()
        self.client.login(username='username', password='pass')

    def test_move_bowler_to_substitute(self):
        league_pk = 3
        team_pk = 7
        bowler_pk = 40

        url = reverse('bowling_entry_league_team_bowlers_detail', args=[league_pk, team_pk, bowler_pk])

        response = self.client.patch('%s?removeTeam' % url, data={}, format='json')

        self.assertEqual(response.status_code, 200)

        bowler = bowling_models.BowlerDefinition.objects.get(pk=bowler_pk)

        self.assertIsNone(bowler.team)


