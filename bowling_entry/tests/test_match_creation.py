from django.test import TestCase
from bowling_entry import models as bowling_models
from bowling_entry.serializers import common


class MatchCreationTest(TestCase):
    fixtures = ['polarbowler']

    def test_create_match(self):
        league = bowling_models.League.objects.get(pk=3)
        week = league.weeks.get(week_number=1)

        team1 = league.teams.all()[0]
        team2 = league.teams.all()[1]

        match_create_definition = {
            'team1_definition': team1.pk,
            'team2_definition': team2.pk,
            'lanes': '1,2'
        }

        context = {
            'week': week,
            'league': league
        }

        serializer = common.Match(data=match_create_definition, context=context)

        self.assertTrue(serializer.is_valid(raise_exception=True))

        match = serializer.save()

        self.assertIsNotNone(match)

        self.assertIsNotNone(match.team1)
        self.assertIsNotNone(match.team2)

        self.assertEqual(len(match.team1.bowlers.all()), league.players_per_team)
        self.assertEqual(len(match.team2.bowlers.all()), league.players_per_team)

        for bowler in match.team1.bowlers.all():
            self.assertEqual(len(bowler.games.all()), league.number_of_games)

        for bowler in match.team2.bowlers.all():
            self.assertEqual(len(bowler.games.all()), league.number_of_games)

    def test_teams_cannot_play_each_other(self):

        league = bowling_models.League.objects.get(pk=3)
        week = league.weeks.get(week_number=1)

        team1 = league.teams.all()[0]

        match_create_definition = {
            'team1_definition': team1.pk,
            'team2_definition': team1.pk,
            'lanes': '1,2'
        }

        context = {
            'week': week,
            'league': league
        }

        serializer = common.Match(data=match_create_definition, context=context)

        self.assertFalse(serializer.is_valid())

    def test_lanes_not_colocated(self):
        league = bowling_models.League.objects.get(pk=3)
        week = league.weeks.get(week_number=1)

        team1 = league.teams.all()[0]
        team2 = league.teams.all()[1]

        match_create_definition = {
            'team1_definition': team1.pk,
            'team2_definition': team2.pk,
            'lanes': '3,5'
        }

        context = {
            'week': week,
            'league': league
        }

        serializer = common.Match(data=match_create_definition, context=context)

        self.assertFalse(serializer.is_valid())

    def test_teams_already_in_games(self):
        league = bowling_models.League.objects.get(pk=3)
        week = league.weeks.get(week_number=1)

        team1 = league.teams.all()[0]
        team2 = league.teams.all()[1]
        team3 = league.teams.all()[2]

        match_create_definition = {
            'team1_definition': team1.pk,
            'team2_definition': team2.pk,
            'lanes': '3,4'
        }

        context = {
            'week': week,
            'league': league
        }

        serializer = common.Match(data=match_create_definition, context=context)

        self.assertTrue(serializer.is_valid())
        serializer.save()

        match_create_definition = {
            'team1_definition': team1.pk,
            'team2_definition': team2.pk,
            'lanes': '3,4'
        }

        serializer = common.Match(data=match_create_definition, context=context)

        self.assertFalse(serializer.is_valid())

        match_create_definition = {
            'team1_definition': team2.pk,
            'team2_definition': team1.pk,
            'lanes': '3,4'
        }

        serializer = common.Match(data=match_create_definition, context=context)

        self.assertFalse(serializer.is_valid())

        match_create_definition = {
            'team1_definition': team3.pk,
            'team2_definition': team1.pk,
            'lanes': '3,4'
        }

        serializer = common.Match(data=match_create_definition, context=context)

        self.assertFalse(serializer.is_valid())

        match_create_definition = {
            'team1_definition': team3.pk,
            'team2_definition': team2.pk,
            'lanes': '3,4'
        }

        serializer = common.Match(data=match_create_definition, context=context)

        self.assertFalse(serializer.is_valid())