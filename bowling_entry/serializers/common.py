from rest_framework import serializers
from bowling_entry import models as bowling_models
from django.contrib.auth import models as auth_models


class LeagueTeams(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, instance):
        return self.context['request'].build_absolute_uri(instance.get_absolute_url())

    class Meta:
        model = bowling_models.TeamDefinition
        fields = ('id', 'name', 'url', )


class LeagueWeeks(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, instance):
        return self.context['request'].build_absolute_uri(instance.get_absolute_url())

    class Meta:
        model = bowling_models.Week
        fields = ('week_number', 'date', 'url', )


class League(serializers.ModelSerializer):
    teams = LeagueTeams(many=True, read_only=True)
    weeks = LeagueWeeks(many=True, read_only=True)

    class Meta:
        model = bowling_models.League
        fields = ('id', 'name', 'start_date', 'number_of_weeks', 'number_of_games', 'players_per_team',
                  'points_per_game', 'points_for_totals', 'handicap_max', 'handicap_percentage', 'teams', 'weeks')


class LeagueList(serializers.ModelSerializer):

    class Meta:
        model = bowling_models.League
        fields = ('id', 'name', 'start_date', 'number_of_weeks', 'number_of_games', 'players_per_team',
                  'points_per_game', 'points_for_totals', 'handicap_max', 'handicap_percentage')
        extra_kwargs = {'number_of_weeks': {'write_only': True},
                        'number_of_games': {'write_only': True},
                        'players_per_team': {'write_only': True},
                        'points_per_game': {'write_only': True},
                        'points_for_totals': {'write_only': True},
                        'handicap_max': {'write_only': True},
                        'handicap_percentage': {'write_only': True}}


class Week(serializers.ModelSerializer):
    matches = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = bowling_models.Week
        fields = ('week_number', 'date', 'matches', )


class TeamBowlerDefinition(serializers.ModelSerializer):

    class Meta:
        model = bowling_models.BowlerDefinition
        fields = ('id', 'name', 'handicap', )


class TeamDefinition(serializers.ModelSerializer):
    bowlers = TeamBowlerDefinition(read_only=True, many=True)

    class Meta:
        model = bowling_models.TeamDefinition
        fields = ('id', 'league', 'name', 'bowlers', )


class BowlerDefinition(serializers.ModelSerializer):

    class Meta:
        model = bowling_models.BowlerDefinition
        fields = ('id', 'name', 'gender', 'handicap', 'team', )

    def update(self, instance, validated_data):
        """
        Update the object and remove the team if the context item is provided.
        :param instance:
        :param validated_data:
        :return:
        """
        _instance = super(BowlerDefinition, self).update(instance, validated_data)

        # Need to clear out the team if it was requested in the query string
        if self.context.get('remove_team', False):
            _instance.team = None
            _instance.save()

        return _instance

    def validate_team(self, value):
        """
        Need to make sure that the team is defined in the league that this object is already defined in.
        :param attrs:
        :return:
        """
        league = self.context.get('league')
        team = league.teams.filter(pk=value.pk)
        if not len(team):
            raise serializers.ValidationError('Team is not apart of the current league')

        return value


class Substitute(serializers.ModelSerializer):
    league = serializers.ReadOnlyField(source='league.name')

    class Meta:
        model = bowling_models.BowlerDefinition
        fields = ('id', 'name', 'handicap', 'league', )


class TeamInstance(serializers.ModelSerializer):
    name = serializers.CharField(source='definition.name')
    id = serializers.PrimaryKeyRelatedField(source='definition.id', read_only=True)

    class Meta:
        model = bowling_models.TeamInstance
        fields = ('id', 'name', )


class Match(serializers.ModelSerializer):
    team1 = TeamInstance(read_only=True)
    team2 = TeamInstance(read_only=True)
    team1_definition = serializers.PrimaryKeyRelatedField(write_only=True,
                                                          source='team1.definition',
                                                          queryset=bowling_models.TeamDefinition.objects.all())
    team2_definition = serializers.PrimaryKeyRelatedField(write_only=True,
                                                          source='team2.definition',
                                                          queryset=bowling_models.TeamDefinition.objects.all())

    class Meta:
        model = bowling_models.Match
        fields = ('id', 'lanes', 'team1', 'team2', 'team1_definition', 'team2_definition', )

    def update(self, instance, validated_data):
        print 'Validated_data %s' % validated_data
        print 'Context %s' % self.context

        print 'Week: %s' % self.context.get('week')

        instance.week = self.context.get('week')
        instance.lanes = validated_data['lanes']

        team01 = validated_data.pop('team1')
        instance.team1.definition = team01['definition']
        instance.team1.save()

        team02 = validated_data.pop('team2')
        instance.team2.definition = team02['definition']
        instance.team2.save()

        instance.save()

        instance.clear_games()
        instance.create_games()

        return instance

    def create(self, validated_data):
        print 'Validated_data %s' % validated_data
        print 'Context %s' % self.context

        print 'Week: %s' % self.context.get('week')

        match = bowling_models.Match(week=self.context.get('week'), lanes=validated_data['lanes'])
        match.save()

        team01 = validated_data.pop('team1')
        team01_instance = bowling_models.TeamInstance(definition=team01['definition'], match=match)
        team01_instance.save()
        team01_instance.define_bowlers()

        team02 = validated_data.pop('team2')
        team02_instance = bowling_models.TeamInstance(definition=team02['definition'], match=match)
        team02_instance.save()
        team02_instance.define_bowlers()

        match.team1 = team01_instance
        match.team2 = team02_instance
        match.save()

        return match

    def validate(self, data):
        print '%s' % data

        print 'Self: %s' % dir(self)

        week = self.context.get('week')

        league = self.context.get('league')

        team01 = data.get('team1')['definition']
        team02 = data.get('team2')['definition']

        lane01, lane02 = data.get('lanes').split(',')

        print '%s' % league

        if week.league.pk != league.pk:
            raise serializers.ValidationError('Week is not a part of the league.')
        elif team01.league.pk != league.pk:
            raise serializers.ValidationError('Team 1 is not a part of the correct league')
        elif team02.league.pk != league.pk:
            raise serializers.ValidationError('Team 2 is not a part of the correct league')
        elif team01 == team02:
            raise serializers.ValidationError('The same team cannot play against each other')
        elif int(lane01) != int(lane02) - 1:
            raise serializers.ValidationError('The lanes are not next to each other')

        for match in week.matches.all():
            if self.instance is not None and match.pk == self.instance.pk:
                continue

            if match.team1.definition.pk == team01.pk:
                raise serializers.ValidationError('%s already has a match the week of %s' % (team01, week))
            elif match.team2.definition.pk == team01.pk:
                raise serializers.ValidationError('%s already has a match the week of %s' % (team01, week))
            elif match.team1.definition.pk == team02.pk:
                raise serializers.ValidationError('%s already has a match the week of %s' % (team02, week))
            elif match.team2.definition.pk == team02.pk:
                raise serializers.ValidationError('%s already has a match the week of %s' % (team02, week))

        return data


class TeamBowlerInstance(serializers.ModelSerializer):

    class Meta:
        model = bowling_models.TeamInstanceBowler
        fields = ('id', 'definition', 'type', )


class User(serializers.ModelSerializer):

    class Meta:
        model = auth_models.User
        fields = ('username', 'first_name', 'last_name', 'email', )
