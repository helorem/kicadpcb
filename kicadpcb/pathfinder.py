import constants
import math
import copy

def float_equals(a, b):
    return a >= b - constants.FLOAT_HACK and a <= b + constants.FLOAT_HACK

class PathFinder:
    def __init__(self):
        self.points = []
        self.entries = []
        self.links = []

    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.pad = None
            self.links = []
            self.locked = False
            self.status = None
            self.val = 0

        def equals(self, pt):
            return float_equals(self.x, pt.x) and float_equals(self.y, pt.y)

        def link_to(self, pt):
            found = False
            for link in self.links:
                if link == pt:
                    found = True
                    break
            if not found:
                self.links.append(pt)
                pt.links.append(self)

        def try_link_to(self, pt):
            min_x = pt.x - constants.GRID - constants.FLOAT_HACK
            max_x = pt.x + constants.GRID + constants.FLOAT_HACK
            min_y = pt.y - constants.GRID - constants.FLOAT_HACK
            max_y = pt.y + constants.GRID + constants.FLOAT_HACK
            if self.x >= min_x and self.x <= max_x and self.y >= min_y and self.y <= max_y:
                self.link_to(pt)

        def lock(self):
            self.locked = True

        def unlock(self):
            self.locked = False

        def get_link_cost(self, link):
            res = 2
            if link.x != self.x and link.y != self.y:
                res = 3
            return res

        def __repr__(self):
            return "Point(%.2f, %.2f)" % (self.x, self.y)

    def create_world(self, pads):
        init = False
        min_x = 0
        min_y = 0
        max_x = 0
        max_y = 0
        points = []
        pad_points = {}
        for pad in pads:
            x, y = pad.get_real_pos()
            x = round(x / constants.GRID) * constants.GRID
            y = round(y / constants.GRID) * constants.GRID
            points.append((x, y, pad))
            if not init:
                min_x = x
                min_y = y
                max_x = x
                max_y = y
                init = True
            else:
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y

        res_points = []
        y = min_y - constants.WORLD_MARGIN
        while y <= max_y + constants.WORLD_MARGIN + constants.FLOAT_HACK:
            x = min_x - constants.WORLD_MARGIN
            while x <= max_x + constants.WORLD_MARGIN + constants.FLOAT_HACK:
                pt = PathFinder.Point(x, y)
                for pt2 in res_points:
                    pt.try_link_to(pt2)
                res_points.append(pt)

                for lock_x, lock_y, pad in points:
                    if float_equals(lock_x, x) and float_equals(lock_y, y):
                        pad_points[pad] = pt
                        pt.pad = pad
                        pt.status = "entry"
                        #pt.lock()
                        self.entries.append(pt)
                        break

                x += constants.GRID
            y += constants.GRID
        self.points = res_points

        print len(self.points), "points", min_x, min_y, max_x, max_y
        for pad, pt in pad_points.iteritems():
            pad_links = []
            done_links = [pt]
            links = copy.copy(pt.links)
            while links:
                link = links.pop(0)
                done_links.append(link)
                if pad.shape and pad.shape.contains(link, constants.TRACK_SIZE * 1.5): # a point need tracksize / 2 for the track and tracksize for the separation space
                    link.pad = pad
                    for sub_link in link.links:
                        if sub_link not in links and sub_link not in pad_links and sub_link not in done_links:
                            links.append(sub_link)
                else:
                    pad_links.append(link)

            for link1 in pad_links:
                for link2 in pad_links:
                    if link2 in link1.links:
                        if pad.shape and pad.shape.intersect(link1, link2, constants.TRACK_SIZE * 1.5):
                            link1.links.remove(link2)
                            link2.links.remove(link1)

    def get_point(self, x, y):
        x = round(x / constants.GRID) * constants.GRID
        y = round(y / constants.GRID) * constants.GRID
        for pt in self.entries:
            if float_equals(pt.x, x) and float_equals(pt.y, y):
                return pt
        return None

    def _make_result(self, pt, res, target, source):
        res.append(pt)
        min_val = pt.val
        min_link = None
        for link in pt.links:
            if link == source:
                return res
            elif link.pad in (None, target.pad, source.pad):
                if min_val == 0 or (link.val > 0 and link.val < min_val):
                    min_val = link.val
                    min_link = link
        if not min_link:
            return res
        return self._make_result(min_link, res, target, source)

    def test_link_valid(self, pt1, pt2):
        if pt1.equals(pt2):
            return True

        for lpt1, lpt2 in self.links:
            if not float_equals(lpt1.x, lpt2.x) and not float_equals(lpt1.y, lpt2.y):
                if (float_equals(lpt1.x, pt1.x) or float_equals(lpt1.x, pt2.x)) and (float_equals(lpt1.y, pt1.y) or float_equals(lpt1.y, pt2.y)):
                    return False
        return True

    def _search(self, pts, source, target):
        pt = pts.pop(0)
        while pt:
            if pt == target:
                return self._make_result(pt, [], target, source)
            #print "test", pt, pt.val, target
            for link in pt.links:
                if link.pad in (None, target.pad, source.pad):
                    if self.test_link_valid(pt, link):
                        if link.status != "entry":
                            link_val = pt.val + pt.get_link_cost(link)
                            if link.val == 0 or link.val > link_val:
                                link.val = link_val
                        if not link.locked:
                            link.lock()
                            # insert
                            inserted = False
                            for i in xrange(len(pts) - 1, 0, -1):
                                fpt = pts[i]
                                if fpt.val <= link.val:
                                    pts.insert(i + 1, link)
                                    inserted = True
                                    break
                            if not inserted:
                                pts.insert(0, link)
            pt = pts.pop(0)

    def _reset_vals(self):
        for pt in self.points:
            pt.val = 0
            if pt.status is None:
                pt.unlock()

    def search_path(self, pt1, pt2):
        pt2.unlock()
        res = self._search([pt1], pt1, pt2)
        if res:
            res.append(pt1)
        pt2.lock()
        self._reset_vals()
        return res

    def lock_points(self, points, status="used"):
        pt1 = None
        for pt in points:
            if pt1:
                self.links.append((pt1, pt))
            pt1 = pt

            if pt.status is None:
                pt.status = status
                pt.lock()

    def print_world(self):
        output = []
        y = 0
        for pt in self.points:
            if y != pt.y:
                output.append("\n")
                y = pt.y
            if pt.status == "entry":
                output.append("O")
            elif pt.locked:
                output.append("#")
            else:
                output.append(".")
        print "".join(output)
    """
    @staticmethod
    def pads2points(pads):
        points = []
        for pad in pads:
            x, y = pad.get_real_pos()
            x = round(x / constants.GRID) * constants.GRID
            y = round(y / constants.GRID) * constants.GRID
            points.append((x, y))
        return points
    """

