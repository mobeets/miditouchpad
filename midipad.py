import time
import mido
import numpy as np

class MidiNote:
    def __init__(self, note, velocity=127, channel=0, max_duration=1000, verbose=True):
        self.note = note
        self.velocity = velocity
        self.channel = channel
        self.timestamp = time.time()
        self.max_duration = max_duration
        self.duration = 0
        self.has_been_played = False
        self.is_done = False

    def update(self, new_events):
        if not self.has_been_played:
            msg = self.play()
        elif any([e for e in new_events if self.is_same_note(e)]):
            if self.duration > self.max_duration:
                msg = self.stop()
            else:
                msg = self.sustain()
        else:
            msg = self.stop()
        return msg

    def play(self):
        assert(not self.has_been_played)
        msgOn = mido.Message('note_on', note=self.note,
            velocity=self.velocity, channel=self.channel)
        self.has_been_played = True
        return msgOn

    def stop(self):
        assert(self.has_been_played)
        msgOff = mido.Message('note_off', note=self.note,
            velocity=self.velocity, channel=self.channel)
        self.is_done = True
        return msgOff

    def sustain(self):
        assert(self.has_been_played)
        self.duration += 1
        return None

    def is_same_note(self, event):
        return isinstance(event, MidiNote) and event.note == self.note and event.channel == self.channel

    def __str__(self):
        return "MidiNote(note={}, vel={}, channel={})".format(self.note, self.velocity, self.channel)

    def __repr__(self):
        return self.__str__()

class MidiPad:
    def __init__(self, outport, nkeys=88, offset=21, latency=0.1, n_fingers_to_pause=5):
        self.outport = outport
        self.nkeys = nkeys
        self.offset = offset
        self.latency = latency
        self.events = []
        self.notes_on = np.zeros(nkeys+1,)
        self.notes_dur = np.zeros(nkeys+1,)
        self.max_note_duration = 1000
        self.last_touch = None
        self.got_pause_touch = False
        self.n_fingers_to_pause = n_fingers_to_pause

    def update_events(self, events):
        # add any note event that isn't already playing
        msgs = []
        new_events = []
        for event in events:
            if not isinstance(event, MidiNote):
                continue
            if not any([e for e in self.events if event.is_same_note(e)]):
                msgs.append(event.update([]))
                new_events.append(event)
        self.events.extend(new_events)
        # update all existing events
        for event in self.events:
            msgs.append(event.update(events))
            if event.is_done:
                self.events.remove(event)
        # send messages to outport
        for msg in msgs:
            if msg is None:
                continue
            self.outport.send(msg)

    def touch_events(self, touch):
        pos_to_note = lambda pos: int(self.offset + self.nkeys*pos)
        notes = [pos_to_note(x) for (x,y) in touch.positions]
        print notes
        return [MidiNote(n) for n in notes]
        
    def update(self, touch):
        if self.paused(touch):
            return
        if self.last_touch is None or touch.timestamp - self.last_touch.timestamp > self.latency:
            events = self.touch_events(touch)
            self.update_events(events)
            self.last_touch = touch

    def paused(self, touch):
        """
        if enough fingers are touching, pause note updates
        """
        if len(touch.positions) == self.n_fingers_to_pause:
            self.got_pause_touch = not self.got_pause_touch
        return self.got_pause_touch
