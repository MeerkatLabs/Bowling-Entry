from bowling_entry import models as bowling_models
from rest_framework import generics
from bowling_entry import serializers as bowling_serializers
from bowling_entry.views import mixins


class LeagueListCreate(generics.ListCreateAPIView):
    queryset = bowling_models.League.objects.prefetch_related('teams', 'weeks')
    serializer_class = bowling_serializers.League

    def perform_create(self, serializer):
        serializer.save(secretary=self.request.user)


class LeagueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = bowling_models.League.objects.prefetch_related('teams', 'weeks')
    serializer_class = bowling_serializers.League


class TeamDefinitionListCreate(generics.ListCreateAPIView, mixins.LeagueMixin):
    serializer_class = bowling_serializers.TeamDefinition

    def list(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(TeamDefinitionListCreate, self).list(request, *args, **kwargs)

    def get_queryset(self):
        return self.get_league().teams.prefetch_related('bowlers')

    def perform_create(self, serializer):
        serializer.save(league=self.get_league())

    def get_serializer_context(self):
        context = super(TeamDefinitionListCreate, self).get_serializer_context()
        self.append_bowling_context(context)
        return context


class TeamDetail(generics.RetrieveUpdateDestroyAPIView, mixins.LeagueMixin):
    serializer_class = bowling_serializers.TeamDefinition

    def retrieve(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(TeamDetail, self).retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(TeamDetail, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(TeamDetail, self).destroy(request, *args, **kwargs)

    def get_queryset(self):
        return self.league.teams

    def perform_update(self, serializer):
        serializer.save(league=self.league)

    def get_serializer_context(self):
        context = super(TeamDetail, self).get_serializer_context()
        self.append_bowling_context(context)
        return context


class TeamBowlerDefinitionListCreate(generics.ListCreateAPIView, mixins.TeamMixin):
    serializer_class = bowling_serializers.TeamBowlerDefinition
    team_url_kwarg = 'pk'

    def list(self, request, *args, **kwargs):
        self.league = self.get_league()
        self.team = self.get_team()
        return super(TeamBowlerDefinitionListCreate, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.league = self.get_league()
        self.team = self.get_team()
        return super(TeamBowlerDefinitionListCreate, self).create(request, *args, **kwargs)

    def get_queryset(self):
        return bowling_models.BowlerDefinition.objects.filter(team=self.team)

    def perform_create(self, serializer):
        serializer.save(team=self.team, league=self.league)

    def get_serializer_context(self):
        context = super(TeamBowlerDefinitionListCreate, self).get_serializer_context()
        self.append_bowling_context(context)
        return context


class TeamBowlerDefinitionDetail(generics.RetrieveUpdateDestroyAPIView, mixins.TeamMixin):
    serializer_class = bowling_serializers.TeamBowlerDefinition

    def retrieve(self, request, *args, **kwargs):
        self.league = self.get_league()
        self.team = self.get_team()
        return super(TeamBowlerDefinitionDetail, self).retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.league = self.get_league()
        self.team = self.get_team()
        return super(TeamBowlerDefinitionDetail, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.league = self.get_league()
        self.team = self.get_team()
        return super(TeamBowlerDefinitionDetail, self).destroy(request, *args, **kwargs)

    def get_queryset(self):
        return bowling_models.BowlerDefinition.objects.filter(league=self.league)

    def get_serializer_context(self):
        context = super(TeamBowlerDefinitionDetail, self).get_serializer_context()
        self.append_bowling_context(context)
        return context


class SubstitutesList(generics.ListCreateAPIView, mixins.LeagueMixin):
    serializer_class = bowling_serializers.Substitute

    def list(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(SubstitutesList, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(SubstitutesList, self).create(request, *args, **kwargs)

    def get_queryset(self):
        return self.get_league().substitutes()

    def perform_create(self, serializer):
        serializer.save(league=self.league, team=None)

    def get_serializer_context(self):
        context = super(SubstitutesList, self).get_serializer_context()
        self.append_bowling_context(context)
        return context


class SubstituteDetail(generics.RetrieveUpdateDestroyAPIView, mixins.LeagueMixin):
    serializer_class = bowling_serializers.Substitute

    def destroy(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(SubstituteDetail, self).destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(SubstituteDetail, self).retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(SubstituteDetail, self).update(request, *args, **kwargs)

    def get_queryset(self):
        return self.league.substitutes()

    def get_serializer_context(self):
        context = super(SubstituteDetail, self).get_serializer_context()
        self.append_bowling_context(context)
        return context


class WeekCreateList(generics.ListCreateAPIView, mixins.LeagueMixin):
    serializer_class = bowling_serializers.Week

    def list(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(WeekCreateList, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(WeekCreateList, self).create(request, *args, **kwargs)

    def get_queryset(self):
        return self.league.weeks.prefetch_related('matches')

    def perform_create(self, serializer):
        serializer.save(league=self.league)

    def get_serializer_context(self):
        context = super(WeekCreateList, self).get_serializer_context()
        self.append_bowling_context(context)
        return context


class WeekDetail(generics.RetrieveUpdateDestroyAPIView, mixins.LeagueMixin):
    serializer_class = bowling_serializers.Week

    def retrieve(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(WeekDetail, self).retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(WeekDetail, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.league = self.get_league()
        return super(WeekDetail, self).destroy(request, *args, **kwargs)

    def get_queryset(self):
        return self.get_league().weeks

    def perform_update(self, serializer):
        serializer.save(league=self.get_league())

    def get_serializer_context(self):
        context = super(WeekDetail, self).get_serializer_context()
        self.append_bowling_context(context)
        return context


class MatchList(generics.ListCreateAPIView, mixins.WeekMixin):
    serializer_class = bowling_serializers.Match

    def create(self, request, *args, **kwargs):
        self.league = self.get_league()
        self.week = self.get_week()
        return super(MatchList, self).create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.league = self.get_league()
        self.week = self.get_week()
        return super(MatchList, self).list(request, *args, **kwargs)

    def get_queryset(self):
        return self.week.matches

    def get_serializer_context(self):
        context = super(MatchList, self).get_serializer_context()
        self.append_bowling_context(context)
        return context


class MatchDetail(generics.RetrieveUpdateDestroyAPIView, mixins.WeekMixin):
    serializer_class = bowling_serializers.ScoreSheet

    def retrieve(self, request, *args, **kwargs):
        self.league = self.get_league()
        self.week = self.get_week()
        return super(MatchDetail, self).retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.league = self.get_league()
        self.week = self.get_week()
        return super(MatchDetail, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.league = self.get_league()
        self.week = self.get_week()
        return super(MatchDetail, self).destroy(request, *args, **kwargs)

    def get_queryset(self):
        return self.week.matches.select_related('team1', 'team2')

    def perform_update(self, serializer):
        serializer.save(week=self.week)

    def get_serializer_context(self):
        context = super(MatchDetail, self).get_serializer_context()
        self.append_bowling_context(context)
        return context


class Self(generics.RetrieveUpdateAPIView):
    serializer_class = bowling_serializers.User

    def get_object(self):
        return self.request.user
