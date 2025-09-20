from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField
from .models import ZwaveNetwork, ZwaveDevice, ZwaveCommandClass, ZwaveAssociation


class ZwaveNetworkForm(NetBoxModelForm):
    """Form for Z-Wave Network"""
    
    class Meta:
        model = ZwaveNetwork
        fields = [
            'name', 'network_id', 'home_id', 'status', 'description',
            'controller_node_id', 'security_enabled', 's2_enabled', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ZwaveNetworkFilterForm(NetBoxModelFilterSetForm):
    """Filter form for Z-Wave Network"""
    model = ZwaveNetwork
    fields = ['id', 'name', 'network_id', 'home_id', 'status', 'security_enabled', 's2_enabled']


class ZwaveDeviceForm(NetBoxModelForm):
    """Form for Z-Wave Device"""
    network = DynamicModelChoiceField(
        queryset=ZwaveNetwork.objects.all(),
        required=True,
        help_text="Z-Wave network this device belongs to"
    )
    
    class Meta:
        model = ZwaveDevice
        fields = [
            'network', 'name', 'node_id', 'device_type', 'status',
            'manufacturer_id', 'product_type', 'product_id', 'firmware_version',
            'hardware_version', 'library_type', 'protocol_version', 'application_version',
            'is_secure', 'is_frequent_listener', 'is_beaming', 'is_routing',
            'max_baud_rate', 'last_seen', 'battery_level', 'signal_strength',
            'description', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'last_seen': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class ZwaveDeviceFilterForm(NetBoxModelFilterSetForm):
    """Filter form for Z-Wave Device"""
    model = ZwaveDevice
    fields = [
        'id', 'network', 'name', 'node_id', 'device_type', 'status',
        'manufacturer_id', 'product_type', 'product_id', 'is_secure',
        'is_frequent_listener', 'is_beaming', 'is_routing'
    ]


class ZwaveCommandClassForm(NetBoxModelForm):
    """Form for Z-Wave Command Class"""
    device = DynamicModelChoiceField(
        queryset=ZwaveDevice.objects.all(),
        required=True,
        help_text="Device this command class belongs to"
    )
    
    class Meta:
        model = ZwaveCommandClass
        fields = [
            'device', 'command_class_id', 'name', 'version',
            'is_secure', 'is_controlled', 'is_supported', 'tags'
        ]


class ZwaveCommandClassFilterForm(NetBoxModelFilterSetForm):
    """Filter form for Z-Wave Command Class"""
    model = ZwaveCommandClass
    fields = [
        'id', 'device', 'command_class_id', 'name', 'version',
        'is_secure', 'is_controlled', 'is_supported'
    ]


class ZwaveAssociationForm(NetBoxModelForm):
    """Form for Z-Wave Association"""
    source_device = DynamicModelChoiceField(
        queryset=ZwaveDevice.objects.all(),
        required=True,
        help_text="Source device"
    )
    target_device = DynamicModelChoiceField(
        queryset=ZwaveDevice.objects.all(),
        required=True,
        help_text="Target device"
    )
    
    class Meta:
        model = ZwaveAssociation
        fields = [
            'source_device', 'target_device', 'group_id', 'description', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ZwaveAssociationFilterForm(NetBoxModelFilterSetForm):
    """Filter form for Z-Wave Association"""
    model = ZwaveAssociation
    fields = ['id', 'source_device', 'target_device', 'group_id']
