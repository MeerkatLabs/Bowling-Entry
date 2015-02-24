from rest_framework import serializers
from bowling_entry import models as bowling_models
from django.contrib.auth import models as auth_models


class League(serializers.ModelSerializer):
    teams = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    weeks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = bowling_models.League
        fields = ('id', 'name', 'number_of_weeks', 'number_of_games', 'players_per_team', 'points_per_game',
                  'points_for_totals', 'handicap_max', 'handicap_percentage', 'teams', 'weeks')


class Week(serializers.ModelSerializer):
    matches = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = bowling_models.Week
        fields = ('id', 'date', 'matches', )


class TeamDefinition(serializers.ModelSerializer):
    league = serializers.ReadOnlyField(source='league.name')

    class Meta:
        model = bowling_models.TeamDefinition
        fields = ('id', 'league', 'name', )


class TeamBowlerDefinition(serializers.ModelSerializer):

    class Meta:
        model = bowling_models.BowlerDefinition
        fields = ('id', 'name', 'handicap')


class BowlerDefinition(serializers.ModelSerializer):
    team = serializers.ReadOnlyField(source='team.name')
    league = serializers.ReadOnlyField(source='league.name')

    class Meta:
        model = bowling_models.BowlerDefinition
        fields = ('id', 'name', 'handicap', 'league', 'team')


class Substitute(serializers.ModelSerializer):
    league = serializers.ReadOnlyField(source='league.name')

    class Meta:
        model = bowling_models.BowlerDefinition
        fields = ('id', 'name', 'handicap', 'league', )


class MatchCreate(serializers.Serializer):
    week = serializers.PrimaryKeyRelatedField(read_only=True)
    lane01 = serializers.IntegerField(required=True)
    lane02 = serializers.IntegerField(required=True)
    team01 = serializers.PrimaryKeyRelatedField(queryset=bowling_models.TeamDefinition.objects.all())
    team02 = serializers.PrimaryKeyRelatedField(queryset=bowling_models.TeamDefinition.objects.all())

    def create(self, validated_data):
        print 'Validated_data %s' % validated_data

        lanes = '%s,%s' % (validated_data.get('lane01'), validated_data.get('lane02'))
        match = bowling_models.Match(week=validated_data.get('week'), lanes=lanes)
        match.save()

        team01 = validated_data['team01']
        team01_instance = bowling_models.TeamInstance(definition=team01, match=match)
        team01_instance.save()
        team01_instance.define_bowlers()

        team02_instance = validated_data['team02']
        team02_instance = bowling_models.TeamInstance(definition=team02_instance, match=match)
        team02_instance.save()
        team02_instance.define_bowlers()

        return dict(week=validated_data.get('week'),
                    lane01=validated_data.get('lane01'),
                    lane02=validated_data.get('lane02'),
                    team01=validated_data.get('team01'),
                    team02=validated_data.get('team02'))

    def update(self, instance, validated_data):

        week = instance.get('week')

        lanes = '%s,%s' % (validated_data.get('lane01'), validated_data.get('lane02'))
        match = bowling_models.Match(week=week, lanes=lanes)
        match.save()

        team01 = validated_data['team01']
        team01_instance = bowling_models.TeamInstance(definition=team01, match=match)
        team01_instance.save()
        team01_instance.define_bowlers()

        team02_instance = validated_data['team02']
        team02_instance = bowling_models.TeamInstance(definition=team02_instance, match=match)
        team02_instance.save()
        team02_instance.define_bowlers()

        return dict(week=instance.get('week'),
                    lane01=validated_data.get('lane01'),
                    lane02=validated_data.get('lane02'),
                    team01=validated_data.get('team01'),
                    team02=validated_data.get('team02'))

    def validate(self, data):
        print '%s' % self.instance

        week = self.instance.get('week')

        league = week.league

        team01 = data.get('team01')
        team02 = data.get('team02')

        if team01.league.pk != league.pk:
            raise serializers.ValidationError('Team 1 is not a part of the same league as the week')
        elif team02.league.pk != league.pk:
            raise serializers.ValidationError('Team 2 is not a part of the same league as the week')
        elif team01 == team02:
            raise serializers.ValidationError('The same team cannot play against each other')
        elif data.get('lane01') != data.get('lane02') - 1:
            raise serializers.ValidationError('The lanes are not next to each other')

        for match in week.matches.all():
            for team in match.teams.all():
                if team == team01:
                    raise serializers.ValidationError('%s already has a match the week of %s' % (team01, week))
                elif team == team02:
                    raise serializers.ValidationError('%s already has a match the week of %s' % (team01, week))

        return data


class Match(serializers.ModelSerializer):
    week = serializers.ReadOnlyField(source='week.date')
    teams = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = bowling_models.Match
        fields = ('id', 'week', 'lanes', 'teams')


class TeamInstance(serializers.ModelSerializer):

    name = serializers.CharField(source='definition.name')
    bowlers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = bowling_models.TeamInstance
        fields = ('id', 'name', 'bowlers', )


class TeamBowlerInstance(serializers.ModelSerializer):

    class Meta:
        model = bowling_models.TeamInstanceBowler
        fields = ('id', 'definition', 'type', )


class Game(serializers.ModelSerializer):
    class Meta:
        model = bowling_models.Game
        fields = ('id', 'bowler', 'game_number', 'frame01', 'frame02', 'frame03', 'frame04', 'frame05', 'frame06',
                  'frame07', 'frame08', 'frame09', 'frame10', 'splits')


class MatchBowlerGame(serializers.ModelSerializer):
    class Meta:
        model = bowling_models.Game


class MatchTeam(serializers.Serializer):
    bowler = serializers.PrimaryKeyRelatedField(read_only=True)
    games = MatchBowlerGame(read_only=True, many=True)


class MatchGames(serializers.Serializer):
    team = serializers.PrimaryKeyRelatedField(read_only=True)
    bowlers = MatchTeam(read_only=True, many=True)


class User(serializers.ModelSerializer):

    class Meta:
        model = auth_models.User
        fields = ('username', 'first_name', 'last_name', 'email', )
