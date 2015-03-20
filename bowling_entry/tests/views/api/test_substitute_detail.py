__author__ = 'rerobins'
from django.test import TestCase
from bowling_entry import models as bowling_models
from rest_framework.test import APIClient
from django.contrib.auth import models as auth_models


class SubstituteDetail(TestCase):
    fixtures = ['polarbowler']

    def setUp(self):
        self.user = auth_models.User.objects.get(pk=1)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_details(self):
        league_pk = 3
        sub_pk = 101

        league = bowling_models.League.objects.get(pk=league_pk)
        sub = league.substitutes().get(pk=sub_pk)

        url = sub.get_absolute_url()

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)

        response_data = response.data

        self.assertEqual(response_data.get('id', None), sub_pk)
        self.assertEqual(response_data.get('name', None), sub.name)

    def test_update_details(self):
        league_pk = 3
        sub_pk = 101

        league = bowling_models.League.objects.get(pk=league_pk)
        sub = league.substitutes().get(pk=sub_pk)

        url = sub.get_absolute_url()

        data = dict(name='New Sub Name')

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, 200)

        response_data = response.data

        self.assertEqual(response_data.get('id', None), sub_pk)
        self.assertEqual(response_data.get('name', None), data.get('name'))

    def test_delete_team(self):
        league_pk = 3
        sub_pk = 101

        league = bowling_models.League.objects.get(pk=league_pk)
        sub = league.substitutes().get(pk=sub_pk)

        url = sub.get_absolute_url()

        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, 204)

        with self.assertRaises(bowling_models.BowlerDefinition.DoesNotExist):
            league.substitutes().get(pk=sub_pk)

        with self.assertRaises(bowling_models.BowlerDefinition.DoesNotExist):
            bowling_models.BowlerDefinition.objects.get(pk=sub_pk)