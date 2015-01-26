from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

# Create your models here.


class Match(models.Model):
    """
    Class that will define a match that is being recorded.
    """
    date = models.DateField(blank=False)
    creator = models.ForeignKey(User, blank=False, related_name='matches')
    number_of_games = models.IntegerField(blank=False, default=3)
    players_per_team = models.IntegerField(blank=False, default=5)
    lanes = models.CommaSeparatedIntegerField(blank=True, max_length=7)
    games_created = models.BooleanField(blank=False, default=False)

    def get_absolute_url(self):
        return reverse('bowling_entry_matchdetails', args=[self.pk])

    def can_start_games(self):

        result = not self.games_created

        # Need to verify that both teams have been defined and that all of the teams have all of the players defined
        if len(self.teams.all()) == 2:
            for team in self.teams.all():
                result = result and len(team.bowlers.all()) == self.players_per_team
        else:
            result = False

        return result

    def start_games(self):

        for team in self.teams.all():
            for bowler in team.bowlers.all():
                for game_number in range(0, self.number_of_games):
                    game = Game(bowler=bowler, game_number=(game_number+1))
                    game.save()

        self.games_created = True
        self.save()

    def game_range(self):
        return range(1, self.number_of_games+1)

    def get_game_data(self, game_id):
        print game_id
        print self.number_of_games

        if game_id > self.number_of_games:
            print 'Returning early'
            return []

        result = []
        for team in self.teams.all().order_by('pk'):
            result.append((team, team.get_game_iterable(game_id)))

        print result

        return result


class Team(models.Model):
    name = models.CharField(blank=False, max_length=100)
    match = models.ForeignKey(Match, blank=False, related_name='teams')

    def get_game_iterable(self, game_id):

        if game_id > self.match.number_of_games:
            return []

        result = []

        for bowler in self.bowlers.all().order_by('order'):
            result.append((bowler, bowler.games.filter(game_number=game_id).get()))

        return result

    def get_absolute_url(self):
        return reverse('bowling_entry_teamdetails', args=[self.match.pk, self.pk])


class Bowler(models.Model):
    REGULAR = 'regular'
    SUBSTITUTE = 'substitute'
    VACANT = 'vacant'
    BLIND = 'blind'
    BOWLER_TYPE_CHOICES = (
        (REGULAR, 'Regular'),
        (SUBSTITUTE, 'Substitute'),
        (VACANT, 'Vacant'),
        (BLIND, 'Blind'),
    )

    order = models.IntegerField(blank=False)
    name = models.CharField(blank=False, max_length=100)
    handicap = models.IntegerField(blank=True)
    type = models.CharField(blank=False, max_length=10, choices=BOWLER_TYPE_CHOICES, default=REGULAR)
    team = models.ForeignKey(Team, blank=False, related_name='bowlers')


class Game(models.Model):
    """
    Collection of all of the frames that were bowled by the bowler.
    """
    bowler = models.ForeignKey('Bowler', blank=False, related_name='games')
    game_number = models.IntegerField(blank=False)
    frame01 = models.CommaSeparatedIntegerField(max_length=4, blank=True)
    frame02 = models.CommaSeparatedIntegerField(max_length=4, blank=True)
    frame03 = models.CommaSeparatedIntegerField(max_length=4, blank=True)
    frame04 = models.CommaSeparatedIntegerField(max_length=4, blank=True)
    frame05 = models.CommaSeparatedIntegerField(max_length=4, blank=True)
    frame06 = models.CommaSeparatedIntegerField(max_length=4, blank=True)
    frame07 = models.CommaSeparatedIntegerField(max_length=4, blank=True)
    frame08 = models.CommaSeparatedIntegerField(max_length=4, blank=True)
    frame09 = models.CommaSeparatedIntegerField(max_length=4, blank=True)
    frame10 = models.CommaSeparatedIntegerField(max_length=8, blank=True)
    splits = models.CommaSeparatedIntegerField(max_length=30, blank=True)

    def get_frame(self, frame_id):
        if frame_id == 1:
            return self.frame01
        elif frame_id == 2:
            return self.frame02
        elif frame_id == 3:
            return self.frame03
        elif frame_id == 4:
            return self.frame04
        elif frame_id == 5:
            return self.frame05
        elif frame_id == 6:
            return self.frame06
        elif frame_id == 7:
            return self.frame07
        elif frame_id == 8:
            return self.frame08
        elif frame_id == 9:
            return self.frame09
        elif frame_id == 10:
            return self.frame10
        else:
            return ''

    def set_frame(self, frame_id, score):
        if frame_id == 1:
            self.frame01 = score
        elif frame_id == 2:
            self.frame02= score
        elif frame_id == 3:
            self.frame03= score
        elif frame_id == 4:
            self.frame04= score
        elif frame_id == 5:
            self.frame05= score
        elif frame_id == 6:
            self.frame06= score
        elif frame_id == 7:
            self.frame07= score
        elif frame_id == 8:
            self.frame08= score
        elif frame_id == 9:
            self.frame09= score
        elif frame_id == 10:
            self.frame10= score


