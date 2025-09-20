from rest_framework import viewsets
from netbox.api.viewsets import NetBoxModelViewSet
from ..models import ZwaveNetwork, ZwaveDevice, ZwaveCommandClass, ZwaveAssociation
from .serializers import (
    ZwaveNetworkSerializer,
    ZwaveDeviceSerializer,
    ZwaveCommandClassSerializer,
    ZwaveAssociationSerializer
)


class ZwaveNetworkViewSet(NetBoxModelViewSet):
    """ViewSet for Z-Wave Network model"""
    queryset = ZwaveNetwork.objects.all()
    serializer_class = ZwaveNetworkSerializer
    filterset_fields = ['name', 'network_id', 'home_id', 'status', 'security_enabled', 's2_enabled']
    search_fields = ['name', 'description', 'home_id']


class ZwaveDeviceViewSet(NetBoxModelViewSet):
    """ViewSet for Z-Wave Device model"""
    queryset = ZwaveDevice.objects.select_related('network').all()
    serializer_class = ZwaveDeviceSerializer
    filterset_fields = [
        'network', 'name', 'node_id', 'device_type', 'status',
        'manufacturer_id', 'product_type', 'product_id', 'is_secure',
        'is_frequent_listener', 'is_beaming', 'is_routing'
    ]
    search_fields = ['name', 'description', 'manufacturer_id', 'product_type', 'product_id']


class ZwaveCommandClassViewSet(NetBoxModelViewSet):
    """ViewSet for Z-Wave Command Class model"""
    queryset = ZwaveCommandClass.objects.select_related('device').all()
    serializer_class = ZwaveCommandClassSerializer
    filterset_fields = [
        'device', 'command_class_id', 'name', 'version',
        'is_secure', 'is_controlled', 'is_supported'
    ]
    search_fields = ['name']


class ZwaveAssociationViewSet(NetBoxModelViewSet):
    """ViewSet for Z-Wave Association model"""
    queryset = ZwaveAssociation.objects.select_related('source_device', 'target_device').all()
    serializer_class = ZwaveAssociationSerializer
    filterset_fields = [
        'source_device', 'target_device', 'group_id'
    ]
    search_fields = ['description']
