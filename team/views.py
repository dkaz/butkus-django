import string

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth.models import User

from butkus.league.models import *
from butkus.ncf.models import *
from butkus.team.forms import *
from butkus.team.models import *
from butkus.team.manipulators import *

AVAILABLE_DRAFTS = [2005,2006,2007]
AVAILABLE_PICKUPS = [2006,2007]
AVAILABLE_ROSTERS = [2006,2007]
AVAILABLE_STARTERS = [2006,2007]

def _current_season():
    return FantasySchedule.objects.current().season

def _current_week():
    return FantasySchedule.objects.current().week

def index(request, team_id=None):
    #if not request.user.is_authenticated():
        #return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)

    teams = _get_teams()
    team = _get_team(request, team_id)
    team_season = FantasySeason.objects.filter(team=team)[0]
    return render_to_response('team/index.html', {
        'team': team,
        'teams': teams,
        'team_season': team_season,
        }, context_instance=RequestContext(request))

def change_current_team(request, team_id):
    try:
        new_team_id = request.GET['new_team_id']
        next = request.GET['next']

        toks = string.split(next, "/")
        if (len(toks) == 3):
            new_next = "/team/%s/" % (new_team_id,)
        else:
            new_next = "/team/%s/%s" % (new_team_id, "/".join(toks[3:]))
    except KeyError:
        raise Http404, _("One or more of the required fields wasn't submitted")

    return HttpResponseRedirect(new_next)

def boxscores(request, team_id, season=_current_season(), week=_current_week()):
    week = int(week)
    season = int(season)
    weeks = FantasySchedule.objects.weeks(season)
    teams = _get_teams()
    team = _get_team(request, team_id)
    team_season = FantasySeason.objects.get(team=team, season=_current_season())
    stat_desc_by_name = Stat.objects.hash_all()    
    starter_infos_by_position = {}
    starters = FantasyStarter.objects.filter(team=team, season=season, week=week)
    for starter in starters:
        position = starter.position
        if (not starter_infos_by_position.has_key(position)):
            # initialize starter_info if it doesn't exist
            position_stats = FantasyScoring().stats(position)
            boxscore_stat_names = [string.upper(stat_desc_by_name[stat].boxscore_name) for stat in position_stats]
            new_starter_info = {
                'position': position,
                'starters': [],
                'stats': [string.upper(stat_desc_by_name[stat].boxscore_name) for stat in position_stats],
                'stats_len': 55.0 / len(position_stats)
            }
            starter_infos_by_position[position] = new_starter_info
        starter_info = starter_infos_by_position[position]
        starter_info['starters'].append(starter)
    starter_infos = starter_infos_by_position.values()
    deco = [(starter_info['starters'][0].position_order, starter_info) for starter_info in starter_infos]
    deco.sort()
    sorted_starter_infos = [starter_info for _, starter_info in deco]
    return render_to_response('team/boxscores.html', {
        'available_seasons': AVAILABLE_STARTERS,
        'selected_season': season,
        'selected_week': week,
        'season_weeks': weeks,
        'starter_infos': sorted_starter_infos,
        'team': team,
        'teams': teams,
        'team_season': team_season,
        }, context_instance=RequestContext(request))

def roster(request, team_id, season=_current_season(), week=_current_week()):
    week = int(week)
    season = int(season)
    teams = _get_teams()
    team = FantasyTeam.objects.get(pk=team_id)
    team_season = _get_team_season(team, season)
    weeks = FantasySchedule.objects.weeks(season)
    schedule_week = FantasySchedule.objects.get(season=season,week=week)
    week_games = Schedule.objects.filter(date__range=(schedule_week.first_date, schedule_week.last_date))
    rosters = FantasyRoster.objects.eligible(team_id=team, season=season, week=week)

    # create roster infos
    roster_infos = [{'roster':roster} for roster in rosters]
    for roster_info in roster_infos:
        roster = roster_info['roster']
        team_games = week_games.filter(team=roster.player.team)
        game_info = ""
        if (len(team_games) == 0):
            game_info = "OFF"
        elif (len(team_games) == 1):
            game = team_games[0]
            game_info = game.opponent.name
        else:
            game_info = "MULTIPLE GAMES"            

    return render_to_response('team/roster.html', {
        'available_seasons': AVAILABLE_ROSTERS,
        'last_week': weeks[len(weeks)-1],
        'rosters': rosters,
        'selected_season': season,
        'selected_week': week,
        'season_weeks': weeks,
        'team': team,
        'teams': teams,
        'team_season': team_season,
        }, context_instance=RequestContext(request))

def starters(request, team_id, season=_current_season(), week=_current_week()):
    week = int(week)
    season = int(season)
    teams = _get_teams()
    team = FantasyTeam.objects.get(pk=team_id)
    team_season = _get_team_season(team, season)
    weeks = FantasySchedule.objects.weeks(season)

    starters = FantasyStarter.objects.filter(team=team, season=season, week=week)
    deco = [(starter.position_order, starter.player_name, starter) for starter in starters]
    deco.sort()
    sorted_starters = [starter for _, _, starter in deco]

    return render_to_response('team/starters.html', {
        'available_seasons': AVAILABLE_STARTERS,
        'starters': sorted_starters,
        'selected_season': season,
        'selected_week': week,
        'season_weeks': weeks,
        'team': team,
        'teams': teams,
        'team_season': team_season,
        }, context_instance=RequestContext(request))

def starters_edit(request, team_id, season, week):
    week = int(week)
    season = int(season)
    teams = _get_teams()
    team = FantasyTeam.objects.get(pk=team_id)
    team_season = _get_team_season(team, season)
    weeks = FantasySchedule.objects.weeks(season)
    schedule_week = FantasySchedule.objects.get(season=season, week=week)

    if request.POST:    
        new_data = request.POST.copy()
        starters_data = [(int(key.split(".")[1]),
                          int_or_none(sub_or_none(new_data[key], ".", 0)),
                          int_or_none(sub_or_none(new_data[key], ".", 1))) for key in new_data.keys() if key.startswith("starter.")]
        for starter_data in starters_data:
            starter_id = starter_data[0]
            roster_id = starter_data[1]
            game_id = starter_data[2]
            starter = FantasyStarter.objects.get(pk=starter_id)
            if (roster_id != None):
                roster = FantasyRoster.objects.get(pk=roster_id)
                starter.roster = roster
                starter.player = roster.player
                if (game_id != None):
                    game = Schedule.objects.get(pk=game_id)
                    starter.game = game
            else:
                starter.roster = None
                starter.player = None
                starter.game = None
            starter.save()

    fantasy_eligibilities = FantasyEligibility.objects.filter(season=season)
    eligibility_map = {}
    for fe in fantasy_eligibilities:
        eligibility_map[fe.fantasy_position] = fe.ncf_positions            
        
    unsorted_starters = FantasyStarter.objects.filter(team=team_id, season=season, week=week)
    deco = [(starter.position_order, starter) for starter in unsorted_starters]
    deco.sort()
    starters = [starter for _, starter in deco]

    # create starter info out of FantasyStarter records
    starter_infos = [{'id':starter.id,
                      'position':starter.position,
                      'player_name':starter.player_name,
                      'player':starter.player} for starter in starters]

    # add eligible replacements
    unsorted_eligible_rosters = FantasyRoster.objects.eligible(team_id=team_id, season=season, week=week)
    deco = [(roster.player.name, roster) for roster in unsorted_eligible_rosters]
    deco.sort()
    week_eligibles = [roster for _, roster in deco]
    for starter_info in starter_infos:
        position = starter_info['position']
        ncf_positions = eligibility_map[position]
        position_eligibles = filter_by_position(week_eligibles, ncf_positions)
        eligible_infos = []
        for eligible_roster in position_eligibles:
            eligible_games = Schedule.objects.filter(team=eligible_roster.player.team, date__range=(schedule_week.first_date, schedule_week.last_date))
            if (len(eligible_games) == 0):
                id = "%s.%s" % (eligible_roster.id, None)
                name = "%s (%s) OFF" % (eligible_roster.player.name, eligible_roster.player.team.name)
                eligible_info = {'roster':eligible_roster, 'id':id, 'name':name}
                eligible_infos.append(eligible_info)
            else:
                for eligible_game in eligible_games:
                    id = "%s.%s" % (eligible_roster.id, eligible_game.id)
                    name = "%s (%s) %s %s" % (eligible_roster.player.name,
                                              eligible_roster.player.team.name,
                                              ternary(eligible_game.away, "@", "vs."),
                                              eligible_game.opponent.name)
                    eligible_info = {'roster':eligible_roster, 'id':id, 'game':eligible_game, 'name':name}
                    eligible_infos.append(eligible_info)
                    
        starter_info['eligible'] = eligible_infos

    return render_to_response('team/starters_edit.html', {
        'starter_infos': starter_infos,
        'selected_season': season,
        'selected_week': week,
        'season_weeks': weeks,
        'team': team,
        'teams': teams,
        'team_season': team_season,
        }, context_instance=RequestContext(request))

def ternary(one, two, three):
    if (one):
        return two
    else:
        return three

def sub_or_none(str, delimiter, part_idx):
    if (str.find(delimiter) != -1):
        return str.split(delimiter)[part_idx]
    else:
        return None
    
    
def int_or_none(str):
    if (str == None or str == "None" or str == ""):
        return None    
    else:
        return int(str)

def filter_by_position(rosters, positions):
    pos_arr = string.split(positions, ',')
    return [roster for roster in rosters if roster.player.position in pos_arr]

def roster_cut(request, team_id, roster_id, season=_current_season(), week=1):
    if (request.user.id == 1):
        team = FantasyTeam.objects.get(pk=team_id)
    else:
        team = FantasyTeam.objects.get(pk=team_id, owner=request.user)
    roster_drop = FantasyRoster.objects.get(pk=roster_id, team=team)

    roster_drop.last_season = season
    roster_drop.last_week = int(week)
    roster_drop.save()
    return HttpResponseRedirect('/team/%s/roster/season/%s/week/%s' % (team_id, season, week))

def roster_move(request, team_id, roster_id, season=_current_season(), week=1):
    if (request.user.id == 1):
        team = FantasyTeam.objects.get(pk=team_id)
    else:
        team = FantasyTeam.objects.get(pk=team_id, owner=request.user)
    roster_drop = FantasyRoster.objects.get(pk=roster_id, team=team)

    manipulator = PickupManipulator(team_id, roster_id, season, week)
    if request.POST:
        new_data = request.POST.copy()
        errors = manipulator.get_validation_errors(new_data)

        if not errors:
            manipulator.do_html2python(new_data)
            manipulator.save(new_data)
            return HttpResponseRedirect('/team/%s/roster/season/%s/week/%s' % (team_id, season, week))
    else:
        errors = new_data = {}

    form = forms.FormWrapper(manipulator, new_data, errors)
    
    return render_to_response('team/roster_move.html', {
        'roster_drop': roster_drop,
        'team': team,
        'selected_season': season,
        'selected_week': week,
        'form': form,
        }, context_instance=RequestContext(request))

def pickups(request, team_id, season=_current_season()):
    teams = _get_teams()
    team = FantasyTeam.objects.get(pk=team_id)
    team_season = _get_team_season(team, season)
    pickups = FantasyPickup.objects.filter(team=team, season=season)

    deco = [(pickup.week, pickup.pick, pickup) for pickup in pickups]
    deco.sort()
    sorted_pickups = [pickup for _, _, pickup in deco]

    return render_to_response('team/pickups.html', {
        'team': team,
        'teams': teams,
        'team_season': team_season,
        'pickups': sorted_pickups,
        'available_seasons': AVAILABLE_PICKUPS,
        'selected_season': season,
        }, context_instance=RequestContext(request))

def draft(request, team_id, season=_current_season(), sort="pick"):
    season = int(season)
    teams = _get_teams()
    team = FantasyTeam.objects.get(pk=team_id)
    team_season = _get_team_season(team, season)
    drafts = FantasyDraft.objects.filter(season=season, team=team)

    if sort == "position":
        deco = [(draft.player.position, draft.pick, draft) for draft in drafts]
    elif sort == "school":
        deco = [(draft.player.team.name, draft.pick, draft) for draft in drafts]
    elif sort == "player":
        deco = [(draft.player.last_name, draft.player.first_name, draft) for draft in drafts]
    else:
        deco = [(draft.pick, draft.pick, draft) for draft in drafts]
    deco.sort()

    sorted_drafts = [draft for _, _, draft in deco]

    return render_to_response('team/draft.html', {
        'team': team,
        'teams': teams,
        'team_season': team_season,
        'drafts': sorted_drafts,
        'available_seasons': AVAILABLE_DRAFTS,
        'selected_season': season,
        }, context_instance=RequestContext(request))

def trades(request, team_id=None):
    teams = _get_teams()
    team = _get_team(request, team_id)
    team_season = _get_team_season(team, season)
    return render_to_response('team/trades.html', {
        'team': team,
        'teams': teams,
        'team_season': team_season,
        }, context_instance=RequestContext(request))

"""
Return FantasySeason record for a particular season OR the last FantasySeason the team participated in
"""
def _get_team_season(team, season):
    try:
        team_season = FantasySeason.objects.get(team=team, season=_current_season())
    except ObjectDoesNotExist:
        team_season = FantasySeason.objects.filter(team=team)[0]
    return team_season

"""
Return a sorted list of teams
"""
def _get_teams():
    teams = FantasyTeam.objects.all()
    deco = [(team.owner.first_name, team) for team in teams]
    deco.sort()
    sorted_teams = [team for _, team in deco]
    return sorted_teams
    
"""
Return a specific team or current user's team
"""
def _get_team(request, team_id):
    if (team_id == None):
        match = FantasyTeam.objects.filter(owner=request.user)
        if (len(match) > 0):
            team = match[0]
        else:
            team = FantasyTeam.objects.get(pk=1)
    else:
        team = FantasyTeam.objects.get(pk=team_id)
    return team
