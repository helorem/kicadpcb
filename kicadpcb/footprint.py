import math
import sexpr

def sexpr2dict(data, headers):
    key = data[0]
    if key not in headers:
        return key, data[1:]
    res = {}
    for i in xrange(1, len(data)):
        item = data[i]
        if type(item) == type([]):
            sub_key, val = sexpr2dict(item, headers)
            res[sub_key] = val
        else:
            res[headers[key][i - 1]] = item
    return key, res

class Footprint:
    def __init__(self, filename):
        self.filename = filename
        self.pads = []

        # read the s-expression data
        with open(self.filename, 'r') as fd:
            sexpr_data = ''.join(fd.readlines())
        self.sexpr_data = sexpr.parse_sexp(sexpr_data)

        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0

        headers = {
            "pad" : ['number', 'type', 'shape'],
            "fp_line" : [],
            "fp_circle" : [],
            "fp_arc" : [],
            "fp_text" : ['id', 'content'],
            "model" : ['file'],
            "module": ["name"]
        }

        for sexpr_item in self.sexpr_data:
            key, item = sexpr2dict(sexpr_item, headers)
            if key == "fp_line":
                self._read_line(item)
            elif key == "fp_circle":
                self._read_circle(item)
            elif key == "pad":
                self._read_pad(item)

        self.w = self.max_x - self.min_x
        self.h = self.max_y - self.min_y

    def _update_min_max_x(self, x, w):
        if x - w < self.min_x:
            self.min_x = x - w
        if x + w > self.max_x:
            self.max_x = x + w

    def _update_min_max_y(self, y, h):
        if y - h < self.min_y:
            self.min_y = y - h
        if y + h > self.max_y:
            self.max_y = y + h

    def _read_pad(self, item):
            self.pads.append(item)
            x = item["at"][0]
            y = item["at"][1]

            if item["shape"] == "circle":
                r1 = item["size"][0] / 2
                self._update_min_max_x(x, r1)
                self._update_min_max_y(y, r1)

            elif item["shape"] == "oval":
                r1 = item["size"][1] / 2
                self._update_min_max_x(x, r1)
                self._update_min_max_y(y, r1)

                r2 = item["size"][0] / 2
                self._update_min_max_x(x, r2)
                self._update_min_max_y(y, r2)

            elif item["shape"] == "rect":
                w = item["size"][0] / 2
                self._update_min_max_x(x, w)

                h = item["size"][1] / 2
                self._update_min_max_y(y, h)

    def _read_circle(self, item):
        x = item["center"][0]
        y = item["center"][1]
        sx = item["end"][0]
        sy = item["end"][1]

        r = math.sqrt(pow(sx - x, 2) + pow(sy - y, 2))
        self._update_min_max_x(x, r)
        self._update_min_max_y(y, r)

    def _read_line(self, item):
        x1 = item["start"][0]
        y1 = item["start"][1]
        x2 = item["end"][0]
        y2 = item["end"][1]

        self._update_min_max_x(x1, 0)
        self._update_min_max_y(y1, 0)
        self._update_min_max_x(x2, 0)
        self._update_min_max_y(y2, 0)
