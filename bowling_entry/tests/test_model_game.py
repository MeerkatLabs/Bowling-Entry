__author__ = 'rerobins'
from django.test import TestCase
from bowling_entry.models import Game


class GameModel(TestCase):

    def test_splits(self):

        g = Game()

        self.assertEquals(g.splits, '')

        g.set_split(0, False)
        self.assertEquals(g.splits, '')

        g.set_split(1, True)
        self.assertEquals(g.splits, '1')

        g.set_split(2, True)
        self.assertEquals(g.splits, '1,2')

        g.set_split(1, False)
        self.assertEquals(g.splits, '2')

