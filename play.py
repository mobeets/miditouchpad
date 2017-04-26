import sys
import time
import mido
import threading
from multitouch import start_devices_with_callback, bind_callback
from midipad import DefaultMidiPad

def play(port_name='MidiPad-Port'):
    with mido.open_output(port_name, virtual=True) as outport:
        M = DefaultMidiPad(outport)
        fcn = bind_callback(M.update)
        start_devices_with_callback(fcn)
        while threading.active_count():
            time.sleep(0.125)

if __name__ == '__main__':
    play()
