import numpy as np
from midipad import MidiPad, MidiNote

# all_notes = xrange(21, 109)
all_notes = range(60, 72)
Cmaj = [60, 62, 64, 65, 67, 69, 71, 72]
Cmin = [60, 62, 63, 65, 67, 69, 70, 71]
key_opts = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
all_key_opts = key_opts + [x.lower() for x in key_opts]

def get_notes_from_key(key):
    if key == 'all':
        return all_notes
    offset = key_opts.index(key.upper())
    if key.islower():
        return [x+offset for x in Cmin]
    return [x+offset for x in Cmaj]

def get_notes(key, octaves):
    """
    get notes in key spanning certain number of octaves
    """
    notes = get_notes_from_key(key)
    nnotes = len(notes)
    notes = np.tile(notes, (7,1))
    mults = np.arange(-3,4)
    notes += 12*np.tile(mults, (nnotes,1)).T
    notes = notes[np.array(octaves)-1]
    return notes.flatten().tolist()

def discretize(pos, vals):
    """
    maps pos in (0,1) to val in vals
        e.g. discretize(0.1, xrange(21, 109))
        maps the position 0.1 to a pitch on 88-key keyboard

    pos is float in (0,1)
    vals is list of values
    """
    ind = np.digitize([pos*len(vals)+1 - 1.0], xrange(len(vals)))[0]
    return vals[ind-1]

class DefaultMidiPad(MidiPad):
    def __init__(self, outport, notes='all', octaves=3,
        latency=0.1, n_fingers_to_pause=5):
        MidiPad.__init__(self, outport, latency, n_fingers_to_pause)
        self.note_opts = get_notes(notes, octaves)

    def touch_events(self, touch):
        """
        maps x position to pitch, y position to velocity
        """
        events = []
        for (x,y),(a,b,c) in zip(touch.positions, touch.ellipses):
            event = MidiNote(note=discretize(x, self.note_opts),
                        velocity=discretize(y, xrange(0, 128)),
                        identifier=a)
            events.append(event)
        print events
        return events
