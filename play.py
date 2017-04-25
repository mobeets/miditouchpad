import time
import mido
import threading
from multitouch import start_devices_with_callback, bind_callback
from midipad import MidiPad

def position_handler(positions, timestamp, M=None):
    """
    positions is list of normalized touch positions: [(x,y), ...]
        where (0,0) is bottom-left, (1,1) is top-right
    """
    if M is not None:
        M.update_position(positions, timestamp)
    return 0

def main():
    with mido.open_output('This-Port', virtual=True) as outport:
        M = MidiPad(outport)
        handler = lambda pos, t: position_handler(pos, t, M=M)
        fcn = bind_callback(handler)
        start_devices_with_callback(fcn)
        while threading.active_count():
            time.sleep(0.125)

if __name__ == '__main__':
    main()
