# This script was used originally for the first step of the create-ietf-999-for-asb.py
# script, which was then further modified. See that script for further explanation.

import django
django.setup()

from ietf.meeting.models import *

existing_meeting = Meeting.objects.get(number='106')

print('##### ROOMS #####\n')

for room in existing_meeting.room_set.all():
    print(f"r = Room.objects.create(meeting=m, name='{room.name}', capacity={room.capacity}, functional_name='{room.functional_name}')")
    if room.resources.count():
        print(f"r.resources.set(ResourceAssociation.objects.filter(pk__in={[r.pk for r in room.resources.all()]}))  # {[r for r in session.resources.all()]}")
    if room.session_types.count():
        print(f"r.session_types.set(TimeSlotTypeName.objects.filter(slug__in={[t.slug for t in room.session_types.all()]}))")

print('\n##### SESSIONS AND CONSTRAINTS #####\n')

for session in existing_meeting.session_set.filter(type_id='regular'):
    print(f"""## session for {session.group.acronym} ##
s = Session.objects.create(
    meeting=m,
    type_id="{session.type.pk}",
    group_id={session.group.pk},  # {session.group.acronym}
    attendees={session.attendees},
    agenda_note="{session.agenda_note}",
    requested_duration={repr(session.requested_duration)},  # {session.requested_duration}
    comments=\"\"\"{session.comments}\"\"\",
    remote_instructions="{session.remote_instructions}",
)""")

    if session.joint_with_groups_acronyms():
        print(f"s.joint_with_groups.set(Group.objects.filter(acronym__in={session.joint_with_groups_acronyms()}))")
    if session.resources.count():
        print(f"s.resources.set(ResourceAssociation.objects.filter(pk__in={[r.pk for r in session.resources.all()]}))  # {[r for r in session.resources.all()]}")
    for constraint in session.constraints():
        print(f"c = Constraint.objects.create(meeting=m, source=s.group, name_id='{constraint.name.slug}', ", end='')
        if constraint.target:
            print(f"target_id={constraint.target.pk}, ", end='')
        if constraint.person:
            print(f"person_id={constraint.person.pk}, ", end='')
        if constraint.time_relation:
            print(f"time_relation='{constraint.time_relation}', ", end='')
        print(")", end='')
        if constraint.target or constraint.person:
            print(f'  # ', end='')
        if constraint.target:
            print(constraint.target.acronym, end='')
        if constraint.person:
            print(constraint.person, end='')
        print('')
        if constraint.timeranges.count():
            print(f"c.timeranges.set(TimeRange.objects.filter(slug__in={[t.slug for t in constraint.timeranges.all()]}))")

    print('')

print('##### TIMESLOTS #####\n')

for timeslot in existing_meeting.timeslot_set.all():
    location = 'None'
    if timeslot.location:
        location = f'Room.objects.get(meeting=m, name="{timeslot.location.name}")'
    print(f'## timeslot {timeslot.time} length {timeslot.duration} in {timeslot.location} ##')
    print(f'TimeSlot.objects.create(meeting=m, type_id="{timeslot.type.pk}", name="{timeslot.name}", time={repr(timeslot.time)}, duration={repr(timeslot.duration)}, location={location}, show_location={timeslot.show_location})')
