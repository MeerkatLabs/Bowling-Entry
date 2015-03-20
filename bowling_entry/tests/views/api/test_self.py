__author__ = 'rerobins'
from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework.test import APIClient
from django.contrib.auth import models as auth_models


class SubstituteListCreate(TestCase):
    fixtures = ['polarbowler']

    def setUp(self):
        self.user = auth_models.User.objects.get(pk=1)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_details(self):

        url = reverse('bowling_entry_self')

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)

        response_data = response.data

        self.assertEqual(response_data.get('username', None), self.user.username)
