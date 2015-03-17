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

class StorageInline(admin.TabularInline):
    model = models.Storage

@admin.register(models.FixityAlgorithm)
class FixityAlgorithmAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)

@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_pull_date')
    list_display_links = ('name',)
    filter_horizontal = ('replicate_from', 'replicate_to',
                         'restore_from', 'restore_to')
    inlines = [StorageInline]

@admin.register(models.Bag)
class BagAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'original_node', 'size', 'bag_type')
    list_display_links = ('uuid',)
    list_filter = ('bag_type', 'original_node', 'updated_at')
    readonly_fields = ('rights', 'interpretive', 'replicating_nodes')
    search_fields = ['uuid',]

@admin.register(models.ReplicationTransfer)
class ReplicationTransferAdmin(admin.ModelAdmin):
    list_display = ('replication_id', 'fixity_nonce',
                    'fixity_value', 'link')
    list_filter = ('protocol', 'from_node', 'to_node', 'fixity_algorithm',
                   'fixity_accept', 'bag_valid', 'status')
    list_display_links = ['replication_id']
    search_fields = ['replication_id',]


@admin.register(models.RestoreTransfer)
class RestoreTransferAdmin(admin.ModelAdmin):
    list_display = ('restore_id', 'link')
    list_filter = ('protocol', 'from_node', 'to_node', 'status')
    readonly_fields = ('bag',)
    list_display_links = ['restore_id']
    search_fields = ['restore_id',]


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
