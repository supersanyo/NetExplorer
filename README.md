# NetExplorer
Convert partial spectre netlist into data structure in python 3 for analysis

## Example Setup
Sample spectre netlist _example.scs_
```
subckt inv a z vdd vss
    M0 (z a vdd vdd) pmos l=100n w=200n multi=1
    M1 (z a vss vss) nmos l=100n w=100n multi=1
ends inv

subckt nand2 a b z vdd vss
    M0 (z a vdd vdd) pmos l=100n w=200n multi=1
    M1 (z b vdd vdd) pmos l=100n w=200n multi=1
    M2 (z a net01 vss) nmos l=100n w=200n multi=1
    M3 (net01 b vss vss) nmos l=100n w=200n multi=1
ends nand2

subckt nor2 a b z vdd vss
    M0 (net01 a vdd vdd) pmos l=100n w=400n multi=1
    M1 (z b net01 vdd) pmos l=100n w=400n multi=1
    M2 (z a vss vss) nmos l=100n w=100n multi=1
    M3 (z b vss vss) nmos l=100n w=100n multi=1
ends nor2

subckt and2 a b z vdd vss
    I0 (a b zn vdd vss) nand2
    I1 (zn z vdd vss) inv
ends

I0 (a b net01 vdd vss) and2
I1 (net01 c net02 vdd vss) nor2
I2 (net02 out vdd vss) inv


V0 (a 0) vsource dc=1 type=dc
V1 (b 0) vsource dc=1 type=dc
V2 (c 0) vsource dc=1 type=dc
```
### GUI Mode
Execute `python3 NetExplorerGUI.py` and open the spectre netlist file
Right click on the items on the tree view on the left side for comprehensive features to be displayed in the log output on the right side.

### Sample python script
```python
import NetExplorer
class Logger:
    def emit(self, txt):
        print(txt)
logger = Logger()
netlist = NetExplorer.parse("example.scs", logger)
print(netlist.str())

print()
print("===== Signal Trace Example =====")
netlist.trace_signal('c')
print()

print("===== Signal Consistency Check =====")
netlist.signal_consistency()
print()

print("===== Subckt Usage =====")
netlist.subckt_usage_list("inv")
```
### Script Result
The result is shown below after executing `python3 example.py`
```
===== Subckt Summary =====
Subckt Name: example.scs
Subckt Pins: []
Subckt Nets: ['a', 'b', 'net01', 'vdd', 'vss', 'c', 'net02', 'out', '0']
# of Nets: 9
# of Instances: 6
# of Parameters: 0
===== End Summary =====


===== Signal Trace Example =====
 c I1 nor2
-- b M1 pmos
-- b M3 nmos
 c V2 vsource

===== Signal Consistency Check =====

=== I0 vs and2 ===
net01 vs z

=== I1 vs nor2 ===
net01 vs a
c vs b
net02 vs z

=== I2 vs inv ===
net02 vs a
out vs z

===== Subckt Usage =====
I0.I1
I2
```
