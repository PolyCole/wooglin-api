from django.contrib import admin
from restapi.models.members import Member
from restapi.models.sober_bros import SoberBro
from restapi.models.sober_bro_shifts import SoberBroShift

# Register your models here.
admin.site.register(Member)
admin.site.register(SoberBro)
admin.site.register(SoberBroShift)
