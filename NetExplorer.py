import re
from Netlist import *

def parse_param(line):
    """
    Input (string) : parameters to parse
    Output (dictionary) : parameter name as key, value stored in dictionary
    """
    res = {}
    i = 0
    read_name = True
    name = ''
    value = ''
    while i < len(line):
        if line[i] == '=':
            read_name = False
        elif read_name:
            name += line[i]
        elif line[i] == '[':
            while line[i] != ']':
                value += line[i]
                i+=1
            value += line[i]
        elif line[i] != ' ':
            value += line[i]
        else:
            res[name] = value
            name = ''
            value = ''
            read_name = True

        i+=1
    if len(name) > 0:
        res[name] = value
    return res

def parse_instance(line, netlist):
    """
    Input (string) : line for instance instantiation
    Output (Instance) : Instance object with information parsed from the line
    """
    
    line = line.strip()
    instance_name = ''
    subckt_name = ''
    pins = None
    params = None

    i = 0
    state = 0
    # state
    # 0: instance name
    # 1: pins
    # 2: subckt_name
    # else: parse param
    while i < len(line) and state <= 2:
        if line[i] == ' ':
            while i < len(line) and line[i] == ' ':
                i+= 1
            state += 1
        else:
            if state == 0:
                instance_name += line[i]
            elif state == 1:
                assert line[i] == '('
                i += 1
                temp_pin = ''
                while i < len(line) and line[i] != ')':
                    temp_pin += line[i]
                    i += 1
                assert line[i] == ')'
                pins = re.split("\s+", temp_pin)
            elif state == 2:
                subckt_name += line[i]
            else:
                print("No such state exists")
                assert False
            i += 1
    param_text = line[i:]
   
    # Create a new instance
    inst = Instance()
    inst.instance_name = instance_name
    inst.subckt_name = subckt_name
    inst.pins = pins
    inst.parameters = None if len(param_text) < 1 else parse_param(param_text)

    # Add instance to subckt
    subckt = netlist.context_subckt()
    subckt.instances.append(inst)
    # Added to nets
    for i in range(len(inst.pins)):
        p = inst.pins[i]
        nets = subckt.nets
        if p in nets:
            nets[p].append((inst, i))
        else:
            nets[p] = [(inst, i)]

def parse_line(line, netlist):
    items = line.split(' ', 1)
    header = items[0]
    
    if header == 'subckt':
        items = re.split("\s+", items[1].strip())
        subckt = Subckt(items[0])
        subckt.pins = items[1:]

        netlist.context_stack.append(subckt)
        netlist.subckts[subckt.name] = subckt

    elif header == 'parameters':
        subckt = netlist.context_subckt()
        subckt.parameters = parse_param(items[1])

    elif header == 'ends':
        netlist.context_stack.pop()

    else:
        parse_instance(line, netlist)

def parse(filename):
    """
    Input (string) : file name to be parsed
    Output (Netlist) : Netlist object with parsed information
    """
    fin = open(filename, 'r')
    lines = fin.readlines()
    fin.close()

    res = Netlist(filename)
    # Traverse every lines
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # skip if line is comment
        if len(line)!=0 and line[0:2] != '//':
            while line[len(line)-1] == "\\":
                i+=1
                line = line[:-1] +' '+ lines[i].strip()
            parse_line(line, res)
        i+=1
    return res
