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
        create_match_url = reverse('bowling_entry_matchcreate')

        response = self.client.get(create_match_url)

        self.assertEquals(response.status_code, 302)

    def test_create_new_match(self):
        create_match_url = reverse('bowling_entry_matchcreate')

        self.client.login(username=self.user.username, password='password')

        response = self.client.get(create_match_url)

        self.assertEquals(response.status_code, 200)

        response = self.client.post(create_match_url, {'date': '2015-01-30',
                                                       'lanes': '5,6',
                                                       'players_per_team': '5',
                                                       'number_of_games': '3'})

        # Because it should be a redirect to a new page.
        self.assertEquals(response.status_code, 302)

        self.user = User.objects.get(username=self.user.username)
        self.assertEquals(len(self.user.matches.all()), 1)

        match = self.user.matches.all()[0]
        self.assertEquals(match.lanes, '5,6')
        self.assertEquals(match.players_per_team, 5)
        self.assertEquals(match.number_of_games, 3)

        self.assertRedirects(response, match.get_absolute_url())

