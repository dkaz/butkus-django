from django.db import models
from django.contrib.auth.models import User
from butkus.ncf.models import Team, Player, Schedule
from datetime import *

SEASONS = (
    (2000, '2000'),
    (2001, '2001'),
    (2002, '2002'),
    (2003, '2003'),
    (2004, '2004'),
    (2005, '2005'),
    (2006, '2006'),
    (2007, '2007'),
)

PICKUP_WEEKS = (
    (1, 'Week 1'),
    (2, 'Week 2'),
    (3, 'Week 3'),
    (4, 'Week 4'),
    (5, 'Week 5'),
    (6, 'Week 6'),
    (7, 'Week 7'),
    (8, 'Week 8'),
    (9, 'Week 9'),
    (10, 'Week 10'),
    (11, 'Week 11'),
    (12, 'Week 12'),
)

WEEKS = (
    (1, 'Week 1'),
    (2, 'Week 2'),
    (3, 'Week 3'),
    (4, 'Week 4'),
    (5, 'Week 5'),
    (6, 'Week 6'),
    (7, 'Week 7'),
    (8, 'Week 8'),
    (9, 'Week 9'),
    (10, 'Week 10'),
    (11, 'Week 11'),
    (12, 'Week 12'),
    (13, 'Week 13'),
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

STATS_BY_POSITION = {
    'QB': ('pass_yds','rush_yds','pass_tds','rush_tds','pass_int'),
    'QB1': ('pass_yds','rush_yds','pass_tds','rush_tds','pass_int'),
    'QB2': ('pass_yds','rush_yds','pass_tds','rush_tds','pass_int'),
    'RB': ('recv_yds','recv_tds','rush_yds','rush_tds'),
    'RB/WR': ('recv_yds','recv_tds','rush_yds','rush_tds'),
    'WR': ('recv_yds','recv_tds','rush_yds','rush_tds'),
    'TE': ('recv_yds','recv_tds'),
    'K': ('fg30','fg40','fg50','xp','xp_miss'),
    'D': ('pts_allow','def_fumbles','def_ints','def_sacks'),
    'PR': ('pr_yards','pr_tds','pr_td_yards'),
    'KR': ('kr_yards','kr_tds','kr_td_yards')
}

CURRENT_SEASON = 2007

class FantasyTeam(models.Model):
    owner = models.ForeignKey(User, unique=True, related_name="fantasy_teams")
    season_joined = models.CharField(maxlength=4, choices=SEASONS)

    def __str__(self):
        return self.owner.first_name

    class Admin:
        pass

    def _get_name(self):
        return "%s's Team" % (self.owner.first_name)

    def _get_owner_private_name(self):
        return "%s %s." % (self.owner.first_name, self.owner.last_name[0])
    
    owner_private_name = property(_get_owner_private_name)
    name = property(_get_name)

class FantasyDraft(models.Model):
    season = models.CharField(maxlength=4, choices=SEASONS)
    pick = models.IntegerField()
    round = models.IntegerField()
    team = models.ForeignKey(FantasyTeam, related_name="draft_picks")
    slot_owner = models.ForeignKey(FantasyTeam, related_name="draft_slots")
    player = models.ForeignKey(Player, related_name="draft_positions")

    def __str__(self):
        return "year:%s round:%d pick:%d player:%s" % (self.season, self.round, self.pick, self.player.name)

    class Admin:
        pass

    class Meta:
        ordering = ['season', 'pick']  

    def _is_traded(self):
        return (self.team != self.slot_owner)
    
    traded = property(_is_traded)

class FantasyScheduleManager(models.Manager):
    def current(self):
        today = date.today()
        if (today.month == 7 or today.month == 8):
            return self.filter(first_date__gte=today).order_by('first_date')[0]
        else:
            return self.filter(first_date__lte=today).order_by('-first_date')[0]
            
    def weeks(self, season):
        season_schedules = self.filter(season=season)
        return range(1, len(season_schedules) + 1)
    
class FantasySchedule(models.Model):
    season = models.CharField(maxlength=4, choices=SEASONS)
    week = models.IntegerField(choices=WEEKS)
    first_date = models.DateField()
    last_date = models.DateField()
    objects = FantasyScheduleManager()

    def __str__(self):
        return "%s, week %s: %s - %s" % (self.season, self.week, self.first_date, self.last_date)

    class Admin:
        pass

    class Meta:
        unique_together = (("season", "week"),)

class FantasyPickup(models.Model):
    season = models.CharField(maxlength=4, choices=SEASONS)
    week = models.IntegerField(choices=PICKUP_WEEKS)
    pick = models.IntegerField()
    team = models.ForeignKey(FantasyTeam, related_name="pickups")
    player_picked = models.ForeignKey(Player, related_name="pickups")
    player_dropped = models.ForeignKey(Player, related_name="drops") 

    def __str__(self):
        return "%s - %s - %s" % (self.season, self.week, self.player_picked.name)

    class Admin:
        pass

    class Meta:
        unique_together = (("season", "week", "pick"),
                           ("season", "week", "player_picked"),
                           ("season", "week", "player_dropped"))
        ordering = ['season', 'pick']  

    def _is_traded(self):
        return (self.team != self.slot_owner)
    
    traded = property(_is_traded)

class FantasyEligibility(models.Model):
    season = models.CharField(maxlength=4, choices=SEASONS, default=CURRENT_SEASON)
    fantasy_position = models.CharField(maxlength=5)
    ncf_positions = models.CharField(maxlength=30) # comma-separated positions
    count = models.IntegerField()
    
    def __str__(self):
        return "%s - %sx %s" % (self.season, self.count, self.fantasy_position)

    class Admin:
        pass

class FantasyStanding(models.Model):
    season = models.CharField(maxlength=4, choices=SEASONS)
    team = models.ForeignKey(FantasyTeam, related_name="standings")
    week1 = models.IntegerField(blank=True, null=True)
    week2 = models.IntegerField(blank=True, null=True)
    week3 = models.IntegerField(blank=True, null=True)
    week4 = models.IntegerField(blank=True, null=True)
    week5 = models.IntegerField(blank=True, null=True)
    week6 = models.IntegerField(blank=True, null=True)
    week7 = models.IntegerField(blank=True, null=True)
    week8 = models.IntegerField(blank=True, null=True)
    week9 = models.IntegerField(blank=True, null=True)
    week10 = models.IntegerField(blank=True, null=True)
    week11 = models.IntegerField(blank=True, null=True)
    week12 = models.IntegerField(blank=True, null=True)
    week13 = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return "year:%s team:%s" % (self.season, self.team.owner_private_name)

    class Admin:
        pass

    class Meta:
        unique_together = (("season", "team"),)

    def _get_weeks(self):
        return [self.week1,self.week2,self.week3,self.week4,
                self.week5,self.week6,self.week7,self.week8,
                self.week9,self.week10,self.week11,self.week12,
                self.week13]

    def _get_weeks12(self):
        return [self.week1,self.week2,self.week3,self.week4,
                self.week5,self.week6,self.week7,self.week8,
                self.week9,self.week10,self.week11,self.week12]

    def _get_overall(self):
        overall = 0
        for week in self.weeks:
            if week != None: overall += week
        return overall
    
    overall = property(_get_overall)
    weeks = property(_get_weeks)
    weeks12 = property(_get_weeks12)

class FantasyScoring:
    def stats(self, method):
        return STATS_BY_POSITION[method]
        
    def total(self, method, statline):
        if method == 'QB1':
            return (statline.pass_yds / 25) + (statline.pass_tds * 6) - (statline.pass_int * 2) + (statline.rush_yds / 10) + (statline.rush_tds * 4)
        elif method == 'QB2':
            return (statline.pass_yds / 25) + (statline.pass_tds * 4) - (statline.pass_int * 3) + (statline.rush_yds / 10) + ((statline.rush_yds / 50) * 2) + (statline.rush_td * 6)
        elif method == 'RB/WR':
            return (statline.rush_yds / 10) + (statline.rush_tds * 6) + (statline.recv_yds / 10) + (statline.recv_tds * 6)
        elif method == 'TE':
            return (statline.recv_yds / 10) + ((statline.recv_yds / 50) * 2) + (statline.recv_tds * 6)
