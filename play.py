import sys
import time
import mido
import argparse
import threading
from multitouch import start_devices_with_callback, bind_callback
from midipad import DefaultMidiPad, all_key_opts

def play(args, PadClass=DefaultMidiPad, port_name='MidiPad-Port'):
    """
    Opens a virtual midi port
        and calls M.update() whenever touch events are received
        where M is a MidiPad object
    """
    with mido.open_output(port_name, virtual=True) as outport:
        M = PadClass(outport,
            latency=args.latency,
            notes=args.notes)
        fcn = bind_callback(M.update)
        start_devices_with_callback(fcn)
        while threading.active_count():
            time.sleep(0.125)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--latency', type=float, default=0.1,
        help='how often to check for note updates (in secs)')
    parser.add_argument('--notes', type=str, default='all',
        choices=['all'] + all_key_opts,
        help='choose key name (lowercase is minor), or "all"')
    args = parser.parse_args()
    play(args)
