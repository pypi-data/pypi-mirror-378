from netbox.plugins import PluginConfig


class NetBoxZwaveConfig(PluginConfig):
    name = 'netbox_zwave'
    verbose_name = 'NetBox Z-Wave'
    description = 'A NetBox plugin for tracking Z-Wave devices and networks'
    version = '0.1.0'
    author = 'Richard Dawson'
    author_email = 'dawsora@gmail.com'
    base_url = 'zwave'
    required_settings = []
    default_settings = {
        'enable_auto_discovery': False,
        'default_network_id': 1,
        'device_timeout': 30,
    }
    django_apps = []
    min_version = '4.0'
    max_version = '4.99'


config = NetBoxZwaveConfig
