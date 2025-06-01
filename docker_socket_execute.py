#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
""" docker_socket_execute.py

    Run "docker exec" commands on a local docker socket without docker client.
"""

# The MIT License (MIT)
#
# Copyright (c) 2025 Georg Lutz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# We only use the standard library imports, so the script can be run in a
# minimal Python environment
import argparse
import http.client
import json
import logging
import socket
import sys

def docker_exec(container, command) -> bool:
    '''Executes a command in a docker container using the local docker socket'''

    # Connect to the Docker UNIX socket using http.client
    conn = http.client.HTTPConnection("localhost")
    conn.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    conn.sock.connect("/var/run/docker.sock")

    exec_data = {
        "AttachStdin": False,
        "AttachStdout": True,
        "AttachStderr": True,
        "Cmd": command.split(),
        "Tty": False,
        "Container": container
    }

    # Create exec instance
    conn.request(
        "POST",
        f"/containers/{container}/exec",
        body=json.dumps(exec_data),
        headers={"Content-Type": "application/json"}
    )
    response = conn.getresponse()
    if response.status != 201:
        logging.error("Failed to create exec instance: %s", response.read().decode('utf-8'))
        conn.close()
        return False
    exec_id = json.loads(response.read().decode('utf-8'))['Id']

    # Start exec instance
    start_data = {
        "Detach": False,
        "Tty": False,
        "ConsoleSize": [80, 64]
    }
    conn.request(
        "POST",
        f"/exec/{exec_id}/start",
        body=json.dumps(start_data),
        headers={"Content-Type": "application/json"}
    )
    response = conn.getresponse()
    if response.status != 200:
        logging.error("Failed to start exec instance: %s", response.read().decode('utf-8', errors='replace'))
        conn.close()
        return False
    output = response.read()
    if output.strip():
        logging.info("Command output:\n%s", output.decode('utf-8', errors='replace'))
    else:
        logging.info("Command executed successfully with no output.")

    conn.close()
    return True

def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="""Run "docker exec" commands on a local docker socket without docker client""")
    parser.add_argument("container", help="container name or ID to execute command in")
    parser.add_argument("command", help="Command to execute in the container")
    return parser.parse_args()

def main():
    '''main function, called when script file is executed directly'''
    args = get_args()
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    if docker_exec(args.container, args.command):
        logging.info("Command executed successfully in container %s", args.container)
    else:
        logging.error("Failed to execute command in container %s", args.container)
        sys.exit(1)

if __name__ == "__main__":
    main()
