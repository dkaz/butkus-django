from django.shortcuts import render_to_response
from django.template import RequestContext
from butkus.league.models import *
from butkus.team.models import *
from butkus.ncf.models import *

AVAILABLE_DRAFTS = [2005,2006,2007]
AVAILABLE_PICKUPS = ['2006','2007']
AVAILABLE_ROSTERS = [2006,2007]
AVAILABLE_STANDINGS = ['2006','2007']
AVAILABLE_STARTERS = [2006,2007]
AVAILABLE_SCHEDULES = ['2006','2007']

def _current_season():
    return FantasySchedule.objects.current().season

def _current_week():
    return FantasySchedule.objects.current().week

def index(request):    
    return render_to_response('league/index.html', {
        }, context_instance=RequestContext(request))

def owners(request):
    teams = FantasyTeam.objects.all()
    return render_to_response('league/owners.html', {
        'teams': teams,
        }, context_instance=RequestContext(request))

def starters(request, season=_current_season(), week=_current_week()):
    week = int(week)
    season = int(season)
    weeks = FantasySchedule.objects.weeks(season)

    starter_entries = []
    fantasy_seasons = FantasySeason.objects.filter(season=season)
    for fantasy_season in fantasy_seasons:
        team = fantasy_season.team
        unsorted_team_starters = FantasyStarter.objects.filter(team=team, season=season, week=week)
        deco = [(starter.position_order, starter.player_name, starter) for starter in unsorted_team_starters]
        deco.sort()
        team_starters = [starter for _, _, starter in deco]
        starter_entry = {}
        starter_entry['team'] = team
        starter_entry['starters'] = team_starters
        starter_entries.append(starter_entry)

    return render_to_response('league/starters.html', {
        'available_seasons': AVAILABLE_STARTERS,
        'season_weeks': weeks,
        'starter_entries': starter_entries,
        'selected_season': season,
        'selected_week': week,
        }, context_instance=RequestContext(request))

def rosters(request, season=_current_season(), week=_current_week()):
    week = int(week)
    season = int(season)
    weeks = FantasySchedule.objects.weeks(season)
    
    roster_entries = []
    fantasy_seasons = FantasySeason.objects.filter(season=season)
    for fantasy_season in fantasy_seasons:
        team = fantasy_season.team
        team_rosters = FantasyRoster.objects.eligible(team_id=team.id, season=season, week=week)
        roster_entry = {}
        roster_entry['team'] = team
        roster_entry['rosters'] = team_rosters
        roster_entries.append(roster_entry)

    return render_to_response('league/rosters.html', {
        'available_seasons': AVAILABLE_ROSTERS,
        'season_weeks': weeks,
        'roster_entries': roster_entries,
        'selected_season': season,
        'selected_week': week,
        }, context_instance=RequestContext(request))

def standings(request, season=_current_season(), sort="overall"):
    standings = FantasyStanding.objects.filter(season=season)

    if sort == "1":
        deco = [(standing.week1, standing.id, standing) for standing in standings]
    elif sort == "2":
        deco = [(standing.week2, standing.id, standing) for standing in standings]
    elif sort == "3":
        deco = [(standing.week3, standing.id, standing) for standing in standings]
    elif sort == "4":
        deco = [(standing.week4, standing.id, standing) for standing in standings]
    elif sort == "5":
        deco = [(standing.week5, standing.id, standing) for standing in standings]
    elif sort == "6":
        deco = [(standing.week6, standing.id, standing) for standing in standings]
    elif sort == "7":
        deco = [(standing.week7, standing.id, standing) for standing in standings]
    elif sort == "8":
        deco = [(standing.week8, standing.id, standing) for standing in standings]
    elif sort == "9":
        deco = [(standing.week9, standing.id, standing) for standing in standings]
    elif sort == "10":
        deco = [(standing.week10, standing.id, standing) for standing in standings]
    elif sort == "11":
        deco = [(standing.week11, standing.id, standing) for standing in standings]
    elif sort == "12":
        deco = [(standing.week12, standing.id, standing) for standing in standings]
    elif sort == "13":
        deco = [(standing.week13, standing.id, standing) for standing in standings]
    else:
        deco = [(standing.overall, standing.id, standing) for standing in standings]
    deco.sort()
    deco.reverse()

    sorted_standings = [standing for _, _, standing in deco]

    weeks = FantasySchedule.objects.weeks(season)

    return render_to_response('league/standings.html', {
        'standings': sorted_standings,
        'available_seasons': AVAILABLE_STANDINGS,
        'selected_season': season,
        'week_numbers': weeks,
        'number_of_weeks': len(weeks),
        }, context_instance=RequestContext(request))

def standings_edit(request, season=_current_season()):
    standings = FantasyStanding.objects.filter(season=season)

    if request.POST:
        for standing in standings:
            weeks = request.POST.getlist(str(standing.id))
            standing.week1 = weeks[0]
            standing.week2 = weeks[1]
            standing.week3 = weeks[2]
            standing.week4 = weeks[3]
            standing.week5 = weeks[4]
            standing.week6 = weeks[5]
            standing.week7 = weeks[6]
            standing.week8 = weeks[7]
            standing.week9 = weeks[8]
            standing.week10 = weeks[9]
            standing.week11 = weeks[10]
            standing.week12 = weeks[11]
            standing.week13 = weeks[12]
            standing.save()
    
    return render_to_response('league/standings_edit.html', {
        'standings': standings,
        'selected_season': season,
        'week_numbers': range(1, 14),
        }, context_instance=RequestContext(request))

def draft(request, season=_current_season(), sort="pick"):
    season = int(season)
    drafts = FantasyDraft.objects.filter(season=season)

    if sort == "team":
        deco = [(draft.team.owner_private_name, draft.pick, draft) for draft in drafts]
    elif sort == "position":
        deco = [(draft.player.position, draft.pick, draft) for draft in drafts]
    elif sort == "school":
        deco = [(draft.player.team.name, draft.pick, draft) for draft in drafts]
    elif sort == "player":
        deco = [(draft.player.name, draft.pick, draft) for draft in drafts]
    else:
        deco = [(draft.pick, draft.pick, draft) for draft in drafts]
    deco.sort()

    sorted_drafts = [draft for _, _, draft in deco]

    return render_to_response('league/draft.html', {
        'drafts': sorted_drafts,
        'available_seasons': AVAILABLE_DRAFTS,
        'selected_season': season,
        }, context_instance=RequestContext(request))

def pickups(request, season=_current_season()):
    pickups = FantasyPickup.objects.filter(season=season)

    deco = [(pickup.week, pickup.pick, pickup) for pickup in pickups]
    deco.sort()
    sorted_pickups = [pickup for _, _, pickup in deco]
    sorted_pickups.reverse()

    return render_to_response('league/pickups.html', {
        'pickups': sorted_pickups,
        'available_seasons': AVAILABLE_PICKUPS,
        'selected_season': season,
        }, context_instance=RequestContext(request))

def schedule(request, season=_current_season()):
    schedules = FantasySchedule.objects.filter(season=season)
    return render_to_response('league/schedule.html', {
        'schedules': schedules,
        'available_seasons': AVAILABLE_SCHEDULES,
        'selected_season': season,
        }, context_instance=RequestContext(request))

def trophy(request):
    return render_to_response('league/trophy.html', {
        }, context_instance=RequestContext(request))
