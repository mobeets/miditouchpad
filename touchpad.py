import time
import mido
import threading
from multitouch import start_devices_with_callback, bind_callback
from midipad import MidiPad

"""
https://mido.readthedocs.io/en/latest/intro.html

see also: https://github.com/SpotlightKid/python-rtmidi/blob/master/examples/sequencer/sequencer.py
"""

def handler(pts, timestamp):
    """
    pts is list of normalized touch positions: [(x,y), ...]
        where (0,0) is bottom-left, (1,1) is top-right
    """
    print pts
    return 0

import numpy as np
def test():
    with mido.open_output('This-Port', virtual=True) as outport:
        M = MidiPad(outport)
        while True:
            n_notes = np.random.randint(0,3)
            notes = np.random.randint(60, 64, (n_notes,2)).tolist()
            M.update_position(notes, time.time())

def main():
    fcn = bind_callback(handler)
    start_devices_with_callback(fcn)
    while threading.active_count():
        time.sleep(0.125)

if __name__ == '__main__':
    test()
