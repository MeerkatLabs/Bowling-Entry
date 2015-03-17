from bowling_entry import models as bowling_models
from django import shortcuts


class LeagueMixin(object):
    """
    Mixin that should make looking up related items easier.
    """
    league_url_kwarg = 'league_pk'
    league_lookup_field = 'pk'
    league_queryset = bowling_models.League.objects
    league = None

    def get_league_queryset(self):
        return self.league_queryset

    def get_league(self):
        filter_kwargs = {self.league_lookup_field: self.kwargs[self.league_url_kwarg]}
        obj = shortcuts.get_object_or_404(self.get_league_queryset(), **filter_kwargs)

        return obj

    def append_bowling_context(self, context):
        if self.league is not None:
            context['league'] = self.league


class TeamMixin(LeagueMixin):
    """
    Mixin that should make looking up related items easier.
    """
    team_url_kwarg = 'team_pk'
    team_lookup_field = 'pk'
    team_queryset = bowling_models.League.objects
    team = None

    def get_team_queryset(self):
        if self.league is None:
            self.league = self.get_league()

        return self.league.teams

    def get_team(self):
        filter_kwargs = {self.team_lookup_field: self.kwargs[self.team_url_kwarg]}
        obj = shortcuts.get_object_or_404(self.get_team_queryset(), **filter_kwargs)

        return obj

    def append_bowling_context(self, context):
        super(TeamMixin, self).append_bowling_context(context)
        if self.team is not None:
            context['team'] = self.team


class WeekMixin(LeagueMixin):
    week_url_kwarg = 'week_pk'
    week_lookup_field = 'pk'
    week_queryset = bowling_models.League.objects
    week = None

    def get_week_queryset(self):
        if self.league is None:
            self.league = self.get_league()

        return self.league.weeks

    def get_week(self):
        filter_kwargs = {self.week_lookup_field: self.kwargs[self.week_url_kwarg]}
        obj = shortcuts.get_object_or_404(self.get_week_queryset(), **filter_kwargs)

        return obj

    def append_bowling_context(self, context):
        super(WeekMixin, self).append_bowling_context(context)
        if self.week is not None:
            context['week'] = self.week


class MatchMixin(WeekMixin):
    match_url_kwarg = 'match_pk'
    match_lookup_field = 'pk'
    match_queryset = bowling_models.Match.objects
    match = None

    def get_match_queryset(self):
        if self.week is None:
            self.week = self.get_week()

        return self.week.matches

    def get_match(self):
        filter_kwargs = {self.match_lookup_field: self.kwargs[self.match_url_kwarg]}
        obj = shortcuts.get_object_or_404(self.get_match_queryset(), **filter_kwargs)

        return obj

    def append_bowling_context(self, context):
        super(MatchMixin, self).append_bowling_context(context)
        if self.match is not None:
            context['match'] = self.match