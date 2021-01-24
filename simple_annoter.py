import tkinter as tk
from tkinter import *

from utils.fieldlabs import FieldLabels
from utils.fileReadWrite import FileReadWrite

from functools import partial

import logging
logging.basicConfig(level=logging.DEBUG)

class SimpleAnnoter:

    def __init__(self, infile=None, outfile=None,
                 labels=[], overwrite=False):

        self.root = Tk()

        self.root.title("Simple Annoter")
        
        self.labels = []
        self.autofill = True
        self.line = None

        # color list for label highlighting
        self.colors = ['red','orange','yellow','green',
                       'blue','violet']
        self.color_key = {}

        # helper class for storing annotations
        self.fields = FieldLabels(self.labels)
        # helper class for reading/writing files
        self.readwrite = FileReadWrite(infile=infile,outfile=outfile,
                                       append= not overwrite)
        self.readwrite.open_infile()
        self.readwrite.open_outfile()

        # set up for right click operations
        self.popup_menu = Menu(self.root, tearoff=0)
        self.root.bind("<Button-3>", self.popup)
        

        # frame for displaying text
        textframe = Frame(self.root)
        textframe.pack(fill=BOTH)
        
        self.textblock = Text(textframe, height = 8)
        self.textblock.config(font =("Arial", 14)) 
        self.textblock.pack(fill=BOTH, padx=5, expand=True)

        # frame for label buttons
        self.labelframe = Frame(self.root, relief=RAISED, borderwidth=1)
        self.labelframe.pack(fill=X)
        self.init_labels(labels)

        # frame for `add label` field
        self.addlabelframe = Frame(self.root)
        self.addlabelframe.pack(fill=X)
        self.add_label_label = Label(self.addlabelframe,
                                     text = "Add Label:") 
        self.label_name = Entry(self.addlabelframe)
        self.add_label_button = Button(self.addlabelframe, text ="Add",
                                       command = self.add_label)

        self.label_name.bind('<Return>', self.add_label)

        self.add_label_label.pack(side=LEFT, padx=5, pady=5)
        self.label_name.pack(side=LEFT, padx=5, pady=5)
        self.add_label_button.pack(side=LEFT, padx=5, pady=5)

        # frame for function buttons
        self.function_frame = Frame(self.root)
        self.function_frame.pack(fill=X)
        
        self.print_button = Button(self.function_frame,
                                   text = "Print and Next",
                                   command = self.show_next) 
        self.skip_button = Button(self.function_frame,
                                  text = "Skip",
                                  command = self.show_next) 
        self.clear_all_button = Button(self.function_frame,
                                       text = "Clear All",
                                       command = self.clear_all) 
        self.clear_last_button = Button(self.function_frame,
                                        text = "Clear Last",
                                        command = self.clear_last) 
        self.exit_button = Button(self.function_frame,
                                  text = "Exit", 
                                  command = self.root.destroy)
        self.taf = Checkbutton(self.function_frame,
                               text='autofill',
                               command=self.toggle_af)
        self.taf.select()
        [b.pack(side= LEFT, padx=5, pady=5) for b in [self.print_button,
                                                      self.skip_button,
                                                      self.clear_all_button,
                                                      self.clear_last_button,
                                                      self.exit_button,
                                                      self.taf]]

        
        # Create output preview window
        self.outputframe = Frame(self.root)
        self.outputframe.pack(fill=BOTH)
        self.output = Text(self.outputframe, height = 15) # , width = 100)
        self.output.pack(fill=BOTH, padx=5, expand=True)
            
        self.output.config(font =("Courier", 12)) 
        self.root.geometry("800x600")
        self.root.mainloop()

        self.readwrite.close_handles()
        
    def toggle_af(self):
        if self.autofill:
            self.autofill = False
        else:
            self.autofill = True

    def clear_all(self):
        self.fields.reset_labels()
        self.output.delete("1.0", tk.END)
        for tag in self.textblock.tag_names():
            self.textblock.tag_remove(tag, "1.0", "end")

    def clear_last(self):
        indices = self.fields.remove_last()
        if indices is not None:
            self.output.delete("1.0", tk.END)
            current_labels = self.fields.all_text()
            self.output.insert(tk.INSERT, current_labels)
            (tag, first, last) = indices[:-1]
            (first,last) = ("1.{}".format(first),"1.{}".format(last))
            self.textblock.tag_remove(tag, first, last)
        
    def show_next(self):
        if self.line is not None:
            d = {'entities' : self.fields.get_line()}
            annoted_line = "'{}', {}\n".format(self.line,d)
            
            if not self.readwrite.write_line(annoted_line):
                print(annoted_line)
        try:
            self.line = next(self.readwrite.read_line())
            self.textblock.config(state=NORMAL)
            self.textblock.delete("1.0", tk.END)
            self.clear_all()
            self.textblock.insert(tk.INSERT, self.line.strip())
            self.textblock.config(state=DISABLED)
        except Exception as e:
            logging.debug("exiting...")
            self.root.destroy()
    
    def add_field(self, l):        
        try:
            if self.autofill:
                indices = [self.textblock.index("sel.first wordstart"),
                           self.textblock.index("sel.last wordend")]
            else:
                indices = [self.textblock.index("sel.first"),
                           self.textblock.index("sel.last")]

            text = self.textblock.get(*indices)
            logging.debug("ADDED FIELD {}".format((text,*indices)))
            if text[-1] == '\n':
                indices[1] = self.textblock.index("sel.last wordend -1c")
                text = self.textblock.get(*indices)
                logging.debug("CORRECTED LINE {}".format((text,*indices)))

            indices = self.fields.add_example(l,(text,*indices))
            self.textblock.tag_add(l, *indices)
            self.textblock.tag_configure(l,
                                 background=self.color_key[l],
                                 relief='raised')
            self.textblock.tag_remove("sel", "sel.first", "sel.last")
        except Exception as e:
            logging.debug(e)
        self.output.delete("1.0", tk.END)
        current_labels = self.fields.all_text()
        self.output.insert(tk.INSERT, current_labels)
        logging.debug("FIELD LABELS {}".format(self.fields.get_line()))
 
    def add_label(self, *args): 
        label = self.label_name.get()
        label = label.strip()
        logging.debug("ADDED LABEL {}".format(label))
        self.init_labels([label])
        self.label_name.delete(0, tk.END)

    def init_labels(self,labels):
        for label in labels:
            if label != '' and self.fields.add_labels(label):
                color = self.colors.pop()
                self.colors = [color] + self.colors

                self.color_key[label] = color
                b = Button(self.labelframe,
                           text = label,
                           command = partial(self.add_field,label),
                           bg=color)
                b.pack(side= LEFT, padx=2.5, pady=5)
                self.popup_menu.add_command(label=label,

                                            command=partial(self.add_field,label),
                                            background=color)
                                            
    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()




import argparse
def main():
    parser = argparse.ArgumentParser(description='Parameters for annotator.')
    parser.add_argument('-i', '--input', default=argparse.SUPPRESS,
                        dest='infile',
                        help='path to input file')
    parser.add_argument('-o', '--output', default=argparse.SUPPRESS,
                        dest='outfile',
                        help='file to save annotations')
    parser.add_argument('--overwrite', action='store_true', default=False,
                        help='overwrite output file (default is to append)')
    parser.add_argument('-l', '--labels', default=argparse.SUPPRESS, nargs='*',
                        help='labels to preload in the annotator')
    args = parser.parse_args()
    logging.debug("command line vars {}".format(vars(args)))


    sa = SimpleAnnoter(**vars(args))

import sys
    
if __name__ == "__main__":
    main()

# TODO:
# - file in/out menus
# - inheritance thing

# - right click - basically working. I don't love it but this can be worked on. Maybe it's just my keyboard/mouse on my laptop
# - layout - work in progress. Much improved already.
# - accept already annotated text - This will take some thought. It should allow us to edit existing annotations. This seems like a phase 2
