#!/usr/bin/env python3

import click
import configparser
import logging
import os
import subprocess
import uuid
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")

def_config = "/etc/waggle/config.ini"
nodeid_file = "/etc/waggle/node-id"
software_version = "{{VERSION}}"

def netintf_mac(interface):
    """Return the network interfaces MAC address; else None

    Arguments:
        interface (str): the interface name to retreive the MAC address from

    Returns:
        str: network interface MAC address; None on error
    """
    result = None
    intpath = Path(f"/sys/class/net/{interface}/address")
    if interface and intpath.exists():
        result = intpath.read_text().strip()

    logging.info(f"Network interface [{interface}] MAC address: [{result}]")
    return result


def generate_node_id(interface=None):
    """Generate the Node ID from the network interface MAC addresss.

    If using the network interface path is not possible, attempt the interface
    for the default route, and as a last resort use a UUID generated value.

    Arguments:
        interface (str): the interface name to retreive the MAC address from

    Returns:
        none
    """
    logging.info(f"Generate the Node ID [net interface: {interface}]")

    # build a network interface list to try
    ## provided option
    intf_options = [interface]
    ## default ip route interface
    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"], stdout=subprocess.PIPE
        )
        intf_options += [result.stdout.decode("utf-8").split(" ")[4]]
    except Exception as e:
        logging.warning(
            f"Unable to include 'ip route default' as candidate network interface. Error: {str(e)}"
        )
        pass
    logging.info(f"Candidate network interfaces: {intf_options}")

    # test the network interface array
    for netint in intf_options:
        logging.info(f"Attempting network interface [{netint}]")
        mac = netintf_mac(netint)
        if mac:
            nodeid = mac.replace(":", "").rjust(16, "0")
            logging.info(
                f"Generated Node ID [{nodeid}] from network interface [{netint}]"
            )
            return nodeid

    # network interfaces did not yeild a good result, generate the node ID
    #  prepend with 'F' to indicate generated value
    nodeid = ("%012X" % uuid.getnode()).rjust(16, "F")
    logging.warning(f"Generated Node ID [{nodeid}] from UUID library")
    return nodeid


@click.command()
@click.version_option(version=software_version, message=f"version: %(version)s")
@click.option(
    "-c", "--config", "config_file", default=def_config, help="config file to use"
)
@click.option("--version", is_flag=True)
def main(config_file, version):

    logging.info(f"Waggle Node ID Start [config: {config_file}]")

    netint = None
    node_id_override = None

    if Path(config_file).exists():
        logging.info(f"Reading {config_file}...")
        config = configparser.ConfigParser()
        config.read(config_file)

        if "system" in config:
            node_id_override = config["system"].get("node-id-override")

        if "hardware" in config:
            netint = config["hardware"].get("wlan-interface")
    else:
        logging.info(f"File {config_file} not found.")

    if node_id_override:
        logging.info(
            f"Use override node-id [{node_id_override}] from config file [{config_file}]"
        )
        nodeid = node_id_override
    else:
        nodeid = generate_node_id(netint)

    logging.info(f"Saving Node ID [{nodeid}] to file [{nodeid_file}]")
    Path(os.path.dirname(nodeid_file)).mkdir(parents=True, exist_ok=True)
    with open(nodeid_file, "w") as nf:
        nf.write(nodeid.upper())


if __name__ == "__main__":
    main()  # pragma: no cover
