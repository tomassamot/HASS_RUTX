# HASS_RUTX (mint)
Home Assistant integration for communicating with a C program and processing, displaying and sending MQTT messages.
## Installation
Follow the steps below to install the integration.  
  
1. Create a "custom_components" folder in the Home Assistant "config" directory  
2. Download and store this integration in the "custom_components" folder  
3. Launch Home Assistant  
4. Go to Settings->Devices & Services  
5. Click "Add integration"  
6. Search for "Mint" and click on it
7. Fill out required information  
## Dashboard setup
Follow the steps below to setup the dashboard with the main states created by the integration.  
  
1. Go to Overview  
2. Click the three dots in the upper right corner  
3. Press "Edit Dashboard"  
4. Again click the three dots in the upper right corner  
5. Press "Raw configuration editor"  
6. Append the "cards" YAML object with the text below:  
```yaml
- type: entities
entities:
  - entity: mint.radio1_up
  - entity: mint.radio1_channel
    icon: ''
  - entity: mint.radio1_hwmode
  - entity: mint.radio1_htmode
  - entity: mint.radio1_wlan1_conn_devices
    icon: ''
  - entity: mint.radio1_wlan1_ifconfig_ssid
  - entity: mint.radio1_wlan1_ifconfig_wifi_id
title: WiFi 802.11a
- type: entities
entities:
  - entity: mint.radio0_up
  - entity: mint.radio0_channel
  - entity: mint.radio0_hwmode
  - entity: mint.radio0_htmode
  - entity: mint.radio0_wlan0_conn_devices
  - entity: mint.radio0_wlan0_ifconfig_ssid
  - entity: mint.radio0_wlan0_ifconfig_wifi_id
title: WiFi 802.11g
- type: entities
entities:
  - entity: mint.device_name
  - entity: mint.total_ram
  - entity: mint.free_ram
  - entity: mint.available_ram
title: Memory
- type: entities
entities:
  - entity: mint.ip
  - entity: sensor.new_ip
    secondary_info: entity-id
  - entity: button.change_ip_address
title: IP
- type: entities
entities:
  - entity: mint.radio0_wlan0_banned_devices
  - entity: mint.radio1_wlan1_banned_devices
  - entity: sensor.device_to_ban
    secondary_info: entity-id
  - entity: sensor.ban_duration
    secondary_info: entity-id
  - entity: sensor.interface_name
    secondary_info: entity-id
  - entity: button.ban_given_device
title: Banning
- type: entities
entities:
  - entity: mint.lan_1_state
  - entity: mint.lan_1_speed
  - entity: mint.lan_2_state
  - entity: mint.lan_2_speed
  - entity: mint.lan_3_state
  - entity: mint.lan_3_speed
title: LAN ports
- type: entities
entities:
  - mint.lease_hostnames
  - mint.lease_ipaddrs
  - mint.lease_macs
title: DHCP Leases
```
