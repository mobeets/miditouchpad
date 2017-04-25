import mido

class MidiPad:
    def __init__(self, outport):
        self.outport = outport
        self.positions = []
        self.current_notes = []
        self.last_timestep = time.time()
        self.latency = 1.0

    def update_notes(self, notes):
        for note in self.current_notes:
            if note not in notes:
                self.stop_note(note)
                self.current_notes.remove(note)
        for note in notes:
            if note not in self.current_notes:
                self.play_note(note)
                self.current_notes.append(note)

    def update_position(self, positions, timestep):
        if len(positions) == 0:
            return
        self.positions = positions
        if timestep - self.last_timestep > self.latency:
            notes = [x for (x,y) in self.positions]
            self.update_notes(notes)
            self.last_timestep = timestep

    def play_note(self, note, duration=0.125, velocity=127, channel=0):
        msgOn = mido.Message('note_on',
            note=note, velocity=velocity, channel=channel)
        self.outport.send(msgOn)
        print "Playing note: {}".format(note)

    def stop_note(self, note, duration=0.125, velocity=127, channel=0):
        msgOff = mido.Message('note_off',
            note=note, velocity=velocity, channel=channel)
        self.outport.send(msgOff)
        print "Stopping note: {}".format(note)
