import random

order=[
    "Derek",
    "Reid",
    "Simon",
    "Brian",
    "Mike",
    "Jeff",
    "Brandon",
    "Jon"
    ]

def team(position):
    return order[position-1]

uniques =[
    [(1,2),(3,4),(5,6),(7,8)],
    [(1,3),(2,4),(5,7),(6,8)],
    [(1,4),(2,3),(5,8),(6,7)],
    [(1,5),(2,6),(3,7),(4,8)],
    [(1,6),(2,5),(3,8),(4,7)],
    [(1,7),(2,8),(3,5),(4,6)],
    [(1,8),(2,7),(3,6),(4,5)]
           ]

schedule=[
    uniques[0],
    uniques[1],
    uniques[2],
    uniques[3],
    uniques[4],
    uniques[5],
    uniques[6],
    uniques[0],
    uniques[1],
    uniques[2],
    uniques[3],
    uniques[4],
    uniques[5]
           ]

def validate(schedule):
    if (uniques[0] != schedule[0]):
        return False
    last_weeks_schedule = None
    for weekly_schedule in schedule:
        if (weekly_schedule == last_weeks_schedule):
            return False
        last_weeks_schedule = weekly_schedule
    return True

valid = False
while (valid == False):
    random.shuffle(schedule)
    valid = validate(schedule)

week = 1
print "\nSchedule\n"
for weekly_schedule in schedule:
    print "\nWeek %s\n" % (week,)
    week = week + 1
    for matchup in weekly_schedule:
        print "%s vs. %s" % (team(matchup[0]), team(matchup[1]))
