import sys
import time
import mido
import threading
from multitouch import start_devices_with_callback, bind_callback
from midipad import MidiPad, MidiNote

class DefaultMidiPad(MidiPad):
    def touch_events(self, touch):
        # maps pos in (0,1) to note in (21, 109)
        pos_to_note = lambda pos: int(21 + 88*pos)
        notes = [pos_to_note(x) for (x,y) in touch.positions]
        print notes
        return [MidiNote(n) for n in notes]

def main(port_name='MidiPad-Port'):
    with mido.open_output(port_name, virtual=True) as outport:
        M = DefaultMidiPad(outport)
        fcn = bind_callback(M.update)
        start_devices_with_callback(fcn)
        while threading.active_count():
            time.sleep(0.125)

if __name__ == '__main__':
    main()
