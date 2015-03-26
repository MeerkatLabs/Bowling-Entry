from django.test import TestCase
from bowling_entry import models as bowling_models
from bowling_entry.serializers import common
from bowling_entry.serializers import scoresheet


class ScoreSheetSerializerTestCase(TestCase):
    fixtures = ['polarbowler']

    def setUp(self):
        self.league = bowling_models.League.objects.get(pk=3)
        self.week = self.league.weeks.get(week_number=2)

        self.team1 = self.league.teams.all()[0]
        self.team2 = self.league.teams.all()[1]

        match_create_definition = {
            'team1_definition': self.team1.pk,
            'team2_definition': self.team2.pk,
            'lanes': '1,2'
        }

        context = {
            'week': self.week,
            'league': self.league
        }

        serializer = common.Match(data=match_create_definition, context=context)

        self.assertTrue(serializer.is_valid(raise_exception=True))

        self.match = serializer.save()

    def test_serialization(self):
        serializer = scoresheet.ScoreSheet(self.match)
        self.assertIsNotNone(serializer.data)

    def test_update_single_bowler_score(self):
        data = {
            'team1': {
                'bowlers': [
                    {
                        'id': self.match.team1.bowlers.all()[0].pk,
                        'games': [
                            {
                                'game_number': 1,
                                'total': 150
                            }
                        ]
                    }
                ]
            }
        }

        serializer = scoresheet.ScoreSheet(self.match, data=data, partial=True,)

        self.assertTrue(serializer.is_valid())

        serializer.save()

        self.assertEquals(self.match.team1.bowlers.all()[0].games.get(game_number=1).total, 150)

    def test_update_no_bowler_id(self):
        data = {
            'team1': {
                'bowlers': [
                    {
                        'games': [
                            {
                                'game_number': 1,
                                'total': 150
                            }
                        ]
                    }
                ]
            }
        }

        serializer = scoresheet.ScoreSheet(self.match, data=data, partial=True,)

        self.assertFalse(serializer.is_valid())

    def test_update_no_game_number(self):
        data = {
            'team1': {
                'bowlers': [
                    {
                        'id': self.match.team1.bowlers.all()[0].pk,
                        'games': [
                            {
                                'total': 150
                            }
                        ]
                    }
                ]
            }
        }

        serializer = scoresheet.ScoreSheet(self.match, data=data, partial=True,)

        self.assertFalse(serializer.is_valid())

    def test_frame_update(self):
        data = {
            'team1': {
                'bowlers': [
                    {
                        'id': self.match.team1.bowlers.all()[0].pk,
                        'games': [
                            {
                                'game_number': 1,
                                'total': 150,
                                'frames': [
                                    {
                                        'frame_number': 1,
                                        'throw1_type': 'T',
                                        'throw1_value': 5,
                                        'throw2_type': 'T',
                                        'throw2_value': 5
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }

        serializer = scoresheet.ScoreSheet(self.match, data=data, partial=True, )
        self.assertTrue(serializer.is_valid(raise_exception=True))

        match = serializer.save()

        output_serializer = scoresheet.ScoreSheet(match)
        data_dict = output_serializer.data

        self.assertIsNotNone(data_dict.get('team1'))
        team1 = data_dict.get('team1')
        self.assertIsNotNone(team1.get('bowlers'))
        bowler = team1.get('bowlers')[0]
        self.assertIsNotNone(bowler.get('games'))
        game = bowler.get('games')[0]

        self.assertEqual(game.get('total'), 150)
        self.assertIsNotNone(game.get('frames'))
        self.assertEqual(len(game.get('frames')), 1)

        frame = game.get('frames')[0]

        self.assertEqual(frame.get('throw1_type'), 'T')
        self.assertEqual(frame.get('throw1_value'), 5)
        self.assertEqual(frame.get('throw2_type'), 'T')
        self.assertEqual(frame.get('throw2_value'), 5)

