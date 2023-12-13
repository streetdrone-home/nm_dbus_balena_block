#!/usr/bin/env python

import logging
import os
from pathlib import Path
import socket
from typing import Optional

import gi
import yaml

gi.require_version("NM", "1.0")
from gi.repository import GLib, NM


def main():
    logging.basicConfig(level=logging.INFO)

    client = NM.Client.new(None)
    logging.info(f"NM client version: {client.get_version()}")

    log_devices(client)

    main_loop = GLib.MainLoop()

    connection_ids = get_existing_connection_ids(client)

    config = load_configuration()
    logging.info("Got configuration:")
    logging.info(config)

    for connection in config:
        if connection["name"] in connection_ids:
            logging.warn(f"Connection {connection['name']} already exists; skipping")
            continue

        add_and_activate_connection(
            client,
            main_loop,
            connection["name"],
            connection["iface"],
            connection["method"],
            connection.get("ipv4"),
        )


def log_devices(client):
    # Get all devices
    devices = client.get_devices()
    logging.info("=== Network devices:")
    for device in devices:
        logging.info(f"  - name:  {device.get_iface()}")
        logging.info(f"    type:  {device.get_type_description()}")
        logging.info(f"    state: {device.get_state().value_nick}")
        if device.get_state().value_nick == "activated":
            logging.info(f"    conn:  {device.get_applied_connection(0)[0].get_id()}")


def get_existing_connection_ids(client):
    # get all connections
    connections = client.get_connections()

    # print the connections' details
    logging.info("=== Existing connections:")
    for c in connections:
        logging.info(f"  - {c.get_id()}  ---  {c.get_path()}")

    return [c.get_id() for c in connections]


def load_configuration():
    config_yaml = os.environ.get("NM_DBUS_CONFIG")

    if not config_yaml:
        logging.info(
            "Configuration not found in environment variable 'NM_DBUS_CONFIG'. Will try to load /nm-dbus.yaml instead."
        )
        config_path = Path("/nm-dbus.yaml")
        if not config_path.is_file():
            raise RuntimeError(
                "File '/nm-dbus.yaml' not found; could not load any configuration!"
            )

        config_yaml = config_path.read_text()

    try:
        return yaml.safe_load(config_yaml)
    except yaml.parser.ParseError as e:
        logging.exception(f"Failed parsing YAML:{config_yaml}\n")
        raise


def add_and_activate_connection(client, glib_loop, name, iface, method, ipv4=None):
    connection = create_connection(name, iface, method, ipv4)
    device = client.get_device_by_iface(iface)
    if not device:
        logging.error(f"Could not get device by iface: {iface}")
        return

    client.add_and_activate_connection_async(
        connection, device, None, None, add_and_activate_cb, glib_loop
    )

    glib_loop.run()


def create_connection(name: str, iface: str, method: str, ipv4: Optional[str] = None):
    connection = NM.SimpleConnection.new()
    s_con = NM.SettingConnection.new()
    s_con.set_property(NM.SETTING_CONNECTION_ID, name)
    s_con.set_property(NM.SETTING_CONNECTION_TYPE, "802-3-ethernet")
    s_con.set_property(NM.SETTING_CONNECTION_INTERFACE_NAME, iface)

    s_ip4 = NM.SettingIP4Config.new()
    s_ip4.set_property(NM.SETTING_IP_CONFIG_METHOD, method)
    if ipv4 is not None:
        s_ip4.add_address(NM.IPAddress.new(socket.AF_INET, ipv4, 24))

    s_ip6 = NM.SettingIP6Config.new()
    s_ip6.set_property(NM.SETTING_IP_CONFIG_METHOD, "ignore")

    connection.add_setting(s_con)
    connection.add_setting(s_ip4)
    connection.add_setting(s_ip6)

    return connection


def add_and_activate_cb(client, result, glib_loop):
    try:
        ac = client.add_and_activate_connection_finish(result)
        logging.info(f"ActiveConnection ac.get_path()")
        logging.info("State {ac.get_state().value_nick}")
    except Exception as e:
        logging.exception("Failed activating connection")
    glib_loop.quit()


if __name__ == "__main__":
    main()
