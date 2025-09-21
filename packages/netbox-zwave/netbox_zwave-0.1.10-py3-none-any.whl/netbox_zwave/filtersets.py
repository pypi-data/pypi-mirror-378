from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from .models import ZwaveNetwork, ZwaveDevice, ZwaveCommandClass, ZwaveAssociation


class ZwaveNetworkFilterSet(NetBoxModelFilterSet):
    """Filter set for Z-Wave Network"""
    
    class Meta:
        model = ZwaveNetwork
        fields = ['id', 'name', 'network_id', 'home_id', 'status', 'security_enabled', 's2_enabled']

    def search(self, queryset, name, value):
        """Search across multiple fields"""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(home_id__icontains=value)
        )


class ZwaveDeviceFilterSet(NetBoxModelFilterSet):
    """Filter set for Z-Wave Device"""
    
    class Meta:
        model = ZwaveDevice
        fields = [
            'id', 'network', 'name', 'node_id', 'device_type', 'status',
            'manufacturer_id', 'product_type', 'product_id', 'is_secure',
            'is_frequent_listener', 'is_beaming', 'is_routing'
        ]

    def search(self, queryset, name, value):
        """Search across multiple fields"""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(manufacturer_id__icontains=value) |
            Q(product_type__icontains=value) |
            Q(product_id__icontains=value)
        )


class ZwaveCommandClassFilterSet(NetBoxModelFilterSet):
    """Filter set for Z-Wave Command Class"""
    
    class Meta:
        model = ZwaveCommandClass
        fields = [
            'id', 'device', 'command_class_id', 'name', 'version',
            'is_secure', 'is_controlled', 'is_supported'
        ]

    def search(self, queryset, name, value):
        """Search across multiple fields"""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        )


class ZwaveAssociationFilterSet(NetBoxModelFilterSet):
    """Filter set for Z-Wave Association"""
    
    class Meta:
        model = ZwaveAssociation
        fields = ['id', 'source_device', 'target_device', 'group_id']

    def search(self, queryset, name, value):
        """Search across multiple fields"""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(description__icontains=value)
        )
