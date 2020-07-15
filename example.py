import NetExplorer
netlist = NetExplorer.parse("example.scs")
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
