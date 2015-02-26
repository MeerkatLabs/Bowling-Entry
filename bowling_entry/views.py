from bowling_entry import models as bowling_models
from rest_framework import generics, response
from bowling_entry import serializers as bowling_serializers
from django.shortcuts import get_object_or_404


class LeagueListCreate(generics.ListCreateAPIView):
    queryset = bowling_models.League.objects.all()
    serializer_class = bowling_serializers.League

    def perform_create(self, serializer):
        serializer.save(secretary=self.request.user)


class LeagueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = bowling_models.League.objects.all()
    serializer_class = bowling_serializers.League


class LeagueMixin():
    """
    Mixin that should make looking up related items easier.
    """
    league_url_kwarg = 'league_pk'
    league_lookup_field = 'pk'
    league_queryset = bowling_models.League.objects.all()

    def get_league_queryset(self):
        return self.league_queryset

    def get_league(self):
        filter_kwargs = {self.league_lookup_field: self.kwargs[self.league_url_kwarg]}
        obj = get_object_or_404(self.get_league_queryset(), **filter_kwargs)

        return obj


class TeamDefinitionListCreate(generics.ListCreateAPIView, LeagueMixin):
    serializer_class = bowling_serializers.TeamDefinition

    def get_queryset(self):
        return self.get_league().teams

    def perform_create(self, serializer):
        serializer.save(league=self.get_league())


class TeamDetail(generics.RetrieveUpdateDestroyAPIView, LeagueMixin):
    serializer_class = bowling_serializers.TeamDefinition

    def get_queryset(self):
        return self.get_league().teams

    def perform_update(self, serializer):
        serializer.save(league=self.get_league())


class TeamMixin(LeagueMixin):
    """
    Mixin that should make looking up related items easier.
    """
    team_url_kwarg = 'team_pk'
    team_lookup_field = 'pk'
    team_queryset = bowling_models.League.objects.all()

    def get_team_queryset(self):
        return self.get_league().teams

    def get_team(self):
        filter_kwargs = {self.team_lookup_field: self.kwargs[self.team_url_kwarg]}
        obj = get_object_or_404(self.get_team_queryset(), **filter_kwargs)

        return obj


class TeamBowlerDefinitionListCreate(generics.ListCreateAPIView, TeamMixin):
    serializer_class = bowling_serializers.TeamBowlerDefinition
    team_url_kwarg = 'pk'

    def get_queryset(self):
        return bowling_models.BowlerDefinition.objects.filter(team=self.get_team())

    def perform_create(self, serializer):
        serializer.save(team=self.get_team(), league=self.get_league())


class TeamBowlerDefinitionDetail(generics.RetrieveUpdateDestroyAPIView, TeamMixin):
    serializer_class = bowling_serializers.TeamBowlerDefinition

    def get_queryset(self):
        return bowling_models.BowlerDefinition.objects.filter(league=self.get_league())

    def perform_update(self, serializer):
        serializer.save(team=self.get_team(), league=self.get_league())


class SubstitutesList(generics.ListCreateAPIView, LeagueMixin):
    serializer_class = bowling_serializers.Substitute

    def get_queryset(self):
        return self.get_league().substitutes()

    def perform_create(self, serializer):
        serializer.save(league=self.get_league(), team=None)


class SubstituteDetail(generics.RetrieveUpdateDestroyAPIView, LeagueMixin):
    serializer_class = bowling_serializers.Substitute

    def get_queryset(self):
        return self.get_league().substitutes()


class WeekCreateList(generics.ListCreateAPIView, LeagueMixin):
    serializer_class = bowling_serializers.Week

    def get_queryset(self):
        return self.get_league().weeks

    def perform_create(self, serializer):
        serializer.save(league=self.get_league())


class WeekDetail(generics.RetrieveUpdateDestroyAPIView, LeagueMixin):
    serializer_class = bowling_serializers.Week

    def get_queryset(self):
        return self.get_league().weeks

    def perform_update(self, serializer):
        serializer.save(league=self.get_league())


class WeekMixin(LeagueMixin):
    week_url_kwarg = 'week_pk'
    week_lookup_field = 'pk'
    week_queryset = bowling_models.League.objects.all()

    def get_week_queryset(self):
        return self.get_league().weeks

    def get_week(self):
        filter_kwargs = {self.week_lookup_field: self.kwargs[self.week_url_kwarg]}
        obj = get_object_or_404(self.get_week_queryset(), **filter_kwargs)

        return obj


class MatchList(generics.ListCreateAPIView, WeekMixin):
    serializer_class = bowling_serializers.Match

    def get_queryset(self):
        return self.get_week().matches

    def get_serializer_context(self):
        context = super(MatchList, self).get_serializer_context()

        context['week'] = self.get_week()
        context['league'] = self.get_league()

        return context


class MatchDetail(generics.RetrieveUpdateDestroyAPIView, WeekMixin):
    serializer_class = bowling_serializers.Match

    def get_queryset(self):
        return self.get_week().matches

    def perform_update(self, serializer):
        serializer.save(week=self.get_week())

    def get_serializer_context(self):
        context = super(MatchDetail, self).get_serializer_context()

        context['week'] = self.get_week()
        context['league'] = self.get_league()

        return context


class ScoreSheetView(generics.RetrieveUpdateAPIView, WeekMixin):
    serializer_class = bowling_serializers.ScoreSheet

    def get_queryset(self):
        return self.get_week().matches.prefetch_related()

    def perform_update(self, serializer):
        serializer.save(week=self.get_week())

    def get_serializer_context(self):
        context = super(ScoreSheetView, self).get_serializer_context()

        context['week'] = self.get_week()
        context['league'] = self.get_league()

        return context


class MatchMixin(WeekMixin):
    match_url_kwarg = 'match_pk'
    match_lookup_field = 'pk'
    match_queryset = bowling_models.Match.objects.all()

    def get_match_queryset(self):
        return self.get_week().matches

    def get_match(self):
        filter_kwargs = {self.match_lookup_field: self.kwargs[self.match_url_kwarg]}
        obj = get_object_or_404(self.get_match_queryset(), **filter_kwargs)

        return obj


class Self(generics.RetrieveUpdateAPIView):
    serializer_class = bowling_serializers.User

    def get_object(self):
        return self.request.user


