from django.test import TestCase
from bowling_entry import models as bowling_models
from bowling_entry.serializers import common


class MatchCreationTest(TestCase):
    fixtures = ['polarbowler']

    def test_move_bowler_to_substitute(self):

        league = bowling_models.League.objects.get(pk=3)
        team = league.teams.get(pk=7)
        bowler = team.bowlers.get(pk=40)

        serializer = common.BowlerDefinition(bowler, {}, partial=True, context={'league': league,
                                                                                'team': team,
                                                                                'remove_team': True})
        self.assertTrue(serializer.is_valid())

        bowler = serializer.save()

        self.assertIsNone(bowler.team)

        with self.assertRaises(bowling_models.BowlerDefinition.DoesNotExist):
            team.bowlers.get(pk=bowler.pk)

    def test_move_bowler_to_another_team(self):

        league = bowling_models.League.objects.get(pk=3)
        team = league.teams.get(pk=7)
        team_other = league.teams.get(pk=5)
        bowler = team.bowlers.get(pk=40)

        serializer = common.BowlerDefinition(bowler, {'team': team_other.pk}, partial=True, context={'league': league,
                                                                                                     'team': team})

        self.assertTrue(serializer.is_valid(raise_exception=True))

        bowler = serializer.save()

        self.assertIsNotNone(bowler.team)

        # Make sure not on the old team
        with self.assertRaises(bowling_models.BowlerDefinition.DoesNotExist):
            team.bowlers.get(pk=bowler.pk)

        self.assertIsNotNone(team_other.bowlers.get(pk=bowler.pk))

    def test_move_bowler_to_another_leagues_team(self):
        league = bowling_models.League.objects.get(pk=3)
        team = league.teams.get(pk=7)
        bowler = team.bowlers.get(pk=40)

        other_league = bowling_models.League.objects.create(secretary=league.secretary,
                                                            name='asdf')
        other_team = bowling_models.TeamDefinition.objects.create(league=other_league, name='asdf')

        serializer = common.BowlerDefinition(bowler, {'team': other_team.pk}, partial=True, context={'league': league,
                                                                                                     'team': team})

        self.assertFalse(serializer.is_valid())