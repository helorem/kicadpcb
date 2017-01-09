import skidl
import kicadpcb

gnd = skidl.Net('GND')  # Ground reference.
vin = skidl.Net('VI')   # Input voltage to the divider.
vout = skidl.Net('VO')  # Output voltage from the divider.
r1, r2 = 2 * skidl.Part('device', 'R', skidl.TEMPLATE)  # Create two resistors.
r1.value, r1.footprint = '1K',  'Resistors_SMD:R_0805'  # Set resistor values
r2.value, r2.footprint = '500', 'Resistors_SMD:R_0805'  # and footprints.
r1[1] += vin      # Connect the input to the first resistor.
r2[2] += gnd      # Connect the second resistor to ground.
vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

netlist_str = skidl.generate_netlist(file="/dev/null")

nl = kicadpcb.Netlist()
nl.parse(netlist_str)

comp1 = nl.components["R1"]
comp2 = nl.components["R2"]
MARGIN = 1 # space between components
comp2.move(comp1.x + comp1.w + MARGIN, comp2.y)

pcb = kicadpcb.Pcb('tst.kicad_pcb', "default.kicad_pcb")

for net in nl.nets.values():
    pcb.add_net(net)

for comp in nl.components.values():
    pcb.add_component(comp)

pcb.save()

