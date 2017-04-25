import time
import mido
import numpy as np

class MidiPad:
    def __init__(self, outport, nkeys=88):
        self.outport = outport
        self.positions = []
        self.notes_on = np.zeros(nkeys,)
        self.notes_dur = np.zeros(nkeys,)
        self.max_note_duration = 1000
        self.last_timestamp = 0.0
        self.latency = 0.1

    def update_notes(self, notes):
        for note in notes:
            note_ind = note-21
            if self.notes_on[note_ind] == 0:
                self.play_note(note)
                self.notes_on[note_ind] = 1
            self.notes_dur[note_ind] += 1
        for note_ind in np.where(self.notes_on)[0]:
            note = note_ind+21
            if note not in notes or self.notes_dur[note_ind] > self.max_note_duration:
                self.stop_note(note)
                self.notes_on[note_ind] = 0
                self.notes_dur[note_ind] = 0

    def update_position(self, positions, timestamp):
        if len(positions) == 0:
            return
        self.positions = positions
        if timestamp - self.last_timestamp > self.latency:
            notes = self.positions_to_notes(positions)
            self.update_notes(notes)
            self.last_timestamp = timestamp

    def positions_to_notes(self, positions):
        pos_to_note = lambda pos: int(21 + 88*pos)
        return [pos_to_note(x) for (x,y) in self.positions]

    def play_note(self, note, duration=0.125, velocity=127, channel=0):
        print "Playing note: {}".format(note)
        msgOn = mido.Message('note_on',
            note=note, velocity=velocity, channel=channel)
        self.outport.send(msgOn)

    def stop_note(self, note, duration=0.125, velocity=127, channel=0):
        print "Stopping note: {}".format(note)
        msgOff = mido.Message('note_off',
            note=note, velocity=velocity, channel=channel)
        self.outport.send(msgOff)
