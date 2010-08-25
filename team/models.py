from django.db import models
from django.contrib.auth.models import User
from butkus.ncf.models import Team, Player, Schedule
from butkus.league.models import FantasyTeam

SEASONS = (
    ('2000', '2000'),
    ('2001', '2001'),
    ('2002', '2002'),
    ('2003', '2003'),
    ('2004', '2004'),
    ('2005', '2005'),
    ('2006', '2006'),
    ('2007', '2007'),
)

WEEKS = (
    ('1', 'Week 1'),
    ('2', 'Week 2'),
    ('3', 'Week 3'),
    ('4', 'Week 4'),
    ('5', 'Week 5'),
    ('6', 'Week 6'),
    ('7', 'Week 7'),
    ('8', 'Week 8'),
    ('9', 'Week 9'),
    ('10', 'Week 10'),
    ('11', 'Week 11'),
    ('12', 'Week 12'),
    ('13', 'Week 13'),
)

POSITIONS = (
    ('QB1', 'Passing QB'),
    ('QB2', 'All-around QB'),
    ('RB', 'RB'),
    ('WR', 'WR'),
    ('RB/WR', 'RB/WR'),
    ('TE', 'TE'),
    ('D', 'D'),
    ('K', 'K'),
    ('PR', 'PR'),
    ('KR', 'KR'),
)

class FantasySeason(models.Model):
    team = models.ForeignKey(FantasyTeam, related_name="fantasy_team_seasons")
    season = models.CharField(maxlength=4, choices=SEASONS)
    patron_team = models.ForeignKey(Team, related_name="patron_team_seasons")
    motto = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return "%s %s's %s" % (self.season, self.team.owner.first_name, self.patron_team.long_name)

    class Admin:
        pass

    class Meta:
        unique_together = (("team", "season"),)

    def _get_team_name(self):
        return "%s's %s" % (self.team.owner.first_name, self.patron_team.nickname)
    
    team_name = property(_get_team_name)

class FantasyRosterManager(models.Manager):
    def eligible(self, team_id, season, week, positions=None):
        if (positions == None):
            rosters = self.filter(team=team_id)
        else:
            rosters = self.filter(team=team_id, positions__in=positions)
            
        current_rosters = []    
        for roster in rosters:
            #print "season:%s week:%s to season:%s week:%s" % (roster.first_season, roster.first_week, roster.last_season, roster.last_week)
            if (roster.first_season > season):
                #print "FILTERED FIRST SEASON: %s > %s (%s)" % (roster.first_season, season, roster.player)
                pass
            elif (roster.first_season == season and roster.first_week > week):
                #print "FILTERED FIRST WEEK: %s > %s (%s)" % (roster.first_week, week, roster.player)
                pass
            elif (roster.last_season != None and roster.last_season < season):
                #print "FILTERED LAST SEASON: %s < %s (%s)" % (roster.last_season, season, roster.player)
                pass
            elif (roster.last_season != None and roster.last_season == season and roster.last_week < week):
                #print "FILTERED LAST WEEK: %s < %s (%s)" % (roster.last_week, week, roster.player)
                pass
            else:
                current_rosters.append(roster)

        if (len(current_rosters) != 22):
            print "ERROR: Illegal roster size: %s" % len(current_rosters)

        deco = [(roster.position_order, roster.player.name, roster) for roster in current_rosters]
        deco.sort()
        sorted_rosters = [roster for _, _, roster in deco]
        return sorted_rosters
        
class FantasyRoster(models.Model):
    team = models.ForeignKey(FantasyTeam, related_name="roster_entries")
    player = models.ForeignKey(Player, related_name="fantasy_roster_entries")
    first_season = models.IntegerField(choices=SEASONS)
    first_week = models.IntegerField(choices=WEEKS)
    last_season = models.IntegerField(choices=SEASONS, blank=True, null=True, default=None)
    last_week = models.IntegerField(choices=WEEKS, blank=True, null=True, default=None)
    edited_date = models.DateTimeField(blank=True, null=True)
    edited_by = models.ForeignKey(User, related_name="fantasy_rosters_edited", blank=True, null=True)
    objects = FantasyRosterManager()

    def __str__(self):
        return "%s - %s" % (self.team.owner.first_name, self.player.name)
        
    class Admin:
        pass

    class Meta:
        unique_together = (("first_season", "first_week", "player"),)

    def _get_position_order(self):
        return self.player.position_order
    position_order = property(_get_position_order)

    def _get_active(self):
        return (self.last_week == None)
    active = property(_get_active)

    def _get_name(self):
        return self.player.name
    name = property(_get_name)

class FantasyStarter(models.Model):
    team = models.ForeignKey(FantasyTeam, related_name="starter_entries")
    position = models.CharField(maxlength=5)
    season = models.IntegerField(choices=SEASONS)
    week = models.IntegerField(choices=WEEKS)
    roster = models.ForeignKey(FantasyRoster, related_name="starter_entries", blank=True, null=True)
    player = models.ForeignKey(Player, related_name="fantasy_starter_entries", blank=True, null=True)
    game = models.ForeignKey(Schedule, related_name="fantasy_starters", blank=True, null=True)
    edited_date = models.DateTimeField(blank=True, null=True)
    edited_by = models.ForeignKey(User, related_name="fantasy_starters_edited", blank=True, null=True)
        
    def __str__(self):
        return "%s (Week %s, %s) - %s" % (self.team.owner.first_name, self.week, self.season, self.position)

    class Admin:
        pass

    class Meta:
        pass

    def _get_player_name(self):
        if (self.player != None):
            return self.player.name
        else:
            return "(vacant)"
        
    def _get_position_order(self):
        positions = ['QB1','QB2','RB','RB/WR','WR','TE','K','D','PR','KR']
        if (self.position in positions):
            return positions.index(self.position)
        else:
            print "ERROR: Unexpected position:%s" % self.position
            return len(positions) + 1
        
    def _get_opponent_name(self):
        if (self.game == None):
            opponent_name = "OFF"
        elif (self.game.away):
            opponent_name = "@ %s" % (self.game.opponent.name)
        else:
            opponent_name = "%s" % (self.game.opponent.name)
        return opponent_name

    position_order = property(_get_position_order)
    player_name = property(_get_player_name)
    opponent_name = property(_get_opponent_name)

