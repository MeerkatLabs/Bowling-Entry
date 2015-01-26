from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.importlib import import_module
from django.core.urlresolvers import reverse

from bowling_entry.models import Match


class TestMatchCreate(TestCase):

    def setUp(self):
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

        self.user = User.objects.create_user(username='rerobins', password='password')

    def test_no_user(self):
        match = Match(creator=self.user, date='2015-01-30', lanes='5,6', players_per_team=5, number_of_games=3)
        match.save()

        response = self.client.get(match.get_absolute_url())

        self.assertEquals(response.status_code, 302)

    def test_get_match(self):
        match = Match(creator=self.user, date='2015-01-30', lanes='5,6', players_per_team=5, number_of_games=3)
        match.save()

        self.client.login(username=self.user.username, password='password')

        response = self.client.get(match.get_absolute_url())

        self.assertEquals(response.status_code, 200)

    def test_get_match_not_mine(self):

        not_my_user = User.objects.create_user(username='asdf', password='password')
        match = Match(creator=not_my_user, date='2015-01-30', lanes='5,6', players_per_team=5, number_of_games=3)
        match.save()

        self.client.login(username=self.user.username, password='password')

        response = self.client.get(match.get_absolute_url())

        self.assertEquals(response.status_code, 404)


