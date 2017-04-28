
## Getting started

0. Install requirements with `pip install -r requirements.txt`
1. Open up GarageBand or Logic with a Software Instrument track
2. Run `python play.py` and drag your finger along the trackpad

## Options

The default MidiPad maps the x-position on your trackpad to notes, and the y-position to velocity (loudness). It also has a few options for specifying exactly which notes are played:

- Play notes in D major: `python play.py --notes D`
- Play notes in F# minor: `python play.py --notes f#`
- Change which octaves are included: `python play.py --octaves 4`
- Change the latency: `python play.py --latency 0.3`
