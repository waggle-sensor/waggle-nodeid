#!/usr/bin/env python3

import click
import configparser
import logging
import logging.handlers
import os
import subprocess
import uuid
from pathlib import Path

logger = logging.getLogger("waggle-nodeid")
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address="/dev/log")
handler.setFormatter(logging.Formatter("waggle-nodeid: %(message)s"))
logger.addHandler(handler)

def_config = "/etc/sage/config.ini"
nodeid_file = "/etc/waggle/node-id"


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

    logger.info(f"Network interface [{interface}] MAC address: [{result}]")
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
    logger.info(f"Generate the Node ID [net interface: {interface}]")

    # build a network interface list to try
    ## provided option
    intf_options = [interface]
    ## default route interface
    result = subprocess.run(["ip", "route", "show", "default"], stdout=subprocess.PIPE)
    intf_options += [result.stdout.decode("utf-8").split(" ")[4]]
    logger.info(f"Candidate network interfaces: {intf_options}")

    # test the network interface array
    for netint in intf_options:
        logger.info(f"Attempting network interface [{netint}]")
        mac = netintf_mac(netint)
        if mac:
            nodeid = mac.replace(":", "").rjust(16, "0")
            logger.info(
                f"Generated Node ID [{nodeid}] from network interface [{netint}]"
            )
            return nodeid

    # network interfaces did not yeild a good result, generate the node ID
    #  prepend with 'F' to indicate generated value
    nodeid = ("%012X" % uuid.getnode()).rjust(16, "F")
    logger.warning(f"Generated Node ID [{nodeid}] from UUID library")
    return nodeid


@click.command()
@click.option(
    "-c", "--config", "config_file", default=def_config, help="config file to use"
)
def main(config_file):

    logger.info(f"Waggle Node ID Start [config: {config_file}]")

    netint = None
    node_id_override = None

    config = configparser.ConfigParser()
    config.read(config_file)

    if "system" in config:
        node_id_override = config["system"].get("node-id-override")

    if "hardware" in config:
        netint = config["hardware"].get("wlan-interface")

    if node_id_override:
        logger.info(
            f"Use override node-id [{node_id_override}] from config file [{config_file}]"
        )
        nodeid = node_id_override
    else:
        nodeid = generate_node_id(netint)

    logger.info(f"Saving Node ID [{nodeid}] to file [{nodeid_file}]")
    Path(os.path.dirname(nodeid_file)).mkdir(parents=True, exist_ok=True)
    with open(nodeid_file, "w") as nf:
        nf.write(nodeid.upper())


if __name__ == "__main__":
    main()  # pragma: no cover
