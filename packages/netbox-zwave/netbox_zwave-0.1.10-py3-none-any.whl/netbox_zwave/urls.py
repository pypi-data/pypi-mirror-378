from django.urls import path, include
from . import views

app_name = 'netbox_zwave'
urlpatterns = [
    # Networks
    path('networks/', views.ZwaveNetworkListView.as_view(), name='zwavenetwork_list'),
    path('networks/add/', views.ZwaveNetworkEditView.as_view(), name='zwavenetwork_add'),
    path('networks/<int:pk>/', views.ZwaveNetworkView.as_view(), name='zwavenetwork'),
    path('networks/<int:pk>/edit/', views.ZwaveNetworkEditView.as_view(), name='zwavenetwork_edit'),
    path('networks/<int:pk>/delete/', views.ZwaveNetworkDeleteView.as_view(), name='zwavenetwork_delete'),
    
    # Devices
    path('devices/', views.ZwaveDeviceListView.as_view(), name='zwavedevice_list'),
    path('devices/add/', views.ZwaveDeviceEditView.as_view(), name='zwavedevice_add'),
    path('devices/<int:pk>/', views.ZwaveDeviceView.as_view(), name='zwavedevice'),
    path('devices/<int:pk>/edit/', views.ZwaveDeviceEditView.as_view(), name='zwavedevice_edit'),
    path('devices/<int:pk>/delete/', views.ZwaveDeviceDeleteView.as_view(), name='zwavedevice_delete'),
    
    # Command Classes
    path('command-classes/', views.ZwaveCommandClassListView.as_view(), name='zwavecommandclass_list'),
    path('command-classes/add/', views.ZwaveCommandClassEditView.as_view(), name='zwavecommandclass_add'),
    path('command-classes/<int:pk>/', views.ZwaveCommandClassView.as_view(), name='zwavecommandclass'),
    path('command-classes/<int:pk>/edit/', views.ZwaveCommandClassEditView.as_view(), name='zwavecommandclass_edit'),
    path('command-classes/<int:pk>/delete/', views.ZwaveCommandClassDeleteView.as_view(), name='zwavecommandclass_delete'),
    
    # Associations
    path('associations/', views.ZwaveAssociationListView.as_view(), name='zwaveassociation_list'),
    path('associations/add/', views.ZwaveAssociationEditView.as_view(), name='zwaveassociation_add'),
    path('associations/<int:pk>/', views.ZwaveAssociationView.as_view(), name='zwaveassociation'),
    path('associations/<int:pk>/edit/', views.ZwaveAssociationEditView.as_view(), name='zwaveassociation_edit'),
    path('associations/<int:pk>/delete/', views.ZwaveAssociationDeleteView.as_view(), name='zwaveassociation_delete'),
]
