from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import ZwaveNetwork, ZwaveDevice, ZwaveCommandClass, ZwaveAssociation


class ZwaveNetworkSerializer(NetBoxModelSerializer):
    """Serializer for Z-Wave Network model"""
    device_count = serializers.IntegerField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_zwave-api:zwavenetwork-detail'
    )

    class Meta:
        model = ZwaveNetwork
        fields = [
            'id', 'url', 'display', 'name', 'network_id', 'home_id', 'status',
            'description', 'controller_node_id', 'security_enabled', 's2_enabled',
            'device_count', 'created', 'last_updated', 'tags', 'custom_fields'
        ]


class ZwaveDeviceSerializer(NetBoxModelSerializer):
    """Serializer for Z-Wave Device model"""
    network_name = serializers.CharField(source='network.name', read_only=True)
    network_id = serializers.IntegerField(source='network.network_id', read_only=True)
    command_class_count = serializers.IntegerField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_zwave-api:zwavedevice-detail'
    )

    class Meta:
        model = ZwaveDevice
        fields = [
            'id', 'url', 'display', 'network', 'network_name', 'network_id',
            'name', 'node_id', 'device_type', 'status', 'manufacturer_id',
            'product_type', 'product_id', 'firmware_version', 'hardware_version',
            'library_type', 'protocol_version', 'application_version',
            'is_secure', 'is_frequent_listener', 'is_beaming', 'is_routing',
            'max_baud_rate', 'last_seen', 'battery_level', 'signal_strength',
            'description', 'command_class_count', 'created', 'last_updated',
            'tags', 'custom_fields'
        ]


class ZwaveCommandClassSerializer(NetBoxModelSerializer):
    """Serializer for Z-Wave Command Class model"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    device_node_id = serializers.IntegerField(source='device.node_id', read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_zwave-api:zwavecommandclass-detail'
    )

    class Meta:
        model = ZwaveCommandClass
        fields = [
            'id', 'url', 'display', 'device', 'device_name', 'device_node_id',
            'command_class_id', 'name', 'version', 'is_secure', 'is_controlled',
            'is_supported', 'created', 'last_updated', 'tags', 'custom_fields'
        ]


class ZwaveAssociationSerializer(NetBoxModelSerializer):
    """Serializer for Z-Wave Association model"""
    source_device_name = serializers.CharField(source='source_device.name', read_only=True)
    source_device_node_id = serializers.IntegerField(source='source_device.node_id', read_only=True)
    target_device_name = serializers.CharField(source='target_device.name', read_only=True)
    target_device_node_id = serializers.IntegerField(source='target_device.node_id', read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_zwave-api:zwaveassociation-detail'
    )

    class Meta:
        model = ZwaveAssociation
        fields = [
            'id', 'url', 'display', 'source_device', 'source_device_name',
            'source_device_node_id', 'target_device', 'target_device_name',
            'target_device_node_id', 'group_id', 'description', 'created',
            'last_updated', 'tags', 'custom_fields'
        ]
