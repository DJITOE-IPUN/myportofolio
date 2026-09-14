from django.contrib import admin
from main.models import Experience, Education, Award

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'category', 'date_range', 'is_ongoing')
    list_filter = ('category', 'is_ongoing')
    search_fields = ('title', 'organization', 'description')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('institution', 'degree', 'field_of_study', 'date_range')
    list_filter = ('degree',)
    search_fields = ('institution', 'field_of_study')

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ('title', 'issuer', 'category', 'date_awarded')
    list_filter = ('category',)
    search_fields = ('title', 'issuer')