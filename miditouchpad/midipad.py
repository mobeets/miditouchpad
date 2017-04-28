import time
import mido

class TouchPad:
    """
    Basic container for touch events
        positions: finger touch locations
        ellipses: finger touch ellipses
    """
    def __init__(self, positions, ellipses, n_fingers, timestamp):
        self.positions = positions
        self.ellipses = ellipses
        self.n_fingers = n_fingers
        self.timestamp = timestamp

class MidiEvent:
    """
    Any midi event you want MidiPad to add must define at minimum an update function
    """
    def __init__(self):
        self.is_done = False

    def update(self, new_events):
        """
        new_events is a list of MidiEvents being added on this cycle

        returns a mido.Message, or anything that can be added to a mido outport using outport.send(msg)
        """
        raise NotImplementedError

class MidiNote(MidiEvent):
    """
    MidiNote
    """
    def __init__(self, note, velocity=127, identifier=None, channel=0, max_duration=1000, threshold=1000):
        self.note = note
        self.velocity = velocity
        self.identifier = identifier
        self.threshold = threshold # try 1.58
        self.channel = channel
        self.timestamp = time.time()
        self.max_duration = max_duration
        self.duration = 0
        self.has_been_played = False
        self.is_done = False

    def update(self, new_events):
        """
        This gets called every time MidiPad.update_events() is called

        This MidiNote will play for the duration that a touch triggers a MidiNote event passing self.is_same_note()
        """
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
        if not isinstance(event, MidiNote) or not hasattr(event, 'identifier') or event.channel != self.channel:
            return False
        return event.note == self.note and event.identifier < self.threshold

    def __str__(self):
        return "MidiNote(note={}, vel={}, channel={})".format(self.note, self.velocity, self.channel)

    def __repr__(self):
        return self.__str__()

class MidiPad:
    """
    MidiPad
    """
    def __init__(self, outport, latency=0.1, n_fingers_to_pause=5):
        self.outport = outport # mido port for sending midi messages
        self.last_touch = None # store last touch event
        self.latency = latency
        self.events = []

        # by default, a touch event involving five fingers prevents calls to self.update_events()
        self.got_pause_touch = False
        self.n_fingers_to_pause = n_fingers_to_pause

    def update_events(self, events):
        """
        checks for matches with existing MidiNote objects
            then updates all events
            and sends events to the outport

        events is a list of MidiEvent objects
        """
        # add any note event that isn't already playing
        msgs = []
        new_events = []
        for event in events:
            if not isinstance(event, MidiNote):
                new_events.append(event)
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
        """
        touch is a TouchPad object with most recent touch event
        returns a list of MidiEvent objects
        """
        raise NotImplementedError
        
    def update(self, touch):
        """
        every time a touch event is triggered, this gets called
            only calls self.update_events() if duration given by latency has passed since last touch event
        
        touch is a TouchPad object
        """
        if self.paused(touch):
            return
        if self.last_touch is None or touch.timestamp - self.last_touch.timestamp > self.latency:
            events = self.touch_events(touch)
            self.update_events(events)
            self.last_touch = touch

    def paused(self, touch):
        """
        if enough fingers are touching, pause calls to self.update_events()

        touch is a TouchPad object
        """
        if len(touch.positions) == self.n_fingers_to_pause:
            self.got_pause_touch = not self.got_pause_touch
        return self.got_pause_touch
