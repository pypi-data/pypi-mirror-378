from netbox.plugins import PluginMenu, PluginMenuItem, PluginMenuButton


menu_items = (
    PluginMenuItem(
        link='plugins:netbox_zwave:zwavenetwork_list',
        link_text='Networks',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_zwave:zwavenetwork_add',
                title='Add Network',
                icon_class='mdi mdi-plus-thick',
                color='green',
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_zwave:zwavedevice_list',
        link_text='Devices',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_zwave:zwavedevice_add',
                title='Add Device',
                icon_class='mdi mdi-plus-thick',
                color='green',
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_zwave:zwavecommandclass_list',
        link_text='Command Classes',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_zwave:zwavecommandclass_add',
                title='Add Command Class',
                icon_class='mdi mdi-plus-thick',
                color='green',
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_zwave:zwaveassociation_list',
        link_text='Associations',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_zwave:zwaveassociation_add',
                title='Add Association',
                icon_class='mdi mdi-plus-thick',
                color='green',
            ),
        ),
    ),
)
