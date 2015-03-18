"""
URLS for the bowling entry application.
"""
from django.conf.urls import url, patterns
from bowling_entry import views as bowling_views


urlpatterns = patterns('',
                       url(r'^api/league/$',
                           bowling_views.LeagueListCreate.as_view(),
                           name='bowling_entry_leagues'),
                       url(r'^api/league/(?P<pk>\d+)/$',
                           bowling_views.LeagueDetail.as_view(),
                           name='bowling_entry_league_detail'),

                       url(r'^api/league/(?P<league_pk>\d+)/substitute/$',
                           bowling_views.SubstitutesList.as_view(),
                           name='bowling_entry_league_substitutes'),
                       url(r'^api/league/(?P<league_pk>\d+)/substitute/(?P<pk>\d+)/$',
                           bowling_views.SubstituteDetail.as_view(),
                           name='bowling_entry_league_substitute_detail'),


                       url(r'^api/league/(?P<league_pk>\d+)/weeks/$',
                           bowling_views.WeekList.as_view(),
                           name='bowling_entry_league_weeks'),
                       url(r'^api/league/(?P<league_pk>\d+)/weeks/(?P<week_number>\d+)/$',
                           bowling_views.WeekDetail.as_view(),
                           name='bowling_entry_league_week_detail'),
                       url(r'^api/league/(?P<league_pk>\d+)/weeks/(?P<week_number>\d+)/matches/$',
                           bowling_views.MatchList.as_view(),
                           name='bowling_entry_league_week_matches'),
                       url(r'^api/league/(?P<league_pk>\d+)/weeks/(?P<week_number>\d+)/matches/(?P<pk>\d+)/$',
                           bowling_views.MatchDetail.as_view(),
                           name='bowling_entry_league_week_match_detail'),

                       url(r'^api/league/(?P<league_pk>\d+)/teams/$',
                           bowling_views.TeamDefinitionListCreate.as_view(),
                           name='bowling_entry_league_teams'),
                       url(r'^api/league/(?P<league_pk>\d+)/teams/(?P<pk>\d+)/$',
                           bowling_views.TeamDetail.as_view(),
                           name='bowling_entry_league_team_detail'),
                       url(r'^api/league/(?P<league_pk>\d+)/teams/(?P<pk>\d+)/bowlers/$',
                           bowling_views.TeamBowlerDefinitionListCreate.as_view(),
                           name='bowling_entry_league_team_bowlers'),
                       url(r'^api/league/(?P<league_pk>\d+)/teams/(?P<team_pk>\d+)/bowlers/(?P<pk>\d+)/$',
                           bowling_views.TeamBowlerDefinitionDetail.as_view(),
                           name='bowling_entry_league_team_bowlers_detail'),
                       url(r'^api/self/$',
                           bowling_views.Self.as_view(),
                           name='bowling_entry_self'),
                       )