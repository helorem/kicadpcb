import copy
import math
import constants

class Pad:
    def __init__(self, num, x, y, shape, component):
        self.num = num
        self.x = x
        self.y = y
        self.shape = shape
        if shape:
            shape.pad = self
        self.component = component
        self.net = None

    class ShapeCircle:
        def __init__(self, r):
            self.pad = None
            self.r = r

        def contains(self, pt, width = 0):
            x, y = self.pad.get_real_pos()
            val = pow(pt.x - x, 2) + pow(pt.y - y, 2)
            res = val <= pow(self.r + width + constants.FLOAT_HACK, 2)
            return res

        def intersect(self, pt1, pt2, width = 0):
            x1 = pt1.x
            y1 = pt1.y
            x2 = pt2.x
            y2 = pt2.y
            cx, cy = self.pad.get_real_pos()
            cr = self.r + width + constants.FLOAT_HACK

            x1 -= cx
            x2 -= cx
            y1 -= cy
            y2 -= cy
            dx = x2 - x1
            dy = y2 - y1
            dr_sqrt = pow(dx, 2) + pow(dy, 2)
            D = x1 * y2 - x2 * y1
            val = pow(cr, 2) * dr_sqrt
            res = val >= pow(D, 2)

            return res


        def __repr__(self):
            x, y = self.pad.get_real_pos()
            return "ShapeCircle(%.2f, %.2f, %.2f)" % (x, y, self.r)

    def get_real_pos(self):
        return self.component.get_real_pos(self.x, self.y)

class Component:
    def __init__(self, footprint):
        self.footprint = footprint
        self.x = 0
        self.y = 0
        self.w = self.footprint.w
        self.h = self.footprint.h
        self.rotation = 0
        self.pads = {}
        for item in self.footprint.pads:
            pad_x = item["at"][0]
            pad_y = item["at"][1]
            pad_num = item["number"]
            shape = None
            if item["shape"] == "circle":
                shape = Pad.ShapeCircle(item["size"][0] / 2)
            self.pads[pad_num] = Pad(pad_num, pad_x, pad_y, shape, self)

    def _getArray(self, data, value, depth=-1, result=None):
        if result is None: result = []
        for i in data:
            if type(i) == type([]):
                if depth == -1 or depth > 0:
                    self._getArray(i, value, depth - 1, result)
            else:
                if i == value:
                    result.append(data)
        return result

    def get_pad(self, pad_num):
        return self.pads[pad_num]

    def get_real_pos(self, x=0, y=0):
        # Update position
        rel_x = -self.footprint.min_x
        rel_y = -self.footprint.min_y

        new_x = self.x + x + rel_x
        new_y = self.y + y + rel_y
        if self.rotation == 90:
            new_x = self.x + rel_y + y
            new_y = self.y + self.footprint.max_x - x
        elif self.rotation == 180:
            new_x = self.x + self.footprint.max_x - x
            new_y = self.y + self.footprint.max_y - y
        elif self.rotation == 270:
            new_x = self.x + self.footprint.max_y - y
            new_y = self.y + rel_x + x
        return (new_x, new_y)

    def get_pcb_data(self):
        sexpr_data = copy.deepcopy(self.footprint.sexpr_data)

        # Update position
        x, y = self.get_real_pos()

        for item in self._getArray(sexpr_data, 'at', 1):
            sexpr_data.remove(item)
        sexpr_data.append(["at", x, y, self.rotation])

        for item in self._getArray(sexpr_data, 'pad'):
            pad_num = item[1]
            pad = self.pads[pad_num]
            if pad.net:
                item.append(pad.net.get_pcb_data())

        return sexpr_data

    def move(self, x, y):
        self.x = math.ceil(x / constants.GRID) * constants.GRID
        self.y = math.ceil(y / constants.GRID) * constants.GRID

    def rotate(self, angle):
        self.rotation = angle
        if self.rotation == 90 or self.rotation == 270:
            self.w = self.footprint.h
            self.h = self.footprint.w
        else:
            self.w = self.footprint.w
            self.h = self.footprint.h


