from django import forms
from django.db.models import Q
from butkus.ncf.models import *
from butkus.league.models import *
from butkus.team.models import *
from datetime import *

class PickupManipulator(forms.Manipulator):
    def __init__(self, team_id, drop_roster_id, season, week):

        players = Player.objects.eligible()
        
        player_choices = [(player.id, player.long_name) for player in players]        
        
        self.fields = (
            forms.SelectField(field_name="pickup", choices=player_choices),
        )

        self.team_id = team_id
        self.drop_roster_id = drop_roster_id
        self.season = season
        self.week = week

    def save(self, new_data):
        player_id = new_data["pickup"]

        this_week = int(self.week)
        last_week = this_week - 1
        
        # update drop
        roster_drop = FantasyRoster.objects.get(pk=self.drop_roster_id)
        roster_drop.last_season = self.season
        roster_drop.last_week = last_week

        # add new roster stop
        roster_pickup = FantasyRoster(team_id=self.team_id, player_id=player_id, first_season=self.season, first_week=this_week)

        # figure out the next pickup #
        weeks_pickups = FantasyPickup.objects.filter(season=self.season, week=last_week).order_by('-pick')        
        if (len(weeks_pickups) > 0):
            pick = int(weeks_pickups[0].pick) + 1
        else:
            pick = 1

        # make sure team did not make two pickups already
        #teams_weeks_pickups = FantasyPickup.objects.filter(season=self.season, week=self.week, team_id=self.team_id)
        #print "teams_weeks_pickups: %s" % (teams_weeks_pickups,)
        #if (teams_weeks_pickups != None && len(teams_weeks_pickups >= 2)):
         #   raise "Team has already made two pickups for the week"

        # insert a pickup record
        pickup = FantasyPickup(team_id=self.team_id, player_picked_id=player_id,
                               player_dropped_id=roster_drop.player.id,
                               season=self.season, week=last_week, pick=pick)
        roster_drop.save()
        roster_pickup.save()
        pickup.save()


class StartersManipulator(forms.Manipulator):
    def __init__(self, team_id, season, week):
        fantasy_eligibilities = FantasyEligibility.objects.filter(season=season)
        eligibility_map = {}
        for fe in fantasy_eligibilities:
            eligibility_map[fe.fantasy_position] = fe.ncf_positions            
        
        starters = FantasyStarter.objects.filter(team=team_id, season=season, week=week)

        # create starter info out of FantasyStarter records
        starter_infos = [{'position':starter.position, 'player':starter.player} for starter in starters]

        # add eligible replacements
        eligible_rosters = FantasyRoster.objects.eligible(team_id=team_id, season=season, week=week)
        for starter_info in starter_infos:
            position = starter_info['position']
            ncf_positions = eligibility_map[position]
            eligible = self.choices(self.filter_by_position(eligible_rosters, ncf_positions))
            starter_info['eligible'] = eligible

        print "starter_infos", starter_infos            

        self.fields = (
            forms.SelectField(field_name="RB", choices=[]),
        )

        self.team_id = team_id
        self.season = season
        self.week = week        

    def filter_by_position(self, rosters, positions):
        return [roster for roster in rosters if roster.player.position in positions]

    def choices(self, rosters):
        return [(roster.id, roster.player.name) for roster in rosters]        

    def save(self, new_data):
        pass        
