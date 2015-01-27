"""
URLS for the bowling entry application.
"""
from django.contrib.auth.decorators import login_required
from django.conf.urls import url, patterns
from bowling_entry.views import (MatchList, MatchCreate, MatchDetails, TeamCreate, BowlerCreate, TeamDetails,
                                 StartGames, GameDisplay, FrameEdit, FrameBowlerEdit)


urlpatterns = patterns('',

                       url(r'^create/$', login_required(MatchCreate.as_view()),
                           name='bowling_entry_matchcreate'),
                       url(r'^match/(?P<match_pk>\d+)/start/$', login_required(StartGames.as_view()),
                           name='bowling_entry_startgames'),
                       url(r'^match/(?P<pk>\d+)/$', login_required(MatchDetails.as_view()),
                           name='bowling_entry_matchdetails'),
                       url(r'^match/(?P<match_pk>\d+)/team/create/$', login_required(TeamCreate.as_view()),
                           name='bowling_entry_teamcreate'),
                       url(r'^match/(?P<match_pk>\d+)/team/(?P<pk>\d+)/$',
                           login_required(TeamDetails.as_view()),
                           name='bowling_entry_teamdetails'),
                       url(r'^match/(?P<match_pk>\d+)/team/(?P<team_pk>\d+)/editbowlers/$',
                           login_required(BowlerCreate.as_view()),
                           name='bowling_entry_bowlercreate'),
                       url(r'^match/(?P<match_pk>\d+)/game/(?P<game_id>\d+)/$',
                           login_required(GameDisplay.as_view()),
                           name='bowling_entry_gamedisplay'),
                       url(r'^match/(?P<match_pk>\d+)/game/(?P<game_id>\d+)/edit/(?P<frame_id>\d+)/$',
                           login_required(FrameEdit.as_view()),
                           name='bowling_entry_frameedit'),
                       url(r'^match/(?P<match_pk>\d+)/game/(?P<game_id>\d+)/edit/(?P<frame_id>\d+)/bowler/(?P<bowler_id>\d+)/$',
                           login_required(FrameBowlerEdit.as_view()),
                           name='bowling_entry_framebowleredit'),
                       url(r'^$', login_required(MatchList.as_view()),
                           name='bowling_entry_matchlist'),

                       )