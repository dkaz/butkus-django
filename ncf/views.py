from django.shortcuts import render_to_response
from django.template import RequestContext
from butkus.ncf.models import *
from butkus.league.models import *
from butkus.team.models import *
import string

AVAILABLE_ROSTERS = ["2005","2006","2007"]
AVAILABLE_SCHEDULES = ["2005","2006","2007"]

def _current_season():
    return FantasySchedule.objects.current().season

def _current_week():
    return FantasySchedule.objects.current().week

def index(request):
    return render_to_response('ncf/index.html', {
        }, context_instance=RequestContext(request))

def gamestats_edit(request, game_id):
    game = Schedule.objects.get(pk=game_id)
    stat_desc_by_name = Stat.objects.hash_all()    
    starters = FantasyStarter.objects.filter(game=game_id)
    boxscore = {'home': {}, 'away': {}}
    for starter in starters:
        player = starter.player
        if (player.team == game.team):
            team_boxscore = boxscore['home']
        else:
            team_boxscore = boxscore['away']
        if (starter.position not in team_boxscore):
            position_stats = FantasyScoring().stats(starter.position)
            stat_names = [string.upper(stat_desc_by_name[stat].boxscore_name) for stat in position_stats]
            team_boxscore[starter.position] = {'position':starter.position, 'stats':stat_names, 'players':[player,]}
        else:
            team_boxscore[starter.position]['players'].append(player)

    print boxscore            

    return render_to_response('ncf/gamestats_edit.html', {
        'game': game,
        'boxscore': boxscore,
        }, context_instance=RequestContext(request))

def conferences(request):
    div1a_conferences = Conference.objects.filter(division='I-A')
    div1aa_conferences = Conference.objects.filter(division='I-AA')
    conference_pairs = __merge_lists(div1a_conferences, div1aa_conferences)
    return render_to_response('ncf/conferences.html', {
        'conference_pairs': conference_pairs,
        }, context_instance=RequestContext(request))

def conference(request, conference_id):
    conference = Conference.objects.get(pk=conference_id)
    return render_to_response('ncf/conference.html', {
        'conference': conference,
        }, context_instance=RequestContext(request))

def conference_stats(request, conference_id):
    conference = Conference.objects.get(pk=conference_id)
    return render_to_response('ncf/conference_stats.html', {
        'conference': conference,
        }, context_instance=RequestContext(request))

def conference_standings(request, conference_id):
    conference = Conference.objects.get(pk=conference_id)
    return render_to_response('ncf/conference_standings.html', {
        'conference': conference,
        }, context_instance=RequestContext(request))

def conference_scores(request, conference_id, season=_current_season(), week=_current_week()):
    week = int(week)
    conference = Conference.objects.get(pk=conference_id)
    weeks = FantasySchedule.objects.weeks(season)
    schedule_week = FantasySchedule.objects.get(season=season,week=week)
    week_games = Schedule.objects.filter(date__range=(schedule_week.first_date, schedule_week.last_date))
    conference_games = [ game for game in week_games if (game.team.conference == conference and game.home)]
    return render_to_response('ncf/conference_scores.html', {
        'available_seasons': ["2006"],
        'conference': conference,
        'season_weeks': weeks,
        'selected_season': season,
        'selected_week': week,
        'games': conference_games,
        }, context_instance=RequestContext(request))

def teams(request):
    div1a_conferences = Conference.objects.filter(division='I-A')
    div1aa_conferences = Conference.objects.filter(division='I-AA')

    div1a_teams = Team.objects.filter(conference__in=div1a_conferences)
    div1aa_teams = Team.objects.filter(conference__in=div1aa_conferences)

    return render_to_response('ncf/teams.html', {
        'div1a_conferences': div1a_conferences,
        'div1aa_conferences': div1aa_conferences,
        }, context_instance=RequestContext(request))

def team(request, team_id):
    team = Team.objects.get(pk=team_id)
    return render_to_response('ncf/team.html', {
        'team': team,
        }, context_instance=RequestContext(request))

def team_stats(request, team_id):
    team = Team.objects.get(pk=team_id)
    return render_to_response('ncf/team_stats.html', {
        'team': team,
        }, context_instance=RequestContext(request))

def team_roster(request, team_id, season=_current_season(), sort="number"):
    team = Team.objects.get(pk=team_id)
    print season
    rosters = Roster.objects.filter(team=team, season=season)
    print len(rosters)
    rosters = [roster for roster in rosters if (roster.last_name != 'Team')]

    if sort == "name":
        deco = [(roster.name, roster) for roster in rosters]
    elif sort == "position":
        deco = [(roster.position, roster) for roster in rosters]
    elif sort == "eligibility":
        deco = [(roster.year, roster) for roster in rosters]
    else:
        deco = [(roster.number, roster) for roster in rosters]
    deco.sort()
    sorted_rosters = [roster for _, roster in deco]

    return render_to_response('ncf/team_roster.html', {
        'team': team,
        'rosters': sorted_rosters,
        'selected_season': season,
        'available_seasons': AVAILABLE_ROSTERS,
        }, context_instance=RequestContext(request))

def team_schedule(request, team_id, season=_current_season()):
    team = Team.objects.get(pk=team_id)
    schedules = Schedule.objects.filter(team=team, season=season)
    print schedules
    return render_to_response('ncf/team_schedule.html', {
        'team': team,
        'schedules': schedules,
        'selected_season': season,
        'available_seasons': AVAILABLE_SCHEDULES,
        }, context_instance=RequestContext(request))

def player(request, player_id):
    player = Player.objects.get(pk=player_id)
    roster = Roster.objects.filter(player=player).order_by('-season')[0]
    return render_to_response('ncf/player.html', {
        'player': player,
        'roster': roster,
        }, context_instance=RequestContext(request))

def player_stats(request, player_id):
    player = Player.objects.get(pk=player_id)
    return render_to_response('ncf/player_stats.html', {
        }, context_instance=RequestContext(request))

'''
merges conferences and teams into 1 list
'''
def __merge_conferences_and_teams(teams):
    teams = __sort_teams_by_conference(teams)
    conferences_and_teams = []
    current_conference = None
    for team in teams:
        if (team.conference != current_conference):
            conferences_and_teams.append(team.conference)
            current_conference = team.conference

        conferences_and_teams.append(team)

    return conferences_and_teams
    
def __sort_teams_by_conference(teams):
    deco = [ (team.conference.name, team.name, team) for team in teams ]
    deco.sort()
    new_teams = [team for _, _, team in deco]
    return new_teams  

'''
merge lists into a list of lists by index
'''
def __merge_lists(*lists):
    list_of_lists = []

    lengths = [len(list) for list in lists]
    for idx in range(max(lengths)):
        current_idx_list = []
        for list in lists:
            if (idx < len(list)):
                current_idx_list.append(list[idx])
            else:
                current_idx_list.append(None)
        list_of_lists.append(current_idx_list)

    return list_of_lists
        
