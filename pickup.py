import sys
sys.path.append('..')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from datetime import *
import optparse
import string

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from butkus.ncf.models import *
from butkus.league.models import *
from butkus.team.models import *


def main():
    parser = optparse.OptionParser(usage='USAGE: pickup.py [user] [season] [week] [drop_first] [drop_last] [drop_school] [pickup_first] [pickup_last] [pickup_school_name]')
    options = parser.parse_args()

    if (len(options[1]) == 0):
        print parser.usage
        return
    
    args = options[1]

    user_first = args[0]
    season = args[1]
    week = int(args[2])
    drop_first = args[3]
    drop_last = args[4]
    drop_school = args[5]
    pickup_first = args[6]
    pickup_last = args[7]
    pickup_school_name = args[8]

    user = User.objects.get(first_name=user_first)
    fantasy_team = FantasyTeam.objects.get(owner=user)
    drop_player = 
    

        

if __name__ == '__main__':
    main()

#~

