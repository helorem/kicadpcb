from kicadpcb import *

if __name__ == "__main__":

    # -- Load kicad footprints
    foot1 = Footprint(constants.KICAD_MODULE_FOLDER + "/Resistors_ThroughHole.pretty/Resistor_Array_SIP8.kicad_mod")
    foot2 = Footprint(constants.KICAD_MODULE_FOLDER + "/Resistors_ThroughHole.pretty/Resistor_TO-220_Horizontal_LargePads.kicad_mod")
    foot3 = Footprint(constants.KICAD_MODULE_FOLDER + "/Resistors_ThroughHole.pretty/Resistor_Horizontal_RM10mm.kicad_mod")

    # -- Instantiate components
    component1 = Component(foot1)
    component2 = Component(foot2)
    component3 = Component(foot3)

    # -- Place components
    MARGIN = 1 # space between components
    component2.move(component1.x + component1.w + MARGIN, component2.y)
    component3.move(component1.x, component1.y + component1.h + MARGIN)
    component2.rotate(90)

    # -- Create nets
    neta = Net(1, "A")
    neta.add_pad(component1.get_pad(2))
    neta.add_pad(component3.get_pad(2))

    netb = Net(2, "B")
    netb.add_pad(component1.get_pad(4))
    netb.add_pad(component3.get_pad(1))

    # -- Create PCB board
    # "default.kicad-pcb" is an empty kicad project.
    pcb = Pcb('tst.kicad_pcb', "default.kicad_pcb")

    # -- Add nets to the board
    pcb.add_net(neta)
    pcb.add_net(netb)

    # -- Add components to the board
    pcb.add_component(component1)
    pcb.add_component(component2)
    pcb.add_component(component3)


    # -- Initialize a pathfinder to calculate routes.
    pf = PathFinder()
    pf.create_world(pcb.get_all_pads()) # initialize pathfinding environment from the list of pads

    # -- Calulats routes
    neta.autoroute(pf)
    netb.autoroute(pf)

    #pf.print_world()

    # -- Save the pcb file
    pcb.save()

