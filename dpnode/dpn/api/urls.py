from django.conf.urls import patterns, url
from dpn.api.views import TransferListView, RegistryListView, NodeListView
from dpn.api.views import TransferDetailView, RegistryDetailView, NodeDetailView

urlpatterns = patterns('',
      url(r'^registry/$', RegistryListView.as_view(), name="registry-list"),
      url(r'^transfer/$', TransferListView.as_view(), name="transfer-list"),
      url(r'^node/$', NodeListView.as_view(), name="node-list"),
      url(r'^registry/(?P<dpn_object_id>.+)/$', RegistryDetailView.as_view(),
          name="registry-detail"),
      url(r'^transfer/(?P<event_id>.+)/$', TransferDetailView.as_view(),
          name="transfer-detail"),
      url(r'node/(?P<namespace>.+)/$', NodeDetailView.as_view(), name="node-detail")
      )
