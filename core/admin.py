from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Profile)
admin.site.register(models.Review)
admin.site.register(models.VolunteerWork)
admin.site.register(models.JoinRequest)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',),}
admin.site.register(models.Category,CategoryAdmin)