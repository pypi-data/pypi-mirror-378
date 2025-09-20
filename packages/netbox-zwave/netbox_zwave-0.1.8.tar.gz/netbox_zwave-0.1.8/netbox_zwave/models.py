from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from netbox.models import NetBoxModel
from utilities.choices import ChoiceSet


class ZwaveNetworkStatusChoices(ChoiceSet):
    """Choices for Z-Wave network status"""
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    MAINTENANCE = 'maintenance', 'Maintenance'
    
    CHOICES = (
        ACTIVE,
        INACTIVE,
        MAINTENANCE,
    )


class ZwaveDeviceStatusChoices(ChoiceSet):
    """Choices for Z-Wave device status"""
    ONLINE = 'online', 'Online'
    OFFLINE = 'offline', 'Offline'
    UNKNOWN = 'unknown', 'Unknown'
    FAILED = 'failed', 'Failed'
    
    CHOICES = (
        ONLINE,
        OFFLINE,
        UNKNOWN,
        FAILED,
    )


class ZwaveDeviceTypeChoices(ChoiceSet):
    """Choices for Z-Wave device types"""
    CONTROLLER = 'controller', 'Controller'
    ROUTER = 'router', 'Router'
    END_DEVICE = 'end_device', 'End Device'
    SLEEPING_END_DEVICE = 'sleeping_end_device', 'Sleeping End Device'
    
    CHOICES = (
        CONTROLLER,
        ROUTER,
        END_DEVICE,
        SLEEPING_END_DEVICE,
    )


class ZwaveNetwork(NetBoxModel):
    """Z-Wave Network model"""
    name = models.CharField(
        max_length=100,
        help_text="Name of the Z-Wave network"
    )
    network_id = models.PositiveIntegerField(
        unique=True,
        validators=[MinValueValidator(1), MaxValueValidator(255)],
        help_text="Z-Wave Network ID (1-255)"
    )
    home_id = models.CharField(
        max_length=16,
        unique=True,
        help_text="Z-Wave Home ID (hexadecimal)"
    )
    status = models.CharField(
        max_length=20,
        choices=ZwaveNetworkStatusChoices,
        default=ZwaveNetworkStatusChoices.ACTIVE,
        help_text="Network status"
    )
    description = models.TextField(
        blank=True,
        help_text="Network description"
    )
    controller_node_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(232)],
        help_text="Controller node ID"
    )
    security_enabled = models.BooleanField(
        default=False,
        help_text="Whether security is enabled on this network"
    )
    s2_enabled = models.BooleanField(
        default=False,
        help_text="Whether S2 security is enabled"
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Z-Wave Network'
        verbose_name_plural = 'Z-Wave Networks'

    def __str__(self):
        return f"{self.name} (ID: {self.network_id})"

    def get_absolute_url(self):
        return reverse('plugins:netbox_zwave:zwavenetwork', kwargs={'pk': self.pk})


class ZwaveDevice(NetBoxModel):
    """Z-Wave Device model"""
    network = models.ForeignKey(
        to=ZwaveNetwork,
        on_delete=models.CASCADE,
        related_name='devices',
        help_text="Z-Wave network this device belongs to"
    )
    name = models.CharField(
        max_length=100,
        help_text="Device name"
    )
    node_id = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(232)],
        help_text="Z-Wave Node ID (1-232)"
    )
    device_type = models.CharField(
        max_length=30,
        choices=ZwaveDeviceTypeChoices,
        default=ZwaveDeviceTypeChoices.END_DEVICE,
        help_text="Device type"
    )
    status = models.CharField(
        max_length=20,
        choices=ZwaveDeviceStatusChoices,
        default=ZwaveDeviceStatusChoices.UNKNOWN,
        help_text="Device status"
    )
    manufacturer_id = models.CharField(
        max_length=8,
        blank=True,
        help_text="Manufacturer ID (hexadecimal)"
    )
    product_type = models.CharField(
        max_length=8,
        blank=True,
        help_text="Product Type (hexadecimal)"
    )
    product_id = models.CharField(
        max_length=8,
        blank=True,
        help_text="Product ID (hexadecimal)"
    )
    firmware_version = models.CharField(
        max_length=20,
        blank=True,
        help_text="Firmware version"
    )
    hardware_version = models.CharField(
        max_length=20,
        blank=True,
        help_text="Hardware version"
    )
    library_type = models.CharField(
        max_length=20,
        blank=True,
        help_text="Z-Wave library type"
    )
    protocol_version = models.CharField(
        max_length=10,
        blank=True,
        help_text="Z-Wave protocol version"
    )
    application_version = models.CharField(
        max_length=10,
        blank=True,
        help_text="Application version"
    )
    is_secure = models.BooleanField(
        default=False,
        help_text="Whether device supports security"
    )
    is_frequent_listener = models.BooleanField(
        default=False,
        help_text="Whether device is a frequent listener"
    )
    is_beaming = models.BooleanField(
        default=False,
        help_text="Whether device supports beaming"
    )
    is_routing = models.BooleanField(
        default=False,
        help_text="Whether device supports routing"
    )
    max_baud_rate = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum baud rate"
    )
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time device was seen"
    )
    battery_level = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Battery level percentage (0-100)"
    )
    signal_strength = models.IntegerField(
        null=True,
        blank=True,
        help_text="Signal strength in dBm"
    )
    description = models.TextField(
        blank=True,
        help_text="Device description"
    )

    class Meta:
        ordering = ['network', 'node_id']
        unique_together = ['network', 'node_id']
        verbose_name = 'Z-Wave Device'
        verbose_name_plural = 'Z-Wave Devices'

    def __str__(self):
        return f"{self.name} (Node {self.node_id})"

    def get_absolute_url(self):
        return reverse('plugins:netbox_zwave:zwavedevice', kwargs={'pk': self.pk})


class ZwaveCommandClass(NetBoxModel):
    """Z-Wave Command Class model"""
    device = models.ForeignKey(
        to=ZwaveDevice,
        on_delete=models.CASCADE,
        related_name='command_classes',
        help_text="Device this command class belongs to"
    )
    command_class_id = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(255)],
        help_text="Command Class ID (0-255)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Command class name"
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text="Command class version"
    )
    is_secure = models.BooleanField(
        default=False,
        help_text="Whether command class supports security"
    )
    is_controlled = models.BooleanField(
        default=False,
        help_text="Whether device can control this command class"
    )
    is_supported = models.BooleanField(
        default=True,
        help_text="Whether device supports this command class"
    )

    class Meta:
        ordering = ['device', 'command_class_id']
        unique_together = ['device', 'command_class_id']
        verbose_name = 'Z-Wave Command Class'
        verbose_name_plural = 'Z-Wave Command Classes'

    def __str__(self):
        return f"{self.name} (v{self.version})"

    def get_absolute_url(self):
        return reverse('plugins:netbox_zwave:zwavecommandclass', kwargs={'pk': self.pk})


class ZwaveAssociation(NetBoxModel):
    """Z-Wave Association model"""
    source_device = models.ForeignKey(
        to=ZwaveDevice,
        on_delete=models.CASCADE,
        related_name='source_associations',
        help_text="Source device"
    )
    target_device = models.ForeignKey(
        to=ZwaveDevice,
        on_delete=models.CASCADE,
        related_name='target_associations',
        help_text="Target device"
    )
    group_id = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(255)],
        help_text="Association group ID"
    )
    description = models.TextField(
        blank=True,
        help_text="Association description"
    )

    class Meta:
        ordering = ['source_device', 'group_id', 'target_device']
        unique_together = ['source_device', 'target_device', 'group_id']
        verbose_name = 'Z-Wave Association'
        verbose_name_plural = 'Z-Wave Associations'

    def __str__(self):
        return f"{self.source_device} -> {self.target_device} (Group {self.group_id})"

    def get_absolute_url(self):
        return reverse('plugins:netbox_zwave:zwaveassociation', kwargs={'pk': self.pk})
