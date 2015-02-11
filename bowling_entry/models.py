from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

# Create your models here.

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


class League(models.Model):
    """
    Definition of a league
    """
    secretary = models.ForeignKey(User, related_name='leagues')
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    number_of_weeks = models.IntegerField(blank=False, default=10)
    number_of_games = models.IntegerField(blank=False, default=3)
    players_per_team = models.IntegerField(blank=False, default=4)
    points_per_game = models.IntegerField(blank=False, default=2)
    points_for_totals = models.IntegerField(blank=False, default=2)
    handicap_max = models.IntegerField(blank=False, default=210)
    handicap_percentage = models.IntegerField(blank=False, default=90)

    def __unicode__(self):
        return self.name

    def substitutes(self):
        return self.bowlers.filter(team=None)


class Week(models.Model):
    """
    Week object used to collect all of the instance data
    """
    league = models.ForeignKey(League, related_name='weeks')
    date = models.DateField(blank=False)

    def __unicode__(self):
        return "%s: %s" % (self.league, self.date)


class TeamDefinition(models.Model):
    """
    Definition of a team.  This will be used to define what team will be used from week to week
    """
    name = models.CharField(max_length=100)
    league = models.ForeignKey(League, related_name='teams', blank=False)

    def __unicode__(self):
        return "%s: %s" % (self.league, self.name)


class BowlerDefinition(models.Model):
    """
    Definition of a bowler that will participate in the league.
    """
    name = models.CharField(max_length=100)
    handicap = models.IntegerField(blank=True, null=True)
    league = models.ForeignKey(League, related_name='bowlers', null=False, blank=False)
    team = models.ForeignKey(TeamDefinition, related_name='bowlers', blank=True, null=True)

    def __unicode__(self):
        if self.team is None:
            return "%s: %s Substitute Definition" % (self.league, self.name)
        else:
            return "%s: %s Definition" % (self.team, self.name)


class TeamInstance(models.Model):
    """
    Instance of a team that is bowling on a given week
    """
    definition = models.ForeignKey(TeamDefinition)
    match = models.ForeignKey('Match')

    def define_bowlers(self):
        index = 0
        for bowler in self.definition.bowlers.all():
            bowler_instance = TeamInstanceBowler(definition=bowler, team=self,
                                                 type=REGULAR, handicap=bowler.handicap,
                                                 order=index)
            bowler_instance.save()
            index += 1

    def bowlers_defined(self):
        league = self.match.week.league

        return len(self.bowlers) == league.players_per_team

    def create_games(self):
        definitions = []

        for bowler in self.bowlers.all():
            games = bowler.get_or_create_games()
            definitions.append(dict(bowler=bowler, games=games))

        return definitions


class TeamInstanceBowler(models.Model):
    """
    The instance of a bowler that is bowling on a given week
    """
    definition = models.ForeignKey(BowlerDefinition)
    team = models.ForeignKey(TeamInstance, related_name='bowlers')
    type = models.CharField(max_length=10, blank=False, choices=BOWLER_TYPE_CHOICES, default=REGULAR)
    handicap = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(blank=False)

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return '%s %s %s' % (self.definition.league, self.team.definition.name, self.definition.name)

    def get_or_create_games(self):
        games = self.games.all()

        if len(games) == self.definition.league.number_of_games:
            return games

        games = []

        for game_index in range(0, self.definition.league.number_of_games):
            game = Game(bowler=self, game_number=game_index+1)
            game.save()
            games.append(game)

        return games


class Match(models.Model):
    """
    Class that will define a match that is being recorded.
    """
    week = models.ForeignKey(Week, related_name='matches')
    lanes = models.CommaSeparatedIntegerField(blank=True, max_length=7)
    games_created = models.BooleanField(blank=False, default=False)
    teams = models.ManyToManyField(TeamDefinition, through=TeamInstance)

    def get_absolute_url(self):
        return reverse('bowling_entry_matchdetails', args=[self.pk])

    def get_games(self):

        results = []

        for team in self.teams.all():
            team_instance = TeamInstance.objects.get(match=self, definition=team)
            bowler_games = team_instance.create_games()
            results.append(dict(team=team, bowlers=bowler_games))

        self.games_created = True
        self.save()

        return results


class Game(models.Model):
    """
    Collection of all of the frames that were bowled by the bowler.
    """
    bowler = models.ForeignKey(TeamInstanceBowler, blank=False, null=False, related_name='games')
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
            self.frame02 = score
        elif frame_id == 3:
            self.frame03 = score
        elif frame_id == 4:
            self.frame04 = score
        elif frame_id == 5:
            self.frame05 = score
        elif frame_id == 6:
            self.frame06 = score
        elif frame_id == 7:
            self.frame07 = score
        elif frame_id == 8:
            self.frame08 = score
        elif frame_id == 9:
            self.frame09 = score
        elif frame_id == 10:
            self.frame10 = score

    def set_split(self, frame_id, is_split):
        if self.splits:
            splits = {int(a) for a in self.splits.split(',')}
        else:
            splits = set()

        if is_split:
            splits.add(frame_id)
        elif frame_id in splits:
            splits.remove(frame_id)

        self.splits = ','.join([str(a) for a in splits])

    def is_split(self, frame_id):
        return frame_id in self.get_splits()

    def get_splits(self):
        if self.splits:
            splits = {int(a) for a in self.splits.split(',')}
        else:
            splits = set()

        return splits

