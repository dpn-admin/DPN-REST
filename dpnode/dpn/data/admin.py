"""
    Creativity is allowing yourself to make mistakes. Art is knowing which ones
    to keep.
                                    - Scott Adams
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from dpn.data import models

class PortInline(admin.TabularInline):
    model = models.Port

class StorageInline(admin.TabularInline):
    model = models.Storage

@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'replicate_from', 'replicate_to',
                    'restore_from', 'restore_to', 'last_pull_date')
    list_display_links = ('name',)
    inlines = [PortInline, StorageInline]

@admin.register(models.RegistryEntry)
class RegistryEntryAdmin(admin.ModelAdmin):
    list_display = ('dpn_object_id', 'first_node', 'bag_size',
                    'object_type')
    list_display_links = ('dpn_object_id',)
    list_filter = ('object_type', 'first_node', 'updated_on')
    search_fields = ['dpn_object_id',]

@admin.register(models.Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'dpn_object_id', 'node',
                    'status', 'fixity', 'valid')
    list_filter = ('node', 'status', 'fixity', 'valid')
    list_display_links = ['event_id']
    search_fields = ['event_id',]

    def dpn_object_id(self, object):
        return object.registry_entry.dpn_object_id

@admin.register(models.Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    pass

# Some user stuff because where the hell else would I put it.
class UserTokenInline(admin.StackedInline):
    model = Token

class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, UserTokenInline)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)