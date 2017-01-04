import pathfinder

class Point:
    def __init__(self, x, y, pad = None):
        self.pad = pad
        self.x = x
        self.y = y
        if pad:
            self.x, self.y = pad.get_real_pos()
        self.prev = None
        self.next = None

class Track:
    def __init__(self, start_pad, end_pad):
        self.net = None
        self.start_point = Point(start_pad.x, start_pad.y, start_pad)
        self.end_point = Point(end_pad.x, end_pad.y, end_pad)
        self.add_track_point(self.end_point)

    def add_point(self, x, y):
        self.add_track_point(Point(x, y))

    def add_track_point(self, point):
        start = self.start_point

        point.prev = start
        point.next = start.next

        if start.next:
            start.next.prev = point
        start.next = point

    def get_segments(self):
        res = []

        pt1 = self.start_point
        pt2 = pt1
        pt = pt1.next
        while pt is not None:
            vec1_x = pt2.x - pt1.x
            vec1_y = pt2.y - pt1.y

            vec2_x = pt.x - pt2.x
            vec2_y = pt.y - pt2.y

            if (vec1_x != 0 or vec1_y != 0) and (vec1_x != vec2_x or vec1_y != vec2_y):
                res.append((pt1, pt2))
                pt1 = pt2
            pt2 = pt
            pt = pt.next
        res.append((pt1, pt2))

        return res

    def get_pcb_data(self):
        # Start : (segment (start 1.27 1.27) (end 0 1.27) (width 0.25) (layer F.Cu) (net 1) (status 400000))
        # Middle : (segment (start -2.5 5.04) (end 1.25 5.04) (width 0.25) (layer F.Cu) (net 1) (tstamp 58669899))
        # End : (segment (start -2.5 5.04) (end 1.25 5.04) (width 0.25) (layer F.Cu) (net 1) (tstamp 58669899) (status 800000))

        status_start = 0x400000
        status_end = 0x800000

        segments = self.get_segments()
        res = []
        for seg in segments:
            sexpr_data = ["segment",
                    ["start", seg[0].x, seg[0].y],
                    ["end", seg[1].x, seg[1].y],
                    ["width", 0.25],
                    ["layer", "F.Cu"],
                    ["net", self.net.index],
                ]
            status = 0
            if len(res) == 0:
                status += status_start
            if len(res) == len(segments) - 1:
                status += status_end
            if status:
                sexpr_data.append(["status", "%X" % status])
            res.append(sexpr_data)

        return res

    def autoroute(self, pf):
        pt1 = pf.get_point(self.start_point.x, self.start_point.y)
        pt2 = pf.get_point(self.end_point.x, self.end_point.y)
        pts = pf.search_path(pt1, pt2)
        for pt in pts:
            self.add_point(pt.x, pt.y)
        pf.lock_points(pts)




