from time import sleep

import winrt.windows.devices.wifidirect as wifi

p = wifi.WiFiDirectAdvertisementPublisher()
advertisement = p.advertisement
print("Publisher: ", p)


# Pass a function
def on_status_change(sender, args):
    print("Status changed: ", sender, args)

    match args.error:
        case wifi.WiFiDirectError.SUCCESS:
            print("\tSuccess")
        case wifi.WiFiDirectError.RADIO_NOT_AVAILABLE:
            print("\tRadio is not available")
        case wifi.WiFiDirectError.RESOURCE_IN_USE:
            print("\tResource in use")

    match args.status:
        case wifi.WiFiDirectAdvertisementPublisherStatus.CREATED:
            print("\tCreated")
        case wifi.WiFiDirectAdvertisementPublisherStatus.STARTED:
            # Begin listening for connections and notify listener that the advertisement started
            print("\tStarted")
        case wifi.WiFiDirectAdvertisementPublisherStatus.STOPPED:
            # Notify listener that the advertisement is stopped
            print("\tStopped")
        case wifi.WiFiDirectAdvertisementPublisherStatus.ABORTED:
            # Check error and notify listener that the advertisement stopped
            print("\tAborted")


token = p.add_status_changed(on_status_change)

# Must set the autonomous group owner (GO) enabled flag
# Legacy Wi-Fi Direct advertisement uses a Wi-Fi Direct GO to act as an access point to legacy settings
advertisement.is_autonomous_group_owner_enabled = True
legacy_settings = advertisement.legacy_settings
legacy_settings.is_enabled = True
legacy_settings.ssid = "DIRECT-MYTEST"
legacy_settings.passphrase.password = "test1234"
print("SSID: ", legacy_settings.ssid)
print("Passphrase: ", legacy_settings.passphrase.password)
# TODO: to edit password we need: pip install winrt-Windows.Security.Credentials

def on_connection_change(sender, args):
    print("Connection change: ", sender, args)

listener = wifi.WiFiDirectConnectionListener()
token_connection = listener.add_connection_requested(on_connection_change)

p.start()
sleep(30)
p.stop()
p.remove_status_changed(token)
listener.remove_connection_requested(token_connection)
sleep(3)
