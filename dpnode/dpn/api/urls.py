from django.conf.urls import patterns, url
from dpn.api.views import TransferListView, RegistryListView, NodeListView
from dpn.api.views import TransferDetailView, RegistryDetailView, NodeDetailView

urlpatterns = patterns('',
      url(r'^data/$', RegistryListView.as_view(), name="data-list"),
      url(r'^event/$', TransferListView.as_view(), name="event-list"),
      url(r'^node/$', NodeListView.as_view(), name="node-list"),
      url(r'^data/(?P<dpn_object_id>.+)/$', RegistryDetailView.as_view(),
          name="data-detail"),
      url(r'^event/(?P<event_id>.+)/$', TransferDetailView.as_view(),
          name="event-detail"),
      url(r'node/(?P<pk>.+)/$', NodeDetailView.as_view(), name="node-detail")
      )
