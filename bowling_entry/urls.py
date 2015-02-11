"""
URLS for the bowling entry application.
"""
from django.conf.urls import url, patterns
from bowling_entry.views import (LeagueListCreate, LeagueDetail, TeamDefinitionListCreate, TeamBowlerDefinitionDetail,
                                 TeamBowlerDefinitionListCreate, SubstitutesList, WeekCreateList, WeekDetail,
                                 MatchList, MatchDetail, MatchCreate, MatchTeamDetail, MatchTeamBowlerDetail,
                                 CreateGames)


urlpatterns = patterns('',
                       url(r'^api/league/$', LeagueListCreate.as_view(),
                           name='bowling_entry_leagues'),
                       url(r'^api/league/(?P<pk>\d+)/$', LeagueDetail.as_view(),
                           name='bowling_entry_league_detail'),

                       url(r'^api/league/(?P<league_pk>\d+)/substitutes/$', SubstitutesList.as_view(),
                           name='bowling_entry_league_substitutes'),


                       url(r'^api/league/(?P<league_pk>\d+)/weeks/$', WeekCreateList.as_view(),
                           name='bowling_entry_league_weeks'),
                       url(r'^api/league/(?P<league_pk>\d+)/weeks/(?P<pk>\d+)/$', WeekDetail.as_view(),
                           name='bowling_entry_league_week_detail'),
                       url(r'^api/league/(?P<league_pk>\d+)/weeks/(?P<week_pk>\d+)/createMatch/$', MatchCreate.as_view(),
                           name='bowling_entry_league_week_match_create'),
                       url(r'^api/league/(?P<league_pk>\d+)/weeks/(?P<week_pk>\d+)/matches/$',
                           MatchList.as_view(),
                           name='bowling_entry_league_week_matches'),
                       url(r'^api/league/(?P<league_pk>\d+)/weeks/(?P<week_pk>\d+)/matches/(?P<pk>\d+)/$',
                           MatchDetail.as_view(),
                           name='bowling_entry_league_week_match_detail'),
                       url(r'^api/league/(?P<league_pk>\d+)/weeks/(?P<week_pk>\d+)/matches/(?P<match_pk>\d+)/teams/(?P<pk>\d+)/$',
                           MatchTeamDetail.as_view(),
                           name='bowling_entry_league_week_match_teams'),
                       url(r'^api/league/(?P<league_pk>\d+)/weeks/(?P<week_pk>\d+)/matches/(?P<match_pk>\d+)/teams/(?P<team_pk>\d+)/bowler/(?P<pk>\d+)/$',
                           MatchTeamBowlerDetail.as_view(),
                           name='bowling_entry_league_week_match_teams'),
                       url(r'^api/league/(?P<league_pk>\d+)/weeks/(?P<week_pk>\d+)/matches/(?P<match_pk>\d+)/games/$',
                           CreateGames.as_view(),
                           name='bowling_entry_league_week_match_games'),


                       url(r'^api/league/(?P<league_pk>\d+)/teams/$', TeamDefinitionListCreate.as_view(),
                           name='bowling_entry_league_teams'),
                       url(r'^api/league/(?P<league_pk>\d+)/teams/(?P<pk>\d+)/$', TeamDefinitionListCreate.as_view(),
                           name='bowling_entry_league_team_detail'),
                       url(r'^api/league/(?P<league_pk>\d+)/teams/(?P<pk>\d+)/bowlers/$',
                           TeamBowlerDefinitionListCreate.as_view(),
                           name='bowling_entry_league_team_bowlers'),
                       url(r'^api/league/(?P<league_pk>\d+)/teams/(?P<team_pk>\d+)/bowlers/(?P<pk>\d+)/$',
                           TeamBowlerDefinitionDetail.as_view(),
                           name='bowling_entry_league_team_bowlers_detail'),
                       )