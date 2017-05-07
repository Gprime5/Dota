from tkinter import Tk, Menu
from pyautogui import position
from tkinter.ttk import Button, Label, Frame, Treeview, Scrollbar, Style
from load import load
import webbrowser as w
from update import update

class main(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.title("Dota")
        self.attributes("-topmost", True)
        x, y = position()
        self.geometry("+2200+340")
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)
        self.minsize(300, 300)

        row0 = Frame(self)
        row0.grid(sticky = "nw")

        self.lbl = Label(self)
        self.lbl.grid(row = 2, sticky = "sw", padx = 5, pady = 5)
    
        Button(row0,
               text = "Load Game Info",
               command = load(self).run,
               width = 20).grid(sticky = "nw", padx = 5, pady= 5)

        Button(row0,
               text = "Update Match History",
               command = update(self.lbl).run,
               width = 20).grid(column = 1, row = 0, sticky = "nw",
                                padx = 5, pady = 5)

        self.tv = self.tree()

        self.menu = Menu(self, tearoff = 0)
        
        self.menu.add_command(label = " Open", command = self.web_open)
        self.menu.add_command(label = "Open all", command = self.open_all)
        self.menu.add_command(label = "Close all", command = self.close_all)
        
        self.mainloop()

    def close_all(self):
        for tv_id in self.tv.get_children():
            if self.tv.item(tv_id)["values"]:
                self.tv.item(tv_id, open = False)

        self.geometry("300x300")

    def open_all(self):
        for tv_id in self.tv.get_children():
            if self.tv.item(tv_id)["values"]:
                self.tv.item(tv_id, open = True)

    def web_open(self):
        selection = self.tv.item(self.tv.selection())
        url = "https://www.dotabuff.com/matches/"
        
        if selection["tags"][0] == "player":
            if selection["values"]:
                if int(selection["values"][0]):
                    self.tv.item(self.tv.selection(), open = True)
                    for tv_id in self.tv.get_children(self.tv.selection()):
                        w.open(url + str(self.tv.item(tv_id)["values"][0]))

        elif selection["tags"][0] == "match":
            w.open(url + str(selection["values"][0]))

    def tree(self):
        tree_frame = Frame(self)
        tree_frame.columnconfigure(0, weight = 1)
        tree_frame.rowconfigure(0, weight = 1)
        tree_frame.grid(columnspan = 2, row = 1, sticky = "nwse",
                        padx = 5, pady = 5)
        
        tv = Treeview(tree_frame,
                      xscroll = lambda f, l: self.scroll(xs, f, l),
                      yscroll = lambda f, l: self.scroll(ys, f, l))
        tv.grid(column = 0, row = 0, sticky = "nwes")

        xs = Scrollbar(tree_frame, orient = 'horizontal', command = tv.xview)

        ys = Scrollbar(tree_frame, orient = 'vertical', command = tv.yview)
        
        Style().layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        tv["columns"] = ["match_ids"]
        tv.heading("#0", text = 'Name', anchor = 'w')
        tv.column("#0", stretch = 0, anchor = "w", width = 170, minwidth = 100)

        tv.heading('match_ids', text = 'Match Ids', anchor = 'w')
        tv.column('match_ids', anchor = 'w', width = 100, minwidth = 100)

        tv.bind("<Button-3>", self.popup)
        tv.tag_bind("player", "<<TreeviewClose>>", self.reset)

        return tv

    def reset(self, arg):
        self.geometry("300x300")

    def scroll(self, sbar, first, last):
        first, last = float(first), float(last)
        difference = last - first
        inverse = 10/difference - 10
        ceil = -(-inverse//1) * 20
        self.geometry("300x{:.0f}".format(ceil + self.winfo_height()))

    def popup(self, args):
        item = self.tv.identify_row(args.y)
        self.tv.selection_set(item)
        if item:
            self.menu.post(args.x_root, args.y_root)

if __name__ == "__main__":
    x = main()
