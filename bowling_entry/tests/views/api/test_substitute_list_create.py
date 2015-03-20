__author__ = 'rerobins'
from django.test import TestCase
from bowling_entry import models as bowling_models
from rest_framework.test import APIClient
from django.contrib.auth import models as auth_models


class SubstituteListCreate(TestCase):
    fixtures = ['polarbowler']

    def setUp(self):
        self.user = auth_models.User.objects.get(pk=1)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_substitute_listing(self):

        league = bowling_models.League.objects.get(pk=3)

        url = league.get_absolute_substitutes_url()

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)

        response_data = response.data

        self.assertEqual(len(response_data), 1)

    def test_add_new_substitute(self):

        league = bowling_models.League.objects.get(pk=3)

        url = league.get_absolute_substitutes_url()

        data = dict(name='Substitute Name')

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201, 'Verify that status code is create')

        response_data = response.data

        self.assertIsNotNone(response_data.get('id', None))

        pk = response_data.get('id')

        sub = league.substitutes().get(pk=pk)

        self.assertIsNotNone(sub)