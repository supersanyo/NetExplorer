import NetExplorer
class Logger:
    def emit(self, txt):
        print(txt)
logger = Logger()
#netlist = NetExplorer.parse('netlist.scs')
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
