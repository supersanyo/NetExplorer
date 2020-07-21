from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import INSERT
import logging
import NetExplorer

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("NetExplorer")
        self.netlist = None
        self.init_window()

    def __trace_signal(self):
        assert self.cur_subckt_name
        assert self.cur_net
        self.logger.emit("\n===== Signal Trace =====")
        self.logger.emit("Subckt Name: %s" % self.cur_subckt_name)
        self.logger.emit("Net Name: %s\n" % self.cur_net)
        self.netlist.trace_signal(self.cur_net, self.cur_subckt_name)
        self.logger.emit("===== Signal Trace End =====")

    def __subckt_info(self):
        assert self.cur_subckt_name
        if self.cur_subckt_name == 'root':
            subckt = self.netlist.root
        else:
            subckt = self.netlist.subckts[self.cur_subckt_name]
        self.logger.emit(subckt.str())

    def __instance_info(self):
        assert self.cur_instance_name
        assert self.cur_subckt_name
        assert self.cur_parent_name
        if self.cur_parent_name == 'root':
            subckt = self.netlist.root
        else:
            subckt = self.netlist.subckts[self.cur_parent_name]
        instance = None
        for inst in subckt.instances:
            if (inst.instance_name == self.cur_instance_name) and \
                (inst.subckt_name == self.cur_subckt_name):
                instance = inst
                break
        assert instance
        self.logger.emit(instance.str())

    def __subckt_usage_list(self):
        assert self.cur_subckt_name
        self.logger.emit("\n===== Subckt Usage List =====")
        self.logger.emit("Subckt Name: %s" % self.cur_subckt_name)
        self.netlist.subckt_usage_list(self.cur_subckt_name)
        self.logger.emit("===== Subckt Usage List End =====")

    def __signal_consistnecy(self):
        assert self.cur_subckt_name
        self.logger.emit("\n===== Signal Consistency Check =====")
        self.logger.emit("Subckt Name: %s" % self.cur_subckt_name)
        self.netlist.signal_consistency(self.cur_subckt_name)
        self.logger.emit("\n===== Signal Consistency Check End =====")

    def init_log_window(self):
        """ Log Frame """
        log_frame = LabelFrame(self, text="Output Log")
        log_frame.pack(side = BOTTOM, expand = True, fill = BOTH)


        self.log = Text(log_frame)
        vsb = ttk.Scrollbar(log_frame, orient="vertical", command = self.log.yview)
        self.log.configure(yscrollcommand=vsb.set)

        self.log.pack(side = LEFT, expand = True, fill = BOTH)
        vsb.pack(side = RIGHT, fill = Y)

        self.logger = WidgetLogger(self.log)

    def _popup_menu(self, event):
        self.cur_subckt_name = None
        self.cur_net = None
        self.cur_instance_name = None
        self.cur_parent_name = None

        item = self.tree.identify('item', event.x, event.y)
        instance_name = self.tree.item(item, 'text')

        values = self.tree.item(item, 'values')
        if len(values) != 2:
            return

        type = values[0]
        if type == 'subckt' or type =='unbound subckt':
            self.cur_subckt_name = values[1]
            self.cur_instance_name = instance_name
            parent_iid = self.tree.parent(item)
            if parent_iid:
                self.cur_parent_name = self.tree.item(parent_iid, 'values')[1]
        elif type == 'net':
            parent_iid = self.tree.parent(item)
            self.cur_subckt_name = self.tree.item(parent_iid, 'values')[1]
            self.cur_net = instance_name
        else:
            self.logger.emit("Incorrect type: %s" % type)
            assert False
        
        self.logger.emit("Selected \"%s\" node" % instance_name)
        # Right click menuu
        m = Menu(self.tree, tearoff=0)
        if self.cur_net:
            # Net related Menu
            m.add_command(label="Signal Trace", command = self.__trace_signal)
        else:
            if self.cur_subckt_name != 'root':
                m.add_command(label="Instance Info", command = self.__instance_info)
            if type == 'subckt':
                m.add_command(label="Subckt Info", command = self.__subckt_info)
                m.add_command(label="Subckt Signal Consistency Check", command = self.__signal_consistnecy)
            m.add_command(label="Subckt Usage List", command = self.__subckt_usage_list)

        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()


    def init_tree_window(self):
        """ Tree Frame """
        self.tree_frame = LabelFrame(self, text="Netlist Tree View")
        self.tree_frame.pack(side = LEFT, expand = True, fill = BOTH)

        self.tree = ttk.Treeview(self.tree_frame)
        self.tree["columns"] = ("types", "subckt")
        self.tree.heading("#0", text="Instance Name")
        self.tree.heading("types", text="Types")
        self.tree.heading("subckt", text="SubCircuit")

        self.tree.pack(side = LEFT, expand = True, fill = BOTH)

        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command = self.tree.yview)
        vsb.pack(side = RIGHT, fill = Y)
        self.tree.configure(yscrollcommand=vsb.set)

        # Click event
        self.tree.bind("<Button-3>", self._popup_menu)


    def init_window(self):
        self.pack(fill=BOTH, expand=1)
        self.init_tree_window()
        self.init_log_window()

        self.open_file()

    def open_file(self):
        if self.netlist:
            self.logger.emit("Netlist already loaded")
        self.filename = filedialog.askopenfilename(initialdir = ".", filetypes=[("spectre netlist", "*.scs"), ("all files", "*.*")])
        

        self.logger.emit("Open File: %s" % self.filename)
        self.netlist = NetExplorer.parse(self.filename, self.logger)
        self._insert_tree(None, self.filename, self.netlist.root)
        self.tree_frame['text'] = self.filename

    def _insert_tree(self, parent, instance_name, subckt):
        if parent:
            node = self.tree.insert(parent, 0, None, text = instance_name, value=("subckt", subckt.name))
        else:
            node = self.tree.insert("", 0, None, text = self.filename, value = ("subckt", "root"))

        # Add Nets
        for net in subckt.nets.keys():
            self.tree.insert(node, "end", None, text = net, value=("net", None))

        for instance in subckt.instances:
            subckt_name = instance.subckt_name
            if subckt_name in self.netlist.subckts:
                subckt = self.netlist.subckts[subckt_name]

                instance_name = instance.instance_name

                self._insert_tree(node, instance_name, subckt)
            else:
                self.tree.insert(node, 0, None, text = instance.instance_name, value=("unbound subckt", subckt_name))
                

class WidgetLogger(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget=widget

    def emit(self, record):
        self.widget.insert(INSERT, record+'\n')
        self.widget.yview_moveto(1)

root = Tk()
app = Application(master=root)
app.mainloop()
