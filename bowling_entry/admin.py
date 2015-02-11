from django.contrib import admin
from bowling_entry import models as bowling_models

# Register your models here.
admin.site.register(bowling_models.League)
admin.site.register(bowling_models.TeamDefinition)
admin.site.register(bowling_models.BowlerDefinition)
admin.site.register(bowling_models.Match)
admin.site.register(bowling_models.TeamInstance)
admin.site.register(bowling_models.TeamInstanceBowler)
admin.site.register(bowling_models.Week)