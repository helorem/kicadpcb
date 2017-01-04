import sexpr

class Pcb:
    def __init__(self, filename, default=None):
        self.filename = filename
        self.nets = []
        self.components = []

        # read the s-expression data
        file_to_read = filename
        if default:
            file_to_read = default
        with open(file_to_read, 'r') as fd:
            sexpr_data = ''.join(fd.readlines())

        # parse s-expr
        sexpr_data = sexpr.parse_sexp(sexpr_data)
        self.sexpr_data = sexpr_data

    def get_all_pads(self):
        res = []
        for item in self.components:
            for pad in item.pads.values():
                res.append(pad)
        return res

    def add_net(self, net):
        self.nets.append(net)

    def add_component(self, component):
        self.components.append(component)

    def save(self):
        for item in self.nets:
            self.sexpr_data.append(item.get_pcb_data())

        for item in self.components:
            self.sexpr_data.append(item.get_pcb_data())

        for net in self.nets:
            for track in net.tracks:
                for item in track.get_pcb_data():
                    self.sexpr_data.append(item)

        # convert array data to s-expression and save in the disc
        output = sexpr.build_sexp(self.sexpr_data)
        output = sexpr.format_sexp(output)
        with open(self.filename, 'w') as fd:
            fd.write(output)


