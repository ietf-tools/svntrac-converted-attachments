# -*- coding: utf-8 -*-
import sys
from datetime import datetime
from ietf.idtracker.models import Area, Acronym, AreaDirector, AreaStatus, PersonOrOrgInfo

LABEL_OTHER = "Other"

# remove the existing one
if Acronym.objects.filter(acronym=LABEL_OTHER).count() > 0 :
        __acronym = Acronym.objects.get(acronym=LABEL_OTHER)
        __acronym.delete()

# insert into acronym
__acronym = Acronym(acronym=LABEL_OTHER, name=LABEL_OTHER, name_key=LABEL_OTHER)
__acronym.save()

# insert into area
# get status
__status = AreaStatus.objects.get(status_id=1)

__area = Area(area_acronym=__acronym, start_date=datetime.now(), status=__status, last_modified_date=datetime.now())
__area.save()

# insert into area_directors
# get IETF and IAB chair from 'chair'.
# mysql>  select * from chairs where chair_name in ('IETF', 'IAB');
# in development data, the if of person_or_org_tag are 5376, 100454.
__persons = PersonOrOrgInfo.objects.filter(person_or_org_tag__in=[5376, 100454, ])

for i in __persons :
        AreaDirector(area=__area, person=i).save()

sys.exit(0)

"""
Description
-----------


ChangeLog
---------


Usage
-----
change directory to ietf source and run this script like this,
shell> python insert_other_area_in_non_wg_mailinglist.py

"""

__author__ =  "Spike^ekipS <spikeekips@gmail.com>"
__version__=  "0.1"
__nonsense__ = ""



