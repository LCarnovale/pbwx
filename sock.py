import socket as sc

PORT = 33710
HOST = "localhost"
byte_order = "big"


class PulseCommunicator:
    def __init__(self):
        # Create socket
        self.sock = sc.socket()
        # Connect with client

    def do_connect(self):
        try:
            self.sock.connect((HOST, PORT))
        except Exception as e:
            print("Unable to connect to %s:%d"%(HOST, PORT))
            raise e

    def send_info(self, raw_seq, acq_delay=0):
        # Send pulse length:
        length = raw_seq.length_ns
        length = int(length).to_bytes(16, byte_order)
        try:
            self.sock.send(length)
        except:
            self.do_connect()
            self.sock.send(length)


    def __enter__(self):
        print("entering")
        return self

    def __exit__(self, *args):
        print("Exiting", args)
        return True
        
    def __del__(self):
        self.sock.close()

class MockClient:
    def __init__(self):
        self.sock = sc.socket()
        print("Binding to %s:%d" % (HOST, PORT))
        self.sock.bind((HOST, PORT))


    def go(self):
        print("Listening with backlog 10")
        self.sock.listen(10)
        print("Awaiting connection...")
        conn, addr = self.sock.accept()
        print("Connection received from:", addr)
        print("Displaying all received data:")
        while True:
            a = conn.recv(32)
            if len(a) == 0:
                break
            a = int.from_bytes(a, byte_order)
            print(a)
        print("Stream ended.")
    
    def __del__(self):
        self.sock.close()
    
_client = None
_conn = None
def establish_client(force=False):
    global _client, _conn
    if _client is None or force:
        _client = sc.socket()
        _client.bind((HOST,PORT))
        # Try connect
        _client.listen(1)
        _conn, addr = _client.accept()
    
def get_data(byte_order=byte_order, n_bytes=16):
    establish_client()
    byts = _conn.recv(n_bytes)
    num = int.from_bytes(byts, byte_order)
    return num

def send_start():
    establish_client()
    _conn.send(b"START")

def send_stop():
    establish_client()
    _conn.send(b"STOP")

def test_server():
    with PulseCommunicator() as pc:
        pc.send_info(raw)

def test_client():
    mc = MockClient()
    mc.go()

if __name__ == "__main__":
    from pulse_src import load_pulse as lp

    rp = lp.read_pulse_file("pulses/test.pls")
    raw = rp.eval(N=2)
    # Use either test_client or test_server