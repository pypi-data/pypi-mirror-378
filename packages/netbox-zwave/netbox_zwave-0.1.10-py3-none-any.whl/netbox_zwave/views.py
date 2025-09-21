from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from netbox.views import generic
from netbox.views.generic import ObjectListView, ObjectView, ObjectEditView, ObjectDeleteView
from . import filtersets, forms, models, tables


class ZwaveNetworkListView(ObjectListView):
    """List view for Z-Wave Networks"""
    queryset = models.ZwaveNetwork.objects.all()
    table = tables.ZwaveNetworkTable
    filterset = filtersets.ZwaveNetworkFilterSet
    filterset_form = forms.ZwaveNetworkFilterForm
    template_name = 'netbox_zwave/zwavenetwork_list.html'


class ZwaveNetworkView(ObjectView):
    """Detail view for Z-Wave Network"""
    queryset = models.ZwaveNetwork.objects.all()
    template_name = 'netbox_zwave/zwavenetwork.html'

    def get_extra_context(self, request, instance):
        return {
            'devices_table': tables.ZwaveDeviceTable(instance.devices.all()),
        }


class ZwaveNetworkEditView(ObjectEditView):
    """Create/Edit view for Z-Wave Network"""
    queryset = models.ZwaveNetwork.objects.all()
    form = forms.ZwaveNetworkForm
    template_name = 'netbox_zwave/zwavenetwork_edit.html'


class ZwaveNetworkDeleteView(ObjectDeleteView):
    """Delete view for Z-Wave Network"""
    queryset = models.ZwaveNetwork.objects.all()
    template_name = 'netbox_zwave/zwavenetwork_delete.html'


class ZwaveDeviceListView(ObjectListView):
    """List view for Z-Wave Devices"""
    queryset = models.ZwaveDevice.objects.select_related('network').all()
    table = tables.ZwaveDeviceTable
    filterset = filtersets.ZwaveDeviceFilterSet
    filterset_form = forms.ZwaveDeviceFilterForm
    template_name = 'netbox_zwave/zwavedevice_list.html'


class ZwaveDeviceView(ObjectView):
    """Detail view for Z-Wave Device"""
    queryset = models.ZwaveDevice.objects.select_related('network').all()
    template_name = 'netbox_zwave/zwavedevice.html'

    def get_extra_context(self, request, instance):
        return {
            'command_classes_table': tables.ZwaveCommandClassTable(instance.command_classes.all()),
            'source_associations_table': tables.ZwaveAssociationTable(instance.source_associations.all()),
            'target_associations_table': tables.ZwaveAssociationTable(instance.target_associations.all()),
        }


class ZwaveDeviceEditView(ObjectEditView):
    """Create/Edit view for Z-Wave Device"""
    queryset = models.ZwaveDevice.objects.all()
    form = forms.ZwaveDeviceForm
    template_name = 'netbox_zwave/zwavedevice_edit.html'


class ZwaveDeviceDeleteView(ObjectDeleteView):
    """Delete view for Z-Wave Device"""
    queryset = models.ZwaveDevice.objects.all()
    template_name = 'netbox_zwave/zwavedevice_delete.html'


class ZwaveCommandClassListView(ObjectListView):
    """List view for Z-Wave Command Classes"""
    queryset = models.ZwaveCommandClass.objects.select_related('device').all()
    table = tables.ZwaveCommandClassTable
    filterset = filtersets.ZwaveCommandClassFilterSet
    filterset_form = forms.ZwaveCommandClassFilterForm
    template_name = 'netbox_zwave/zwavecommandclass_list.html'


class ZwaveCommandClassView(ObjectView):
    """Detail view for Z-Wave Command Class"""
    queryset = models.ZwaveCommandClass.objects.select_related('device').all()
    template_name = 'netbox_zwave/zwavecommandclass.html'


class ZwaveCommandClassEditView(ObjectEditView):
    """Create/Edit view for Z-Wave Command Class"""
    queryset = models.ZwaveCommandClass.objects.all()
    form = forms.ZwaveCommandClassForm
    template_name = 'netbox_zwave/zwavecommandclass_edit.html'


class ZwaveCommandClassDeleteView(ObjectDeleteView):
    """Delete view for Z-Wave Command Class"""
    queryset = models.ZwaveCommandClass.objects.all()
    template_name = 'netbox_zwave/zwavecommandclass_delete.html'


class ZwaveAssociationListView(ObjectListView):
    """List view for Z-Wave Associations"""
    queryset = models.ZwaveAssociation.objects.select_related('source_device', 'target_device').all()
    table = tables.ZwaveAssociationTable
    filterset = filtersets.ZwaveAssociationFilterSet
    filterset_form = forms.ZwaveAssociationFilterForm
    template_name = 'netbox_zwave/zwaveassociation_list.html'


class ZwaveAssociationView(ObjectView):
    """Detail view for Z-Wave Association"""
    queryset = models.ZwaveAssociation.objects.select_related('source_device', 'target_device').all()
    template_name = 'netbox_zwave/zwaveassociation.html'


class ZwaveAssociationEditView(ObjectEditView):
    """Create/Edit view for Z-Wave Association"""
    queryset = models.ZwaveAssociation.objects.all()
    form = forms.ZwaveAssociationForm
    template_name = 'netbox_zwave/zwaveassociation_edit.html'


class ZwaveAssociationDeleteView(ObjectDeleteView):
    """Delete view for Z-Wave Association"""
    queryset = models.ZwaveAssociation.objects.all()
    template_name = 'netbox_zwave/zwaveassociation_delete.html'
