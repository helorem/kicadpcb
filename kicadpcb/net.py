from track import Track

class Net:
    def __init__(self, index, name):
        self.index = index
        self.name = name
        self.pads = []
        self.tracks = []

    def add_pad(self, pad):
        pad.net = self
        self.pads.append(pad)

    def add_track(self, track):
        track.net = self
        self.tracks.append(track)

    def get_pcb_data(self):
        # (net 1 VI)
        sexpr_data = ["net", self.index, self.name]
        return sexpr_data

    def autoroute(self, pf):
        previous_pad = None
        for pad in self.pads:
            if previous_pad:
                track = Track(previous_pad, pad)
                self.add_track(track)
                track.autoroute(pf)
            previous_pad = pad
