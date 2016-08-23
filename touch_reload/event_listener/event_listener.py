import sys


class EventListener(object):
    def write_stdout(self, s):
        # only eventlistener protocol messages may be sent to stdout
        sys.stdout.write(s)
        sys.stdout.flush()

    def write_stderr(self, s):
        sys.stderr.write("{}\n".format(s))
        sys.stderr.flush()

    def send_ready(self):
        self.write_stdout('READY\n')

    def send_ok(self):
        self.write_stdout('RESULT 2\nOK')

    def read_headers(self):
        line = sys.stdin.readline()
        self.write_stderr(line)
        headers = dict([x.split(':') for x in line.split()])
        return headers

    def read_data(self, data_len):
        return sys.stdin.read(data_len)

    def on_event(self, headers, data):
        raise NotImplementedError

    def start_loop(self):
        while True:
            self.send_ready()
            headers = self.read_headers()
            data = self.read_data(int(headers['len']))
            self.on_event(headers, data)
            self.send_ok()
