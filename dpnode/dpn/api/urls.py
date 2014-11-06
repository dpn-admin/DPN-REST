from django.conf.urls import patterns, url
from dpn.api.views import TransferListView, RegistryListView, NodeListView
from dpn.api.views import TransferDetailView, RegistryDetailView, NodeDetailView

urlpatterns = patterns('',
      url(r'^registry/$', RegistryListView.as_view(), name="data-list"),
      url(r'^transfer/$', TransferListView.as_view(), name="event-list"),
      url(r'^node/$', NodeListView.as_view(), name="node-list"),
      url(r'^registry/(?P<dpn_object_id>.+)/$', RegistryDetailView.as_view(),
          name="data-detail"),
      url(r'^transfer/(?P<event_id>.+)/$', TransferDetailView.as_view(),
          name="event-detail"),
      url(r'node/(?P<namespace>.+)/$', NodeDetailView.as_view(), name="node-detail")
      )
