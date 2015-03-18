__author__ = 'rerobins'
from bowling_entry import models as bowling_models
from django.contrib.auth import models as auth_models
from django.test import TestCase
import datetime


class LeagueCreationTest(TestCase):

    def test_league_creation_defaults(self):
        user = auth_models.User.objects.create_user(username='example', password='example', email='example@example.com')
        league = bowling_models.League.objects.create(secretary=user, name='Bowling League')

        league.update_weeks()

        self.assertEqual(len(league.weeks.all()), league.number_of_weeks)
        self.assertEqual(league.weeks.first().week_number, 1)
        self.assertEqual(league.weeks.last().week_number, league.number_of_weeks)

        week_number = 1
        date = league.start_date
        delta = datetime.timedelta(days=7)
        for week in league.weeks.all():
            self.assertEqual(week.week_number, week_number)
            self.assertEqual(week.date, date)
            week_number += 1
            date += delta

    def test_league_update_more_weeks(self):
        user = auth_models.User.objects.create_user(username='example', password='example', email='example@example.com')
        league = bowling_models.League.objects.create(secretary=user, name='Bowling League')

        league.update_weeks()

        # Initial starting point.
        league.number_of_weeks += 5
        league.save()

        league.update_weeks()
        self.assertEqual(len(league.weeks.all()), league.number_of_weeks)
        self.assertEqual(league.weeks.first().week_number, 1)
        self.assertEqual(league.weeks.last().week_number, league.number_of_weeks)

        week_number = 1
        date = league.start_date
        delta = datetime.timedelta(days=7)
        for week in league.weeks.all():
            self.assertEqual(week.week_number, week_number)
            self.assertEqual(week.date, date)
            week_number += 1
            date += delta

    def test_league_update_fewer_weeks(self):
        user = auth_models.User.objects.create_user(username='example', password='example', email='example@example.com')
        league = bowling_models.League.objects.create(secretary=user, name='Bowling League')

        league.update_weeks()

        # Initial starting point.
        league.number_of_weeks -= 5
        league.save()

        league.update_weeks()
        self.assertEqual(len(league.weeks.all()), league.number_of_weeks)
        self.assertEqual(league.weeks.first().week_number, 1)
        self.assertEqual(league.weeks.last().week_number, league.number_of_weeks)

        week_number = 1
        date = league.start_date
        delta = datetime.timedelta(days=7)
        for week in league.weeks.all():
            self.assertEqual(week.week_number, week_number)
            self.assertEqual(week.date, date)
            week_number += 1
            date += delta