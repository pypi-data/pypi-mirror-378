# ##### BEGIN GPL LICENSE BLOCK #####
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import argparse
import logging
import os
import sys
import uuid
from pathlib import Path



# REFACTOR: remove this in favor of a better env setup
replication_lib = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(str(replication_lib.parent))
sys.path.append(str(replication_lib.parent.parent))

from replication.constants import CONNECTION_TIMEOUT

logger = logging.getLogger(__name__)

import zmq

def heartbeat(address="127.0.0.1",
              id=None,
              port=5562,
              timeout=CONNECTION_TIMEOUT):
    contex = zmq.Context()
    command = contex.socket(zmq.DEALER)
    command.setsockopt(zmq.IDENTITY, uuid.UUID(id).bytes)
    command.connect(f"tcp://{address}:{port+2}")
    command.linger = 0
    loop_interval = timeout+1000

    poller = zmq.Poller()
    poller.register(command, zmq.POLLIN)

    command.send(b"INIT")
    logging.info("TTL running")
    while True:
        sockets = dict(poller.poll(loop_interval))

        if command in sockets:
            command.recv()
            command.send(b"PONG")
        else:
            command.close()
            exit(0)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', required=True,
                        help="port to listen")
    parser.add_argument('-d', '--destination', required=True,
                        help="address to listen")
    parser.add_argument('-i', '--id', required=True,
                        help="user id")
    parser.add_argument('-t', '--timeout', required=True,
                        help="timeout before disconnection")

    args = parser.parse_args()

    heartbeat(port=int(args.port),
              address=args.destination,
              id=args.id,
              timeout=int(args.timeout))
