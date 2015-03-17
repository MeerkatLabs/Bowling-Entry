from rest_framework import serializers
from bowling_entry import models as bowling_models


class ScoreSheetFrameListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):
        ret = []

        for frame_data in validated_data:
            frame, created = instance.get_or_create(frame_number=frame_data.get('frame_number'),
                                                    defaults={'throws': ''})
            result = self.child.update(frame, frame_data)

            if result is not None:
                ret.append(result)

        return ret


class ScoreSheetFrame(serializers.ModelSerializer):

    class Meta:
        model = bowling_models.Frame
        fields = ('frame_number', 'throws', )
        list_serializer_class = ScoreSheetFrameListSerializer

    def update(self, instance, validated_data):

        print '%s' % validated_data
        print '%s' % instance

        instance.throws = validated_data.get('throws')
        instance.save()

        return instance

    def validate(self, attrs):
        # frame_number must be provided, same with throws
        if attrs.get('frame_number') is None:
            raise serializers.ValidationError('frame_number must be provided')
        elif attrs.get('throws') is None:
            raise serializers.ValidationError('throws must be provided')
        return attrs


class ScoreSheetGameListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):
        ret = []

        for game_data in validated_data:
            game = instance.get(game_number=game_data.get('game_number'))
            result = self.child.update(game, game_data)

            if result is not None:
                ret.append(result)

        return ret

    def get_attribute(self, instance):
        result = super(ScoreSheetGameListSerializer, self).get_attribute(instance)
        return result.prefetch_related('frames')


class ScoreSheetGame(serializers.ModelSerializer):
    game_number = serializers.IntegerField()
    total = serializers.IntegerField()
    frames = ScoreSheetFrame(many=True)
    splits = serializers.SerializerMethodField()

    class Meta:
        model = bowling_models.Game
        fields = ('game_number', 'total', 'frames', 'splits', )
        list_serializer_class = ScoreSheetGameListSerializer

    def get_splits(self, obj):

        splits = []
        for frame in obj.frames.all():
            for split in frame.splits.split(','):
                splits.append(split)

        return splits

    def update(self, instance, validated_data):

        # Only fields that we are going to update are the totals
        total_value = validated_data.get('total')
        if total_value is not None:
            instance.total = total_value
        instance.save()

        # TODO: Update the split and frame values.
        frame_data = validated_data.get('frames')
        if frame_data is not None:
            self.fields['frames'].update(instance.frames, frame_data)

        return instance

    def validate(self, attrs):
        # game_number must always be provided
        if attrs.get('game_number') is None:
            raise serializers.ValidationError('game_number must be provided')
        return attrs


class ScoreSheetBowlerListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):

        ret = []

        for bowler_data in validated_data:
            bowler = instance.get(pk=bowler_data.get('id'))
            result = self.child.update(bowler, bowler_data)

            if result is not None:
                ret.append(result)

        return ret

    def get_attribute(self, instance):
        result = super(ScoreSheetBowlerListSerializer, self).get_attribute(instance)
        return result.prefetch_related('games')


class ScoreSheetBowler(serializers.ModelSerializer):
    id = serializers.IntegerField()
    definition = serializers.PrimaryKeyRelatedField(queryset=bowling_models.BowlerDefinition.objects)
    handicap = serializers.IntegerField(read_only=True)
    average = serializers.IntegerField(read_only=True)
    type = serializers.CharField()
    name = serializers.CharField(source='definition.name', read_only=True)
    games = ScoreSheetGame(many=True)
    total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = bowling_models.TeamInstanceBowler
        fields = ('id', 'definition', 'name', 'type', 'handicap', 'average', 'games', 'total', )
        list_serializer_class = ScoreSheetBowlerListSerializer

    def update(self, instance, validated_data):
        # There is nothing to update here (don't want to change any of the values of the bowler).
        # instead do want to update the games.

        games = validated_data.get('games')
        if games is not None:
            self.fields['games'].update(instance.games, games)

        definition = validated_data.get('definition')
        type = validated_data.get('type')
        if definition is not None and type is not None:
            instance.update_definition(definition, type)

        return instance

    def get_total(self, bowler):
        total = 0
        for game in bowler.games.all():
            total += game.total

        return total

    def validate_definition(self, value):
        # definition object must either be a member of the team or a league substitute
        print 'validating definition'
        return value

    def validate(self, attrs):
        # id must always be present
        if attrs.get('id') is None:
            raise serializers.ValidationError("Bowler Id must always be present")

        print '%s' % attrs

        # definition and bowler type must be defined together
        if attrs.get('definition') is not None and attrs.get('type') is None:
            raise serializers.ValidationError('Bowler definition and type must be present together (type missing)')
        elif attrs.get('type') is not None and attrs.get('definition') is None:
            raise serializers.ValidationError('Bowler definition and type must be present together (definition missing)')

        return attrs


class ScoreSheetTeam(serializers.ModelSerializer):
    name = serializers.CharField(source='definition.name', read_only=True)
    bowlers = ScoreSheetBowler(many=True)
    definition_id = serializers.PrimaryKeyRelatedField(source='definition.id', read_only=True)

    class Meta:
        model = bowling_models.TeamInstance
        fields = ('id', 'name', 'bowlers', 'definition_id', )

    def update(self, instance, validated_data):

        bowlers = validated_data.get('bowlers')

        self.fields['bowlers'].update(instance.bowlers, bowlers)

        return instance


class ScoreSheet(serializers.ModelSerializer):
    team1 = ScoreSheetTeam()
    team2 = ScoreSheetTeam()

    class Meta:
        model = bowling_models.Match
        fields = ('id', 'lanes', 'team1', 'team2', )

    def update(self, instance, validated_data):

        instance.lanes = validated_data.get('lanes')

        team1_definition = validated_data.get('team1')
        if team1_definition is not None:
            self.fields['team1'].update(instance.team1, team1_definition)

        team2_definition = validated_data.get('team2')
        if team2_definition is not None:
            self.fields['team2'].update(instance.team2, team2_definition)

        return instance