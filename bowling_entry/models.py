from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import datetime

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
    start_date = models.DateField(default=datetime.date.today)
    number_of_weeks = models.IntegerField(blank=False, default=10)
    number_of_games = models.IntegerField(blank=False, default=3)
    players_per_team = models.IntegerField(blank=False, default=4)
    points_per_game = models.IntegerField(blank=False, default=2)
    points_for_totals = models.IntegerField(blank=False, default=2)
    handicap_max = models.IntegerField(blank=False, default=210)
    handicap_percentage = models.IntegerField(blank=False, default=90)

    class Meta:
        ordering = ['start_date', 'name', ]

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
    week_number = models.IntegerField(default=1)

    class Meta:
        unique_together = (('league', 'week_number'),)
        ordering = ['date', ]

    def __unicode__(self):
        return "%s: %s" % (self.league, self.date)

    def get_absolute_url(self):
        return reverse('bowling_entry_league_week_detail', args=[self.league.pk, self.week_number])


class TeamDefinition(models.Model):
    """
    Definition of a team.  This will be used to define what team will be used from week to week
    """
    name = models.CharField(max_length=100)
    league = models.ForeignKey(League, related_name='teams', blank=False)

    def __unicode__(self):
        return "%s: %s" % (self.league, self.name)

    def get_absolute_url(self):
        return reverse('bowling_entry_league_team_detail', args=[self.league.pk, self.pk])


class BowlerDefinition(models.Model):
    """
    Definition of a bowler that will participate in the league.
    """
    name = models.CharField(max_length=100)
    average = models.IntegerField(blank=True, null=True)
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

    def define(self):
        self.define_bowlers()

    def define_bowlers(self):
        """
        Define all of the bowlers to be associated with this team.  Iterates through the team definition for this
        instance.  Fills in vacant bowlers if there are not enough bowlers available.
        """
        index = 0
        league = self.match.week.league

        max_bowlers = league.players_per_team

        # Assume the bowler definition based on the team definition values.
        for bowler in self.definition.bowlers.all():
            bowler_instance = TeamInstanceBowler(definition=bowler, team=self,
                                                 type=REGULAR, handicap=bowler.handicap,
                                                 order=index)
            bowler_instance.save()
            bowler_instance.create_games()
            index += 1

            # Break out of the loop if the maximum number of bowlers has been reached.
            if index >= max_bowlers:
                break

        # Create the vacant bowlers
        for vacant_index in range(index, max_bowlers):
            bowler_instance = TeamInstanceBowler(definition=None, team=self,
                                                 type=VACANT, order=vacant_index)
            bowler_instance.save()
            bowler_instance.create_games()

    def clear_games(self):
        for bowler in self.bowlers.all():
            for game in bowler.games.all():
                game.delete()
            bowler.delete()


class TeamInstanceBowler(models.Model):
    """
    The instance of a bowler that is bowling on a given week
    """
    definition = models.ForeignKey(BowlerDefinition, null=True)
    team = models.ForeignKey(TeamInstance, related_name='bowlers')
    type = models.CharField(max_length=10, blank=False, choices=BOWLER_TYPE_CHOICES, default=REGULAR)
    average = models.IntegerField(blank=True, null=True)
    handicap = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(blank=False)

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return '%s %s %s (I)' % (self.definition.league, self.team.definition.name, self.definition.name)

    def create_games(self):
        game_count = self.definition.league.number_of_games

        for game_number in range(1, game_count+1):
            game = Game(bowler=self, game_number=game_number)
            game.save()

    def update_definition(self, definition, bowler_type=SUBSTITUTE):
        self.definition = definition
        self.type = bowler_type
        self.handicap = definition.handicap
        self.average = definition.average
        self.save()


class Match(models.Model):
    """
    Class that will define a match that is being recorded.
    """
    week = models.ForeignKey(Week, related_name='matches')
    lanes = models.CommaSeparatedIntegerField(blank=True, max_length=7)
    team1 = models.ForeignKey(TeamInstance, related_name='+', null=True)
    team2 = models.ForeignKey(TeamInstance, related_name='+', null=True)

    def get_absolute_url(self):
        return reverse('bowling_entry_matchdetails', args=[self.pk])

    def create_games(self):
        self.team1.define()
        self.team2.define()

    def clear_games(self):
        self.team1.clear_games()
        self.team2.clear_games()


class Game(models.Model):
    """
    Collection of all of the frames that were bowled by the bowler.
    """
    bowler = models.ForeignKey(TeamInstanceBowler, blank=False, null=False, related_name='games')
    game_number = models.IntegerField(blank=False)
    total = models.IntegerField(blank=False, default=0)


class Frame(models.Model):
    game = models.ForeignKey(Game, related_name='frames')
    frame_number = models.IntegerField(blank=False)
    throws = models.CommaSeparatedIntegerField(max_length=10, blank=False)
    splits = models.CommaSeparatedIntegerField(max_length=10, blank=True)

    class Meta:
        ordering = ['frame_number', ]