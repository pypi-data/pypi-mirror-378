import sdbus
from uuid import uuid4
from sdbus_block.networkmanager import NetworkManagerSettings
from sdbus_block.networkmanager import NetworkManagerConnectionProperties


import pywifi

def connect_to_wifi_pywifi(ssid: str, auth_type: str, password: str):
    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.auth = pywifi.const.AUTH_ALG_OPEN
    if auth_type == "" or auth_type.lower == "none":
        profile.akm.append(pywifi.const.AKM_TYPE_NONE)
    if auth_type == "WPA":
        profile.akm.append(pywifi.const.AKM_TYPE_WPA)
    if auth_type == "WPAPSK":
        profile.akm.append(pywifi.const.AKM_TYPE_WPAPSK)
    if auth_type == "WPA2":
        profile.akm.append(pywifi.const.AKM_TYPE_WPA2)
    if auth_type == "WPA2PSK":
        profile.akm.append(pywifi.const.AKM_TYPE_WPA2PSK)
    # profile.cipher = pywifi.const.CIPHER_TYPE_CCMP
    profile.key = password
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    profile = iface.add_network_profile(profile)
    iface.connect(profile)

def connect_to_wifi_dbus(ssid: str, auth_type: str, password: str):
    match auth_type:
        case "WPA":
            auth_type = "wpa"
        case "WPAPSK":
            auth_type="wpa-psk"
        case "WPA2":
            auth_type = "wpa2"
        case "WPA2PSK":
            auth_type="wpa2-psk"
    sdbus.set_default_bus(sdbus.sd_bus_open_system())
    if connection_dpath := add_wifi_psk_connection(
    conn_id=ssid,
    uuid=uuid4(),
    ssid=ssid,
    psk=password,
    interface_name="",
    auto=True,
    save=True,
        
    ):
        print(f"Path of the new connection: {connection_dpath}")
    else:
        print("Error: No new connection created.")





def add_wifi_psk_connection(
    
    conn_id:str,
    uuid:str,
    ssid:str,
    psk:str,
    interface_name:str,
    auto:bool,
    save:bool,
 ) -> str:
    """Add a temporary (not yet saved) network connection profile
    :param Namespace args: autoconnect, conn_id, psk, save, ssid, uuid
    :return: dbus connection path of the created connection profile
    """

    # If we add many connections passing the same id, things get messy. Check:
    if NetworkManagerSettings().get_connections_by_id(conn_id):
        print(f'Connection "{conn_id}" exists, remove it first')
        print(f'Run: nmcli connection delete "{conn_id}"')
        return ""

    properties: NetworkManagerConnectionProperties = {
        "connection": {
            "id": ("s", conn_id),
            "uuid": ("s", str(uuid)),
            "type": ("s", "802-11-wireless"),
            "autoconnect": ("b", auto),
        },
        "802-11-wireless": {
            "mode": ("s", "infrastructure"),
            "security": ("s", "802-11-wireless-security"),
            "ssid": ("ay", ssid.encode("utf-8")),
        },
        "802-11-wireless-security": {
            "key-mgmt": ("s", "wpa-psk"),
            "auth-alg": ("s", "open"),
            "psk": ("s", psk),
        },
        "ipv4": {"method": ("s", "auto")},
        "ipv6": {"method": ("s", "auto")},
    }

    # To bind the new connection to a specific interface, use this:
    if  interface_name:
        properties["connection"]["interface-name"] = ("s", interface_name)

    s = NetworkManagerSettings()
    save = bool(save)
    addconnection = s.add_connection if save else s.add_connection_unsaved
    connection_settings_dbus_path = addconnection(properties)
    created = "created and saved" if save else "created"
    return connection_settings_dbus_path

