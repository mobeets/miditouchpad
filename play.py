import sys
import time
import mido
import threading
from multitouch import start_devices_with_callback, bind_callback
from midipad import MidiPad

def main():
    with mido.open_output('MidiPad-Port', virtual=True) as outport:
        M = MidiPad(outport)
        fcn = bind_callback(M.update)
        start_devices_with_callback(fcn)
        while threading.active_count():
            time.sleep(0.125)

if __name__ == '__main__':
    main()
