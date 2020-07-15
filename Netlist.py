
class Netlist:
    def __init__(self, name):
        self.name = name
        self.root = Subckt(name)
        self.subckts = {}
        self.context_stack = [self.root]

    def context_subckt(self):
        return self.context_stack[len(self.context_stack)-1]

    def str(self):
        return self.root.str()

    """
        Signal Trace
        
        Description: print all the subckt the particular signal connects to
        Format: "--[Signal Name] [Instance Name] [Subcircuit Name]
        Input:
            signal_name (string) : name of the signal
            subckt_name (string) : default is root

    """
    def trace_signal(self, signal_name, subckt_name='root'):
        if subckt_name == 'root':
            subckt = self.root
        else:
            try:
                subckt = self.subckts[subckt_name]
            except:
                print("Subckt %s not found in this netlist" % subckt_name)
                return None
        self.__trace_signal(signal_name, subckt, 0)
        return

    def __trace_signal(self, signal_name, subckt, depth):
        if signal_name in subckt.nets:
            for inst, i in subckt.nets[signal_name]:
                indent = ''
                for x in range(depth):
                    indent+='--'
                print("%s %s %s %s" % ( indent, signal_name, inst.instance_name, inst.subckt_name))

                if inst.subckt_name in self.subckts:
                    sc = self.subckts[inst.subckt_name]
                    sig_name = sc.pins[i]
                    self.__trace_signal(sig_name, sc, depth+1)

    """
        Signal Consistency Check

        Description: Check whether instance signal name matches subcircuit signal name
        Input:
            subckt_name (string) : default is root
    """

    def signal_consistency(self, subckt_name='root'):
        if subckt_name == 'root':
            subckt = self.root
        else:
            try:
                subckt = self.subckts[subckt_name]
            except:
                print("Subckt %s not found in this netlist" % subckt_name)
                return None
        for inst in subckt.instances:
            inst_pins = inst.pins
            if inst.subckt_name in self.subckts:
                subckt_pins = self.subckts[inst.subckt_name].pins
                assert len(inst_pins) == len(subckt_pins)

                errors = []
                for i in range(len(inst_pins)):
                    if inst_pins[i] != subckt_pins[i]:
                        errors.append((inst_pins[i], subckt_pins[i]))
                if len(errors) > 0:
                    print()
                    print("=== %s vs %s ===" % (inst.instance_name, inst.subckt_name))
                    for e in errors:
                        print("%s vs %s" % e)

    """
        Subckt Usage Check

        Description: Check every occurance of the subckt in this netlist
        Input:
            subckt_name (string) : subckt name
    """
    def subckt_usage_list(self, subckt_name):
        stack = []
        for inst in self.root.instances:
            self._subckt_usage(subckt_name, inst, stack)
    
    def _subckt_usage(self, subckt_name, inst, stack):
        if inst.subckt_name == subckt_name:
            stack.append(inst.instance_name)
            print(".".join(stack))
            stack.pop()
            return

        if inst.subckt_name in self.subckts:
            children = self.subckts[inst.subckt_name].instances
            stack.append(inst.instance_name)
            for child in children:
                self._subckt_usage(subckt_name, child, stack)
            stack.pop()

class Subckt:
    def __init__(self, name):
        self.name = name
        self.instances = []
        self.nets = {}
        self.parameters = None
        self.pins = []

    def str(self):
        ret = '\n'
        ret += "===== Subckt Summary =====\n"
        ret += "Subckt Name: %s\n" % self.name
        ret += "Subckt Pins: %s\n" % self.pins
        ret += "Subckt Nets: %s\n" % list(self.nets.keys())
        ret += "# of Nets: %d\n" % len(self.nets)
        ret += "# of Instances: %d\n" % len(self.instances)
        ret += "# of Parameters: %d\n" % (len(self.parameters) if self.parameters else 0)
        ret += "===== End Summary =====\n"
        return ret

class Instance:
    def __init__(self):
        self.subckt_name = None
        self.instance_name = None
        self.pins = []
        self.parameters = None

    def str(self):
        ret = '\n'
        ret += "===== Instance Summary =====\n"
        ret += "Instance Name: %s\n" % self.instance_name
        ret += "Subckt Name: %s\n" % self.subckt_name
        ret += "Subckt Pin Order: %s\n" % self.pins
        ret += "# of Parameters: %d\n" % (len(self.parameters) if self.parameters else 0)
        ret += "===== End Summary =====\n"
        return ret
