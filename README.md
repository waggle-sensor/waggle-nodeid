# Waggle Node ID Service

An early boot service that generates a unique Node ID and stores the value in
the node file (`/etc/waggle/node-id`). The unique ID is generated using the
MAC address of the main network interface, falling back on a randomly generated
UUID if the network interface can't be found. The service only runs if the
`/etc/waggle/node-id` file does **not** exist.

## Build Instructions

Builds are created using the `./build.sh` script. For help execute `./build.sh -?`.

Build generates a Debian package that can be installed into a Debian OS via
the `dpkg -i` command.
