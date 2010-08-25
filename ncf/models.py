from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User

DIVISIONS = (
    ('I-A', 'Division I-A'),
    ('I-AA', 'Division I-AA'),
)

class ConferenceManager(models.Manager):
    def eligible(self):
        return self.filter(Q(pk=1) | Q(pk=2) | Q(pk=3) | Q(pk=4) | Q(pk=6) | Q(pk=7))

class Conference(models.Model):
    objects = ConferenceManager()
    id = models.IntegerField(primary_key=True)
    name = models.CharField(maxlength=20)
    division = models.CharField(maxlength=10, default="I-A", choices=DIVISIONS)
    objects = ConferenceManager()

    def __str__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        ordering = ['name']

class TeamManager(models.Manager):
    def eligible(self):
        eligible_conferences = Conference.objects.eligible()
        return self.filter(Q(conference__in=eligible_conferences) | Q(pk=513))

class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    conference = models.ForeignKey(Conference, related_name="teams")
    name = models.CharField(maxlength=20)
    nickname = models.CharField(maxlength=20)
    objects = TeamManager()

    def __str__(self):
        return self.name + " " + self.nickname

    class Admin:
        pass

    class Meta:
        ordering = ['name']

    def _get_long_name(self):
        return self.name + " " + self.nickname

    long_name = property(_get_long_name)

LOCATIONS = (
    ('H', 'Home'),
    ('A', 'Away'),
    ('N', 'Neutral Site'),
)

ELIGIBILITIES = (
    ('FR', 'Freshman'),
    ('SO', 'Sophomore'),
    ('JR', 'Junior'),
    ('SR', 'Senior'),
)

SEASONS = (
    ('2005', '2005'),
    ('2006', '2006'),
)

class Schedule(models.Model):
    team = models.ForeignKey(Team, related_name="schedules")
    opponent =  models.ForeignKey(Team, related_name="opponent_schedules")
    date = models.DateField()
    location = models.CharField(maxlength=1, choices=LOCATIONS)
    season = models.CharField(maxlength=4, choices=SEASONS)
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, related_name="schedules_edited", blank=True, null=True)

    def __str__(self):
        return "%d vs. %d (%s)" % (self.team_id, self.opponent_id, self.season)

    class Admin:
        pass

    class Meta:
        ordering = ['date']

    def _is_home(self):
        if (self.location == 'H'):
            return True
        else:
            return False

    def _is_away(self):
        if (self.location == 'A'):
            return True
        else:
            return False
    
    def _is_neutral(self):
        if (self.location == 'N'):
            return True
        else:
            return False

    home = property(_is_home)
    away = property(_is_away)
    neutral = property(_is_neutral)

class PlayerManager(models.Manager):
    def eligible(self):
        eligible_teams = Team.objects.eligible()
        return self.filter(team__in=eligible_teams, position__in=('QB','RB','WR','TE','K','D'))

class Player(models.Model):    
    ncaa_player_id = models.IntegerField(blank=True, null=True, unique=True)
    team = models.ForeignKey(Team, related_name="players")
    first_name = models.CharField(maxlength=20)
    last_name = models.CharField(maxlength=20)
    nickname = models.CharField(maxlength=20, blank=True, null=True)
    position = models.CharField(maxlength=5)
    eligibility = models.CharField(maxlength=2, choices=ELIGIBILITIES)
    objects = PlayerManager()
    
    class Admin:
        pass

    class Meta:
        ordering = ['last_name', 'first_name']  

    def __str__(self):
        return "%s, %s (%s)" % (self.last_name, self.first_name, self.position)

    def _get_name(self):
        if (len(self.first_name) > 0):
            return self.first_name + " " + self.last_name
        else:
            return 'Defense'

    def _get_pos(self):
        if (self.last_name == "Team"):
            return "D"
        else:
            return self.position

    def _get_long_name(self):
        return "%s, %s (%s, %s)" % (self.last_name, self.first_name, self.position, self.team.name)

    def _get_position_order(self):
        positions = ['QB','RB','WR','TE','K','D']
        if (self.position in positions):
            return positions.index(self.position)
        else:
            print "ERROR: Unexpected position:%s" % self.position
            return len(positions) + 1
    
    name = property(_get_name)
    long_name = property(_get_long_name)
    pos = property(_get_pos)    
    position_order = property(_get_position_order)    


VIDEO_SITES = (
    ('YouTube', 'YouTube'),
    ('Misc', 'Miscallenous'),
)

class PlayerVideo(models.Model):
    player = models.ForeignKey(Player, related_name="videos")
    name = models.CharField(maxlength=20)
    video_site = models.CharField(maxlength=20, choices=VIDEO_SITES)
    video_url = models.CharField(maxlength=30, blank=True, null=True)
    video_id = models.CharField(maxlength=30, blank=True, null=True)

    class Admin:
        pass

    class Meta:
            pass

    def __str__(self):
        return self.name
    

class Roster(models.Model):
    player = models.ForeignKey(Player, related_name="roster_entries")
    ncaa_player_id = models.IntegerField()
    team = models.ForeignKey(Team, related_name="rosters")
    number = models.IntegerField()
    first_name = models.CharField(maxlength=20)
    last_name = models.CharField(maxlength=20)
    position = models.CharField(maxlength=5)
    eligibility = models.CharField(maxlength=2, choices=ELIGIBILITIES)
    season = models.CharField(maxlength=4, choices=SEASONS)
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, related_name="rosters_edited", blank=True, null=True)

    class Admin:
        pass

    class Meta:
        unique_together = (("ncaa_player_id", "season"),)

    def __str__(self):
        return self.last_name + ", " + self.first_name

    def _get_name(self):
        return self.first_name + " " + self.last_name

    def _get_year(self):
        if self.eligibility == 'FR':
            return 1
        elif self.eligibility == 'SO':
            return 2
        elif self.eligibility == 'JR':
            return 3
        else:
            return 4

    name = property(_get_name)
    year = property(_get_year)

class StatManager(models.Manager):
    def hash_all(self):
        stats = self.all()
        stat_hash = {}
        for stat in stats:
            stat_hash[stat.db_name] = stat
        return stat_hash

class Stat(models.Model):
    db_name = models.CharField(maxlength=15, unique=True)
    boxscore_name = models.CharField(maxlength=15)
    long_name = models.CharField(maxlength=30)
    objects = StatManager()

    def __str__(self):
        return self.long_name

    class Admin:
        pass

class PlayerGameStat(models.Model):
    player = models.ForeignKey(Player, related_name="game_stats")
    home_game = models.ForeignKey(Schedule, related_name="home_game_stats")
    away_game = models.ForeignKey(Schedule, related_name="away_game_stats")
    rush_att = models.IntegerField(blank=True, null=True, verbose_name="rushing attempts")
    rush_yds = models.IntegerField(blank=True, null=True, verbose_name="rushing yards")
    rush_tds = models.IntegerField(blank=True, null=True, verbose_name="rushing TDs")
    recv_catches = models.IntegerField(blank=True, null=True, verbose_name="receptions")
    recv_yds = models.IntegerField(blank=True, null=True, verbose_name="receiving yards")
    recv_tds = models.IntegerField(blank=True, null=True, verbose_name="receiving TDs")
    pass_att = models.IntegerField(blank=True, null=True, verbose_name="passing attempts") 
    pass_made = models.IntegerField(blank=True, null=True, verbose_name="passing completions") 
    pass_yds = models.IntegerField(blank=True, null=True, verbose_name="passing yards") 
    pass_tds = models.IntegerField(blank=True, null=True, verbose_name="passing TDs")
    pass_int = models.IntegerField(blank=True, null=True, verbose_name="INTs thrown")
    fumbles = models.IntegerField(blank=True, null=True, verbose_name="fumbles")
    fg30 = models.IntegerField(blank=True, null=True, verbose_name="FGs 0-39")
    fg40 = models.IntegerField(blank=True, null=True, verbose_name="FGs 40-49")
    fg50 = models.IntegerField(blank=True, null=True, verbose_name="FGs 50+")
    xp = models.IntegerField(blank=True, null=True, verbose_name="XPs")
    xp_miss = models.IntegerField(blank=True, null=True, verbose_name="XP misses")
    pts_allow = models.IntegerField(blank=True, null=True, verbose_name="points allowed (regular time)")
    def_fumbles = models.IntegerField(blank=True, null=True, verbose_name="defensive fumbles")
    def_ints = models.IntegerField(blank=True, null=True, verbose_name="defensive INTs")
    def_sacks = models.IntegerField(blank=True, null=True, verbose_name="defensive sacks")
    def_tds = models.IntegerField(blank=True, null=True, verbose_name="defensive TDs")
    def_safeties = models.IntegerField(blank=True, null=True, verbose_name="defensive safeties")
    pr_yards = models.IntegerField(blank=True, null=True, verbose_name="punt return yards")
    pr_tds = models.IntegerField(blank=True, null=True, verbose_name="punt return TDs")
    pr_td_yards = models.IntegerField(blank=True, null=True, verbose_name="punt return TD yards")
    kr_yards = models.IntegerField(blank=True, null=True, verbose_name="kickoff return yards")
    kr_tds = models.IntegerField(blank=True, null=True, verbose_name="kickoff return TDs")
    kr_td_yards = models.IntegerField(blank=True, null=True, verbose_name="kickoff return TD yards")
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, related_name="game_stats_edited", blank=True, null=True)
    
    class Admin:
        pass

    class Meta:
        unique_together = (("player", "home_game"),("player", "away_game"))
