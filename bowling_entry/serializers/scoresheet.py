from rest_framework import serializers
from bowling_entry import models as bowling_models


class ScoreSheetFrameListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):
        # Break apart the valid data and call update on self.child
        return []

class ScoreSheetFrame(serializers.ModelSerializer):

    class Meta:
        model = bowling_models.Frame
        fields = ('frame_number', 'throws', )
        list_serializer_class = ScoreSheetFrameListSerializer


class ScoreSheetGameListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):
        # Break apart the valid data and call update on self.child
        return []


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
        # Update the frames, total, and splits (if the frame is defined).
        return []


class ScoreSheetBowlerListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):

        ret = []
        for i in instance.all():
            print '%s' % i

        for bowler_data in validated_data:
            print 'Updating bowler: %s' % bowler_data.get('id')
            bowler = bowling_models.TeamInstanceBowler.objects.get(pk=bowler_data.get('id'))
            print 'Updating bowler: %s' % bowler.definition.name
            print 'bd: %s' % bowler_data
            self.child.update(bowler, bowler_data)

        return ret


class ScoreSheetBowler(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='definition.name', read_only=True)
    games = ScoreSheetGame(many=True)

    class Meta:
        model = bowling_models.TeamInstanceBowler
        fields = ('id', 'name', 'games', )
        list_serializer_class = ScoreSheetBowlerListSerializer

    def update(self, instance, validated_data):
        print 'updating the bowler'
        return None


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
    team1 = ScoreSheetTeam()
    team2 = ScoreSheetTeam()

    class Meta:
        model = bowling_models.Match
        fields = ('id', 'lanes', 'team1', 'team2', )

    def update(self, instance, validated_data):

        instance.lanes = validated_data.get('lanes')

        team1_definition = validated_data.get('team1')
        self.fields['team1'].update(instance.team1, team1_definition)

        team2_definition = validated_data.get('team2')

        print '%s' % dir(self.fields)

        return instance


    def validate(self, attrs):

        print '%s' % attrs

        return attrs

