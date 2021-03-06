from django.conf.urls.defaults import *

urlpatterns = patterns('butkus.ncf.views',
    (r'^$', 'index'),
    (r'^index/$', 'index'),
    (r'^conference/(?P<conference_id>\d+)/$', 'conference'),
    (r'^conference/(?P<conference_id>\d+)/scores/$', 'conference_scores'),
    (r'^conference/(?P<conference_id>\d+)/scores/season/(?P<season>\d+)/$', 'conference_scores'),
    (r'^conference/(?P<conference_id>\d+)/scores/season/(?P<season>\d+)/week/(?P<week>\d+)/$', 'conference_scores'),
    (r'^conference/(?P<conference_id>\d+)/standings/$', 'conference_standings'),
    (r'^conference/(?P<conference_id>\d+)/stats/$', 'conference_stats'),
    (r'^conferences/$', 'conferences'),
    (r'^game/(?P<game_id>\d+)/stats/edit/$', 'gamestats_edit'),
    (r'^player/(?P<player_id>\d+)/$', 'player'),
    (r'^player/(?P<player_id>\d+)/stats/$', 'player_stats'),
    (r'^team/(?P<team_id>\d+)/$', 'team'),
    (r'^team/(?P<team_id>\d+)/roster/$', 'team_roster'),
    (r'^team/(?P<team_id>\d+)/roster/season/(?P<season>[a-zA-Z0-9]+)/$', 'team_roster'),
    (r'^team/(?P<team_id>\d+)/roster/season/(?P<season>[a-zA-Z0-9]+)/sort/(?P<sort>[a-zA-Z]+)/$', 'team_roster'),
    (r'^team/(?P<team_id>\d+)/schedule/$', 'team_schedule'),
    (r'^team/(?P<team_id>\d+)/schedule/season/(?P<season>[a-zA-Z0-9]+)/$', 'team_schedule'),
    (r'^team/(?P<team_id>\d+)/stats/$', 'team_stats'),
    (r'^teams/$', 'teams'),
)
