import argparse
import xmlrpclib
import sys
import logging
import os
import supervisor.xmlrpc
import socket

from event_listener import EventListener

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


def check_socket_format(s):
    if not (s.startswith('http') or s.startswith("unix:///")):
        raise argparse.ArgumentTypeError(
            """Socket parameter can have only
"http(s)://" or "unix:///" format""")
    return s


def parse_args():
    parser = argparse.ArgumentParser(description="""Event listener for supervisord\n
that monitors special file and restart process if that file was changed""")

    parser.add_argument(
        "--socket",
        type=check_socket_format,
        help="address of socket file or tcp socket",
        required=True,
    )
    parser.add_argument(
        "--file",
        type=str,
        help="file to monitor",
        required=True,
    )
    parser.add_argument(
        "--program",
        help="name of supervisord program to restart",
        required=True,
    )
    parser.add_argument(
        "--username",
        help="xmlrpc username",
        nargs="?",
        const=None,
    )
    parser.add_argument(
        "--password",
        help="xmlrpc username",
        nargs="?",
        const=None,
    )
    return parser.parse_args()


class FileChecker():
    def __init__(self, checking_file):
        self.file = checking_file
        self.access_time = os.path.getmtime(self.file)

    def __call__(self):
        current_access_time = os.path.getmtime(self.file)
        if self.access_time < current_access_time:
            self.access_time = current_access_time
            return True
        return False


class TouchReloadEventListener(EventListener):
    def __init__(self, args, server):
        self.check = FileChecker(args.file)
        self.supervisor = server.supervisor
        self.args = args

    def action(self):
        self.supervisor.reloadConfig()
        self.supervisor.stopProcess(self.args.program)
        self.supervisor.startProcess(self.args.program)

    def on_event(self, headers, data):
        if not headers["eventname"] == "TICK_5":
            return
        if self.check():
            self.action()


def main():
    args = parse_args()
    server = xmlrpclib.Server(
        "http://127.0.0.1",
        transport=supervisor.xmlrpc.SupervisorTransport(
            args.username, args.password, serverurl=args.socket))

    if not os.path.isfile(args.file):
        logging.error("file {} doesn't exist".format(args.file))
        sys.exit(1)

    try:
        server.supervisor.getState()
    except socket.error:
        logging.error("Could not connect to socket: {}".format(args.socket))
        sys.exit(1)

    listener = TouchReloadEventListener(args, server)
    listener.start_loop()
