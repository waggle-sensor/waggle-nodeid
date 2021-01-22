#!/usr/bin/env python3

import os
import pytest
from click.testing import CliRunner
from ROOTFS.usr.bin.waggle_nodeid import main
from pathlib import Path


def test_config_interface():
    runner = CliRunner()
    result = runner.invoke(main, ["-c", "/workdir/tests/config.ini"])
    assert result.exit_code == 0

    # assert the node-id file exists
    assert Path("/etc/waggle/node-id").exists()

    # assert it start with 0 and is 16 characters long
    with open("/etc/waggle/node-id", "r") as file:
        content = file.readline()
    assert len(content) == 16
    assert content[0] == "0"


def test_no_config_route_intf():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0

    # assert the log file exists
    assert Path("/var/log/waggle/waggle.log").exists()

    # assert the node-id file exists
    assert Path("/etc/waggle/node-id").exists()

    # assert it start with 0 and is 16 characters long
    with open("/etc/waggle/node-id", "r") as file:
        content = file.readline()
    assert len(content) == 16
    assert content[0] == "0"


def test_bad_config_route_intf():
    runner = CliRunner()
    result = runner.invoke(main, ["-c", "/workdir/tests/config_bad.ini"])
    assert result.exit_code == 0

    # assert the node-id file exists
    assert Path("/etc/waggle/node-id").exists()

    # assert it start with F and is 16 characters long
    with open("/etc/waggle/node-id", "r") as file:
        content = file.readline()
    assert len(content) == 16
    assert content[0] == "0"


def test_config_route_override():
    runner = CliRunner()
    result = runner.invoke(main, ["-c", "/workdir/tests/config_over.ini"])
    assert result.exit_code == 0

    # assert the node-id file exists
    assert Path("/etc/waggle/node-id").exists()

    # assert it start with F and is 16 characters long
    with open("/etc/waggle/node-id", "r") as file:
        content = file.readline()
    assert len(content) == 16
    assert content == "123456789ABCDEFG"


def test_no_config_no_route(mocker):
    mocker.patch("subprocess.run")

    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0

    # assert the node-id file exists
    assert Path("/etc/waggle/node-id").exists()

    # assert it start with F and is 16 characters long
    with open("/etc/waggle/node-id", "r") as file:
        content = file.readline()
    assert len(content) == 16
    assert content[0] == "F"
