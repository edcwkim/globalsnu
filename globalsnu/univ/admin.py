from django.contrib import admin
from .models import Country, Report, School, SNUInWorld, Tag

admin.site.register(Country)
admin.site.register(School)
admin.site.register(SNUInWorld)
admin.site.register(Report)
admin.site.register(Tag)
