from django.conf.urls import patterns, url

from rest_framework import routers
from dpn.api.views import ReplicationTransferListView, RestoreTransferListView
from dpn.api.views import BagListView, NodeListView
from dpn.api.views import BagDetailView, NodeDetailView
from dpn.api.views import ReplicationTransferDetailView, RestoreTransferDetailView



urlpatterns = patterns('',
      url(r'^bag/$', BagListView.as_view(),
          name="bag-list"),
      url(r'^replicate/$', ReplicationTransferListView.as_view(),
          name="replication-list"),
      url(r'^restore/$', RestoreTransferListView.as_view(),
          name="restore-list"),
      url(r'^node/$', NodeListView.as_view(),
          name="node-list"),
      url(r'^bag/(?P<uuid>.+)/$', BagDetailView.as_view(),
          name="bag-detail"),
      url(r'^replicate/(?P<replication_id>.+)/$',
          ReplicationTransferDetailView.as_view(),
          name="replication-detail"),
      url(r'^restore/(?P<restore_id>.+)/$',
          RestoreTransferDetailView.as_view(),
          name="restore-detail"),
      url(r'node/(?P<namespace>.+)/$', NodeDetailView.as_view(),
          name="node-detail")
      )
