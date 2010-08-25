import sys
sys.path.append('..')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import csv
import optparse
import string
from datetime import *

from django.core.exceptions import ObjectDoesNotExist
from butkus.ncf.models import *
from butkus.league.models import *
from butkus.team.models import *

def load_draft():
    for line in open('data/draft-2006.csv', 'r').readlines():
        round, pick, fantasy_team, player = string.split(line, ',')
        if (player.count('-') == 0):
            toks = string.split(player, ' ')
            team_name = ' '.join(toks[:-1])
            team = Team.objects.get(name=team_name)
            player = Player.objects.get(last_name='Team', team=team)
        else:
            toks = string.split(player, ' ')
            first_name = toks[0]
            last_name = toks[1]
            team_name = ' '.join(toks[3:-1])
            team = Team.objects.get(name=team_name)
            player = Player.objects.get(last_name=last_name, first_name=first_name, team=team)

        toks = string.split(fantasy_team, ' ')
        user = User.objects.get(first_name=toks[0])
        owner = FantasyTeam.objects.get(owner=user)

        if (len(toks) > 1):
            slot_user = User.objects.get(first_name=toks[2][:-1])
            slot_owner = FantasyTeam.objects.get(owner=slot_user)
        else:
            slot_owner = owner

        draft = FantasyDraft(season="2006", pick=int(pick), round=int(round),
                             team=owner, slot_owner=slot_owner, player=player)
        draft.save()
                            
def load_draft_2005():
    for line in open('data/draft-2005.csv', 'r').readlines():
        print string.split(line, ',')
        round, pick, fantasy_team, player = string.split(line, ',')
        
        if (player.count('Defense') == 0):
            name, position, team_name = string.split(player.rstrip(), '/')
            first_name, last_name = string.split(name, ' ', 1)
            team = Team.objects.get(name=team_name)
            player = Player.objects.get(last_name=last_name, first_name=first_name, team=team)

        else:
            toks = string.split(player, ' ')
            team_name = ' '.join(toks[:-1])
            team = Team.objects.get(name=team_name)
            player = Player.objects.get(position='D', team=team)
 
        toks = string.split(fantasy_team.rstrip(), ' ')
        user = User.objects.get(first_name=toks[0])
        owner = FantasyTeam.objects.get(owner=user)

        if (len(toks) > 1):
            slot_user = User.objects.get(first_name=toks[2][:-1])
            slot_owner = FantasyTeam.objects.get(owner=slot_user)
        else:
            slot_owner = owner

        draft = FantasyDraft(season="2005", pick=int(pick), round=int(round),
                             team=owner, slot_owner=slot_owner, player=player)
        draft.save()

def load_draft_2002():
    order = {}
    reader = csv.reader(open("data/draft-2002.csv"))
    for line in reader:
        if (len(line) == 0):
            break
        order[line[2]] = line[1]
    print order
                    
def load_fantasy_schedules():
    first_date = date(2006, 8, 22)
    for week in range(1, 13):
        first_date = first_date + timedelta(days=7)
        last_date = first_date + timedelta(days=6)
        schedule = FantasySchedule(season='2006', week=week, first_date=first_date, last_date=last_date)
        schedule.save()
        
def load_conferences():
    for line in open('data/conferences.csv', 'r').readlines():
        id, name, division = string.split(line, ',')
        conference = Conference(id=id.rstrip(), name=name.rstrip(), division=division.rstrip())
        conference.save()
    
def load_teams():
    for line in open('data/teams.csv', 'r').readlines():
        id, conference_id, name, nickname = string.split(line, ',')
        team = Team(id=id.rstrip(), conference_id=conference_id.rstrip(), name=name.rstrip(), nickname=nickname.rstrip())
        team.save()

def load_schedules():
    reader = csv.reader(open("data/schedules-2007.csv"))
    for team_id, team_name, datestring, opponent_id, opponent_name, location in reader:
        if (len(location)):
            location = location[0]
        schedule = Schedule(team_id=int(team_id.rstrip()), opponent_id=int(opponent_id.rstrip()), date=__to_date(datestring), location=location.rstrip(), season=2007)
        schedule.save()

def load_fantasy_rosters_2006_1():
    reader = csv.reader(open("data/fantasy-rosters-2006-1.csv"))
    for team_name, position, player_name, school_name, eligibility, origin in reader:
        team_name = team_name.rstrip()
        position = position.rstrip()
        player_name = player_name.rstrip()
        school_name = school_name.rstrip()
        eligibility = eligibility.rstrip()
        origin = origin.rstrip()

        if (team_name.count('\'') > 0):
            owner_name, junk = string.split(team_name, '\'')

        user = User.objects.get(first_name=owner_name)
        fantasy_team = FantasyTeam.objects.get(owner=user)

        school = Team.objects.get(name=school_name)

        if (school_name == player_name):
            player = Player.objects.get(position='D', team=school)
        else:            
            toks = string.split(player_name, ' ')
            if (player_name.count('Jr') > 0):
                first_name = toks[0]
                last_name = ' '.join(toks[1:])
            else:
                first_name = ' '.join(toks[:-1])
                last_name = toks[-1]
            #print "FIRST:%s LAST:%s" % (first_name, last_name)
            player = Player.objects.get(first_name=first_name, last_name=last_name, team=school)

        print "REC: %s %s" % (fantasy_team, player)

        roster = FantasyRoster(team=fantasy_team, player=player, first_week=1, first_season=2006)
        roster.save()

def load_rosters():
    season = 2007
    reader = csv.reader(open("data/rosters-" + str(season) + ".csv"))
    for team_id, team_name, number, last_name, first_name, position, eligibility, ncaa_player_id in reader:
        team_id = team_id.rstrip()
        number = number.rstrip().strip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        first_name = first_name.rstrip()
        last_name = last_name.rstrip()
        position = position.rstrip()
        eligibility = eligibility.rstrip()
        ncaa_player_id = ncaa_player_id.rstrip()

        print "Processing player id:%s (%s %s)" % (ncaa_player_id, first_name, last_name)

        try:
            player = Player.objects.get(ncaa_player_id=ncaa_player_id)
            player.first_name = first_name
            player.last_name = last_name
            player.position = position
            player.eligibility = eligibility
            player.team_id = team_id
            player.save()        
        except ObjectDoesNotExist:
            player = Player(team_id=team_id, last_name=last_name, first_name=first_name,
                            position=position, eligibility=eligibility, ncaa_player_id=ncaa_player_id)
            player.save()        

        try:
            roster = Roster.objects.get(ncaa_player_id=ncaa_player_id, season=season)
        except ObjectDoesNotExist:
            roster = Roster(player=player, team_id=team_id, number=number, last_name=last_name, first_name=first_name,
                            position=position, eligibility=eligibility, ncaa_player_id=ncaa_player_id, season=season)
            roster.save()

def load_starter_games():
    season = 2006
    for starter in FantasyStarter.objects.filter(season=season):
        if (starter.player == None):
            continue
        
        schedule_week = FantasySchedule.objects.get(season=season, week=starter.week)
        games = Schedule.objects.filter(team=starter.player.team, date__range=(schedule_week.first_date, schedule_week.last_date))
        if (len(games) != 1):
            continue;

        starter.game = games[0]
        starter.save()
    
def load_starters():
    season = 2006
    for fantasy_season in FantasySeason.objects.filter(season=season):
        team = fantasy_season.team
        for week in range(1, 12+1):
            for slot in FantasyEligibility.objects.all():
                for slot_count in range(1, slot.count+1):
                    starter = FantasyStarter(season=slot.season, week=week, position=slot.fantasy_position, team=team)
                    starter.save()

def load_starters_13():
    for s12 in FantasyStarter.objects.filter(season=2006, week=12):
        s13 = FantasyStarter(season=2006, week=13, position=s12.position, team=s12.team)
        s13.save()
        
def load_eligibility():
    for el in FantasyEligibility.objects.all():
        elnew = FantasyEligibility(season=2007, fantasy_position=el.fantasy_position, ncf_positions=el.ncf_positions, count=el.count)     
        elnew.save()   
        

def __to_date(datestring):
    datestring = datestring.rstrip()
    month, day, year = string.split(datestring.rstrip(), '/')
    day = int(day)
    month = int(month)
    year = int(year)
    if (year < 100):
        year = year + 2000
    return date(year, month, day)

def main():
    parser = optparse.OptionParser(usage='%prog [options]')
    parser.add_option('--conferences', action='store_true', dest='conferences', help='Load NCAA conferences.')
    parser.add_option('--draft', action='store_true', dest='draft', help='Load NCAA conferences.')
    parser.add_option('--eligibility', action='store_true', dest='eligibility', help='Load eligibilities.')
    parser.add_option('--rosters', action='store_true', dest='rosters', help='Load NCAA teams.')
    parser.add_option('--schedules', action='store_true', dest='schedules', help='Load NCAA schedules.')
    parser.add_option('--starters', action='store_true', dest='starters', help='Load NCAA starters.')
    parser.add_option('--teams', action='store_true', dest='teams', help='Load NCAA teams.')
    options = parser.parse_args()[0]
    
    if options.conferences:
        load_conferences()
    elif options.teams:
        load_teams()
    elif options.starters:
        load_starters_13()
    elif options.schedules:
        load_schedules()
    elif options.rosters:
        load_rosters()
    elif options.draft:
        load_draft_2002()
    elif options.eligibility:
        load_eligibility()
    else:
        print "Unknown option"
        

if __name__ == '__main__':
    main()

#~

