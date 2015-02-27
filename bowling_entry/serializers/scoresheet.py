from rest_framework import serializers
from bowling_entry import models as bowling_models


class ScoreSheetFrameListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):
        ret = []

        for frame_data in validated_data:
            frame, created = instance.get_or_create(frame_number=frame_data.get('frame_number'), defaults={'throws': ''})
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


class ScoreSheetGameListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):
        ret = []

        for game_data in validated_data:
            game = instance.get(game_number=game_data.get('game_number'))
            result = self.child.update(game, game_data)

            if result is not None:
                ret.append(result)

        return ret


class ScoreSheetGame(serializers.ModelSerializer):
    game_number = serializers.IntegerField()
    total = serializers.IntegerField(required=False)
    frames = ScoreSheetFrame(many=True, required=False)
    splits = serializers.SerializerMethodField(required=False)

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

        ## Only fields that we are going to update are the totals
        total_value = validated_data.get('total')
        if total_value is not None:
            instance.total = total_value
        instance.save()

        ## TODO: Update the split and frame values.
        frame_data = validated_data.get('frames')
        if frame_data is not None:
            self.fields['frames'].update(instance.frames, frame_data)

        return instance


class ScoreSheetBowlerListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):

        ret = []

        for bowler_data in validated_data:
            bowler = instance.get(pk=bowler_data.get('id'))
            result = self.child.update(bowler, bowler_data)

            if result is not None:
                ret.append(result)

        return ret


class ScoreSheetBowler(serializers.ModelSerializer):
    id = serializers.IntegerField()
    handicap = serializers.IntegerField(read_only=True)
    type = serializers.CharField(read_only=True)
    name = serializers.CharField(source='definition.name', read_only=True)
    games = ScoreSheetGame(many=True)
    total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = bowling_models.TeamInstanceBowler
        fields = ('id', 'name', 'type', 'handicap', 'games', 'total', )
        list_serializer_class = ScoreSheetBowlerListSerializer

    def update(self, instance, validated_data):
        # There is nothing to update here (don't want to change any of the values of the bowler).
        # instead do want to update the games.

        games = validated_data.get('games')
        self.fields['games'].update(instance.games, games)

        return instance

    def get_total(self, object):
        total = 0
        for game in object.games.all():
            total += game.total

        return total


class ScoreSheetTeam(serializers.ModelSerializer):
    name = serializers.CharField(source='definition.name', read_only=True)
    bowlers = ScoreSheetBowler(many=True)

    class Meta:
        model = bowling_models.TeamInstance
        fields = ('id', 'name', 'bowlers', )

    def update(self, instance, validated_data):

        bowlers = validated_data.get('bowlers')

        self.fields['bowlers'].update(instance.bowlers, bowlers)

        return instance


class ScoreSheet(serializers.ModelSerializer):
    team1 = ScoreSheetTeam(required=False)
    team2 = ScoreSheetTeam(required=False)

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

    def validate(self, attrs):
        return attrs

