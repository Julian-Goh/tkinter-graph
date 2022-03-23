import tkinter as tk
from tkinter import filedialog
import os
import re
import pathlib

import numpy as np

import cv2

from ScrolledCanvas import ScrolledCanvas
from tk_custom_combobox import CustomBox
from Tk_MsgBox.custom_msgbox import Ask_Msgbox

import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from matplotlib.figure import Figure 
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Root_Window(tk.Tk):
    ### This class is used to prevent root from flashing if user plan to change the app icon.
    def __init__(self,*args,**kw):
        tk.Tk.__init__(self,*args,**kw)
        self.withdraw() #hide the window
        self.after(0,self.deiconify) #as soon as possible (after app starts) show again


class Tkinter_Graph_GUI(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.__file_ext_list = [("All Files","*")] ### Allow all types of file extensions
        ''' 
        You can change the format list if you want a specific file extentions support in this app. 
        E.g. if you only allow image-type file extensions you can set self.__file_ext_list as below:
        self.__file_ext_list = [("All Files","*.bmp *.jpg *.jpeg *.png *.tiff"),
                                ('BMP file', '*.bmp'),
                                ('JPG file', '*.jpg'),
                                ('JPEG file', '*.jpeg'),
                                ('PNG file', '*.png'),
                                ('TIFF file', '*.tiff')]

        '''
        self.__curr_file_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\\Sample'
        self.__file_dict = {} ### Dictionary to store the file paths of the selected files.


        self.load_file_btn = tk.Button(master = self, relief = tk.GROOVE, font = 'Helvetica 16', text = 'Load File')
        self.load_file_btn['command'] = self.load_file
        self.load_file_btn.place(x = 5, y = 5, anchor = 'nw')

        self.load_file_btn.update_idletasks()

        self.tk_file_lb = tk.Label(master = self, font = 'Helvetica 14', text = 'Current File:', bg = 'white')
        self.tk_file_lb.place(x = 20 + self.load_file_btn.winfo_width()
            , y = 12, anchor = 'nw')

        self.tk_file_lb.update_idletasks()

        ### self.tk_dropdown is a widget to allow user to select a desired file before generating a graph plot
        self.tk_dropdown = CustomBox(master = self, width = 25, font = 'Helvetica 14', state = 'readonly')
        self.tk_dropdown.unbind_class("TCombobox", "<MouseWheel>")
        self.tk_dropdown.bind('<<ComboboxSelected>>', self.file_dropdown_sel)

        self.tk_dropdown.place(x = 20 + self.load_file_btn.winfo_width() + self.tk_file_lb.winfo_width()
            , y = 12, anchor = 'nw')

        ### Initialize the graph display on tkinter
        self.graph_fig = Figure(figsize = (7,7)) ### Figure object from matplotlib.figure
        self.plot_graph_fig = self.graph_fig.add_subplot(111)
        self.plot_graph_fig.clear() ### Initialize phase we clear the plot

        self.graph_fig.suptitle('Graph Data', fontsize=18)
        self.plot_graph_fig.set_ylabel('Y-Axis', fontsize=16)
        self.plot_graph_fig.set_xlabel('X-Axis', fontsize=16)

        self.tk_frame_graph_fig = tk.Frame(master = self, height = 700) ### We create frame widget to place self.tk_canvas_graph_fig inside.

        self.tk_canvas_graph_fig = FigureCanvasTkAgg(self.graph_fig, master = self.tk_frame_graph_fig)
        self.tk_canvas_graph_fig.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.tk_frame_toolbar = tk.Frame(master = self, height = 35)
        self.toolbar_graph_fig = tkagg.NavigationToolbar2Tk(self.tk_canvas_graph_fig, self.tk_frame_toolbar)
        
        self.tk_frame_graph_fig.place(x = 0, y = self.load_file_btn.winfo_height() + 15, relwidth = 1, anchor = 'nw')
        self.tk_frame_toolbar.place(relx = 0.1, y = 700 + self.load_file_btn.winfo_height() + 15, relwidth = 0.8, anchor = 'nw')
        
        self.toolbar_graph_fig.update_idletasks()

        ### In this example we will plot a graph of y versus x, so we will use .plot from matplotlib.figure. If you wish to use other type(s) of graph, you may need to search online on how to do so.
        self.ax_plt_fig = self.plot_graph_fig.plot([], [], color = "blue")


    def load_file(self):
        f = filedialog.askopenfilenames(initialdir = self.__curr_file_dir, title="Select file", filetypes = self.__file_ext_list)
        if f == '':
            ### No files selected
            pass
        else:
            file_list = []
            for file_path in f:
                file_name = (re.findall(r'[^\\/]+|[\\/]', file_path))[-1]
                file_list.append(file_name)
                self.__file_dict[str(file_name)] = file_path

            self.tk_dropdown['values'] = file_list
            self.tk_dropdown.current(0)
            self.file_dropdown_sel(event = None)
            ### file_extension = os.path.splitext(f)[-1]
            ### file_name = (re.findall(r'[^\\/]+|[\\/]', file_path))[-1]
            ### file_basename = os.path.basename(os.path.splitext(f)[0]) ## without file extension
            ### folder_name = str((pathlib.Path(f)).parent)

    def file_dropdown_sel(self, event):
        file_name = str(self.tk_dropdown.get())
        if file_name in self.__file_dict:
            ### Here when user select something from tk_dropdown, we pass the file path to a function which converts/loads the numpy-data.
            numpy_data = self.convert_img_numpy(self.__file_dict[file_name])
            self.plot_graph_func(numpy_data)


    def convert_img_numpy(self, img_path):
        ''' 
        In this example, I plan to use numpy-data from image files to plot a graph. Hence, I create this function for this sole purpose only.
        You can create a custom function to obtain numpy-data from your desired file.
        '''
        return cv2.imread(img_path)

    def plot_graph_func(self, numpy_data):
        '''
        Function to plot the graph when given numpy-data.
        NOTE: In this example we will plot a graph of y versus x, so we will use .plot from matplotlib.figure. If you wish to use other type(s) of graph, you may need to search online on how to do so.
        So, everything within "Graph Function" can be modified
        '''
        if (isinstance(numpy_data, np.ndarray)) == True:
            '''---------------------------> Graph Function --------------------------->
                Start
            '''
            ### Since we are plotting an image histogram we will slice the x-axis into values from 0 - 255.
            if len(numpy_data.shape) > 2: ## If image 3-channel, we have to conver to grayscale 2-D numpy array (y versus x).
                numpy_data = cv2.cvtColor(numpy_data, cv2.COLOR_BGR2GRAY)

            if len(numpy_data.shape) == 2:
                hist_x_index = []
                for i in range(256):
                    hist_x_index.append(i)

                ### Convert numpy data into graph data -- which can be passed into .plot from matplotlib.figure.
                graph_data = cv2.calcHist([numpy_data], [0], None, [256], [0,256])

                self.ax_plt_fig[0].set_data(hist_x_index, graph_data)

                _graph_spacing_x = int(round( np.multiply(np.max(hist_x_index), 0.025) )) + 1
                _graph_spacing_y = int(round( np.multiply(np.max(graph_data), 0.025) )) + 1

                self.plot_graph_fig.set_xlim(xmin = 0-_graph_spacing_x, xmax = 255+_graph_spacing_x)
                self.plot_graph_fig.set_ylim(ymin = 0-_graph_spacing_y, ymax = np.max(graph_data)+_graph_spacing_y)
            '''---------------------------> Graph Function --------------------------->
                End
            '''

            ### Draw the plot onto self.tk_canvas_graph_fig
            self.tk_canvas_graph_fig.draw()


if __name__ == '__main__':
    
    from functools import partial

    def close_protocol(tk_root):
        ask_msgbox = Ask_Msgbox('Do you want to quit?', title = 'Quit', parent = tk_root, message_anchor = 'w')
        if ask_msgbox.ask_result() == True:
            tk_root.destroy()

    tk_root = Root_Window()
    tk_root.title('Tkinter Graph Display.exe')

    tk_root.resizable(True, True)
    tk_root_width = 890
    tk_root_height = 600
    tk_root.minsize(width=890, height=600)

    screen_width = tk_root.winfo_screenwidth()
    screen_height = tk_root.winfo_screenheight()

    x_coordinate = int((screen_width/2) - (tk_root_width/2))
    y_coordinate = int((screen_height/2) - (tk_root_height/2))

    tk_root.geometry("{}x{}+{}+{}".format(tk_root_width, tk_root_height, x_coordinate, y_coordinate)) ## Set the display to be center of the screen when initialize

    tk_scroll_class = ScrolledCanvas(master = tk_root, frame_w = tk_root_width, frame_h = 850, canvas_x = 0, canvas_y = 0, canvas_highlightthickness = 0)
    tk_scroll_class.rmb_all_func()

    tk_graph_gui = Tkinter_Graph_GUI(parent = tk_scroll_class.window_fr, bg = 'white')
    tk_graph_gui.place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 1, relheight = 1, anchor = 'nw')

    tk_root.protocol("WM_DELETE_WINDOW", partial(close_protocol, tk_root = tk_root))

    tk_root.mainloop()
