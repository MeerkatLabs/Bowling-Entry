from rest_framework import serializers
from bowling_entry import models as bowling_models
from django.contrib.auth import models as auth_models


class LeagueTeams(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, object):
        return self.context['request'].build_absolute_uri(object.get_absolute_url())

    class Meta:
        model = bowling_models.TeamDefinition
        fields = ('id', 'name', 'url', )


class LeagueWeeks(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, object):
        return self.context['request'].build_absolute_uri(object.get_absolute_url())

    class Meta:
        model = bowling_models.Week
        fields = ('id', 'date', 'url', )


class League(serializers.ModelSerializer):
    teams = LeagueTeams(many=True, read_only=True)
    weeks = LeagueWeeks(many=True, read_only=True)

    class Meta:
        model = bowling_models.League
        fields = ('id', 'name', 'start_date', 'number_of_weeks', 'number_of_games', 'players_per_team',
                  'points_per_game', 'points_for_totals', 'handicap_max', 'handicap_percentage', 'teams', 'weeks')


class Week(serializers.ModelSerializer):
    matches = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = bowling_models.Week
        fields = ('id', 'week_number', 'date', 'matches', )


class TeamBowlerDefinition(serializers.ModelSerializer):

    class Meta:
        model = bowling_models.BowlerDefinition
        fields = ('id', 'name', 'handicap', )


class TeamDefinition(serializers.ModelSerializer):
    league = serializers.ReadOnlyField(source='league.name')
    bowlers = TeamBowlerDefinition(read_only=True, many=True)

    class Meta:
        model = bowling_models.TeamDefinition
        fields = ('id', 'league', 'name', 'bowlers', )


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


class TeamInstanceBowlerInstanceListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):

        ret = []

        for bowler in validated_data:
            print '%s' % bowler
            bowler_instance = instance.get(pk=bowler.get('id'))
            self.child.update(bowler_instance, bowler)
            ret.append(bowler_instance)

        return ret


class TeamInstanceBowlerInstance(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = bowling_models.TeamInstanceBowler
        fields = ('id', 'definition', 'type', )
        list_serializer_class = TeamInstanceBowlerInstanceListSerializer

    def update(self, instance, validated_data):

        print 'validated_data: %s' % validated_data

        definition = validated_data.get('definition')
        instance.update_definition(definition, validated_data.get('type'))

        return instance


class TeamInstance(serializers.ModelSerializer):
    name = serializers.CharField(source='definition.name')
    bowlers = TeamInstanceBowlerInstance(many=True, read_only=True)
    definition_id = serializers.PrimaryKeyRelatedField(source='definition.id', read_only=True)

    class Meta:
        model = bowling_models.TeamInstance
        fields = ('id', 'name', 'bowlers', 'definition_id', )


class MatchTeam(serializers.ModelSerializer):
    name = serializers.CharField(source='definition.name', read_only=True)
    bowlers = TeamInstanceBowlerInstance(many=True)
    definition_id = serializers.PrimaryKeyRelatedField(source='definition.id', read_only=True)

    class Meta:
        model = bowling_models.TeamInstance
        fields = ('id', 'name', 'bowlers', 'definition_id', )

    def update(self, instance, validated_data):

        self.fields['bowlers'].update(instance.bowlers.all(), validated_data.get('bowlers'))

        return instance



class Match(serializers.ModelSerializer):
    week = serializers.PrimaryKeyRelatedField(read_only=True)
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
        fields = ('id', 'week', 'lanes', 'team1', 'team2', 'team1_definition', 'team2_definition', )

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
                raise serializers.ValidationError('%s already has a match the week of %s' % (team01, week))
            elif match.team2.definition.pk == team02.pk:
                raise serializers.ValidationError('%s already has a match the week of %s' % (team01, week))

        return data


class TeamBowlerInstance(serializers.ModelSerializer):

    class Meta:
        model = bowling_models.TeamInstanceBowler
        fields = ('id', 'definition', 'type', )


class User(serializers.ModelSerializer):

    class Meta:
        model = auth_models.User
        fields = ('username', 'first_name', 'last_name', 'email', )
