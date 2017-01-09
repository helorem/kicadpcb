import sexpr
import constants
import functions
import footprint
import component
import net

class Netlist:
    def __init__(self):
        self.sexpr_data = None
        self.components = {}
        self.nets = {}

    def parse(self, content):
        self.sexpr_data = sexpr.parse_sexp(content)

        headers = {
            "field" : [None, "val"]
        }

        key, main_dict = functions.sexpr2dict(self.sexpr_data, headers)

        for item in main_dict["components"]["comp"]:
            folder, name = item["footprint"].split(":")
            foot = footprint.Footprint(constants.KICAD_MODULE_FOLDER + "/%s.pretty/%s.kicad_mod" % (folder, name))
            self.components[item["ref"]] = component.Component(foot)

        index = 1
        for item in main_dict["nets"]["net"]:
            net_item = net.Net(index, item["name"])
            nodes = item["node"]
            if type(nodes) != type([]):
                nodes = [nodes]
            for node in nodes:
                comp = self.components[node["ref"]]
                net_item.add_pad(comp.get_pad(node["pin"]))
            self.nets[item["name"]] = net_item
            index += 1

