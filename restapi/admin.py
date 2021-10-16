from django.contrib import admin
from restapi.models.members import Member
from restapi.models.sober_bros import SoberBro
from restapi.models.sober_bro_shifts import SoberBroShift
from restapi.models.events import Event
from restapi.models.event_attendances import EventAttendance
from restapi.models.guests import Guest
from restapi.models.aliases import Alias

# Register your models here.
admin.site.register(Member)
admin.site.register(SoberBro)
admin.site.register(SoberBroShift)
admin.site.register(Event)
admin.site.register(EventAttendance)
admin.site.register(Guest)
admin.site.register(Alias)
