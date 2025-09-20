import django_tables2 as tables
from django_tables2.utils import Accessor
from netbox.tables import NetBoxTable, columns
from .models import ZwaveNetwork, ZwaveDevice, ZwaveCommandClass, ZwaveAssociation


class ZwaveNetworkTable(NetBoxTable):
    """Table for Z-Wave Networks"""
    name = tables.Column(
        linkify=True,
        verbose_name='Name'
    )
    network_id = tables.Column(
        verbose_name='Network ID'
    )
    home_id = tables.Column(
        verbose_name='Home ID'
    )
    status = columns.ChoiceFieldColumn(
        verbose_name='Status'
    )
    device_count = tables.Column(
        verbose_name='Devices',
        accessor=Accessor('devices.count'),
        orderable=False
    )
    security_enabled = columns.BooleanColumn(
        verbose_name='Security'
    )
    s2_enabled = columns.BooleanColumn(
        verbose_name='S2'
    )
    tags = columns.TagColumn(
        url_name='plugins:netbox_zwave:zwavenetwork_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ZwaveNetwork
        fields = (
            'pk', 'id', 'name', 'network_id', 'home_id', 'status',
            'device_count', 'security_enabled', 's2_enabled', 'created',
            'last_updated', 'tags'
        )
        default_columns = (
            'name', 'network_id', 'home_id', 'status', 'device_count',
            'security_enabled', 's2_enabled'
        )


class ZwaveDeviceTable(NetBoxTable):
    """Table for Z-Wave Devices"""
    name = tables.Column(
        linkify=True,
        verbose_name='Name'
    )
    network = tables.Column(
        linkify=True,
        verbose_name='Network'
    )
    node_id = tables.Column(
        verbose_name='Node ID'
    )
    device_type = columns.ChoiceFieldColumn(
        verbose_name='Type'
    )
    status = columns.ChoiceFieldColumn(
        verbose_name='Status'
    )
    manufacturer_id = tables.Column(
        verbose_name='Manufacturer ID'
    )
    product_type = tables.Column(
        verbose_name='Product Type'
    )
    product_id = tables.Column(
        verbose_name='Product ID'
    )
    firmware_version = tables.Column(
        verbose_name='Firmware'
    )
    is_secure = columns.BooleanColumn(
        verbose_name='Secure'
    )
    is_routing = columns.BooleanColumn(
        verbose_name='Routing'
    )
    battery_level = tables.Column(
        verbose_name='Battery %'
    )
    signal_strength = tables.Column(
        verbose_name='Signal (dBm)'
    )
    last_seen = columns.DateTimeColumn(
        verbose_name='Last Seen'
    )
    command_class_count = tables.Column(
        verbose_name='Command Classes',
        accessor=Accessor('command_classes.count'),
        orderable=False
    )
    tags = columns.TagColumn(
        url_name='plugins:netbox_zwave:zwavedevice_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ZwaveDevice
        fields = (
            'pk', 'id', 'name', 'network', 'node_id', 'device_type', 'status',
            'manufacturer_id', 'product_type', 'product_id', 'firmware_version',
            'is_secure', 'is_routing', 'battery_level', 'signal_strength',
            'last_seen', 'command_class_count', 'created', 'last_updated', 'tags'
        )
        default_columns = (
            'name', 'network', 'node_id', 'device_type', 'status',
            'manufacturer_id', 'firmware_version', 'is_secure', 'battery_level'
        )


class ZwaveCommandClassTable(NetBoxTable):
    """Table for Z-Wave Command Classes"""
    device = tables.Column(
        linkify=True,
        verbose_name='Device'
    )
    command_class_id = tables.Column(
        verbose_name='Command Class ID'
    )
    name = tables.Column(
        verbose_name='Name'
    )
    version = tables.Column(
        verbose_name='Version'
    )
    is_secure = columns.BooleanColumn(
        verbose_name='Secure'
    )
    is_controlled = columns.BooleanColumn(
        verbose_name='Controlled'
    )
    is_supported = columns.BooleanColumn(
        verbose_name='Supported'
    )
    tags = columns.TagColumn(
        url_name='plugins:netbox_zwave:zwavecommandclass_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ZwaveCommandClass
        fields = (
            'pk', 'id', 'device', 'command_class_id', 'name', 'version',
            'is_secure', 'is_controlled', 'is_supported', 'created',
            'last_updated', 'tags'
        )
        default_columns = (
            'device', 'command_class_id', 'name', 'version',
            'is_secure', 'is_controlled', 'is_supported'
        )


class ZwaveAssociationTable(NetBoxTable):
    """Table for Z-Wave Associations"""
    source_device = tables.Column(
        linkify=True,
        verbose_name='Source Device'
    )
    target_device = tables.Column(
        linkify=True,
        verbose_name='Target Device'
    )
    group_id = tables.Column(
        verbose_name='Group ID'
    )
    tags = columns.TagColumn(
        url_name='plugins:netbox_zwave:zwaveassociation_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ZwaveAssociation
        fields = (
            'pk', 'id', 'source_device', 'target_device', 'group_id',
            'description', 'created', 'last_updated', 'tags'
        )
        default_columns = (
            'source_device', 'target_device', 'group_id', 'description'
        )
