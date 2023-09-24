import tkinter as tk
from tkinter import Menu, Label
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import itertools
import psutil

class System:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("System status display")
        
        self.frame = tk.Frame(self.window, width=800, height=400)
        self.frame.pack()

        menubar = Menu(self.window)
        self.window.config(menu=menubar)

        options_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=options_menu)

        options_menu.add_command(label="Overall", command=self.display_overall)
        options_menu.add_command(label="CPU", command=self.display_cpu)
        options_menu.add_command(label="Memory", command=self.display_memory)
        options_menu.add_command(label="Network", command=self.display_network)
        options_menu.add_command(label="Process", command=self.display_process)
        options_menu.add_command(label="Disk", command=self.display_disk)
        options_menu.add_command(label="Temperature", command=self.display_temperature)
        options_menu.add_command(label="Battery", command=self.display_battery)
#-----------------------------------------------------------------------------------------------------------------------------------      
        self.index = itertools.count()
        self.current_page = None
        self.cpu_ani = None
        self.memory_ani = None
        self.network_ani = None
        self.process_ani = None
        self.disk_ani = None
        self.temperature_ani = None
        self.battery_ani = None
#-----------------------------------------------------------------------------------------------------------------------------------
        self.fig_cpu, self.ax_cpu = plt.subplots()
        self.fig_memory, self.ax_memory = plt.subplots()
        self.fig_network, self.ax_network = plt.subplots()
        self.fig_process, self.ax_process = plt.subplots()
        self.fig_disk, self.ax_disk = plt.subplots()
        self.fig_temperature, self.ax_temperature = plt.subplots()
        self.fig_battery, self.ax_battery = plt.subplots()
#-----------------------------------------------------------------------------------------------------------------------------------
        self.cpu_x_vals = []
        self.cpu_y_vals = []
        self.memory_x_vals = []
        self.memory_y_vals = []
        self.network_x_vals = []
        self.network_y_vals1 = []
        self.network_y_vals2 = []
        self.process_x_vals = []
        self.process_y_vals = []
        self.disk_x_vals = []
        self.disk_y_vals = []
        self.temperature_x_vals = []
        self.temperature_y_vals = []
        self.battery_x_vals = []
        self.battery_y_vals = []
#-----------------------------------------------------------------------------------------------------------------------------------
        self.display_overall()
        self.window.mainloop()
#-----------------------------------------------------------------------------------------------------------------------------------
    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def set_header(self, header_text):
        if self.current_page:
            self.current_page.destroy()
        self.current_page = Label(self.frame, text=header_text, font=("Helvetica", 24))
        self.current_page.pack(side=tk.TOP)

    def animate_cpu(self, i):
        self.cpu_x_vals.append(next(self.index))
        self.cpu_y_vals.append(psutil.cpu_percent())
        self.ax_cpu.clear()
        self.ax_cpu.plot(self.cpu_x_vals, self.cpu_y_vals)
        self.ax_cpu.set_xlabel("Time (s)")
        self.ax_cpu.set_ylabel("CPU Usage (%)")
        current_cpu_usage = psutil.cpu_percent()
        self.cpu_info_label.config(text=f"Current CPU usage = {current_cpu_usage}%")

    def animate_memory(self, i):
        self.memory_x_vals.append(next(self.index))
        self.memory_y_vals.append(psutil.virtual_memory().percent)
        self.ax_memory.clear()
        self.ax_memory.plot(self.memory_x_vals, self.memory_y_vals)
        self.ax_memory.set_xlabel("Time (s)")
        self.ax_memory.set_ylabel("Memory Usage (%)")

    def animate_network(self, i):
        self.network_x_vals.append(next(self.index))
        self.network_y_vals1.append(psutil.net_io_counters().bytes_sent)
        self.network_y_vals2.append(psutil.net_io_counters().bytes_recv)
        self.ax_network.clear()
        self.ax_network.plot(self.network_x_vals, self.network_y_vals1, label="Bytes sent")
        self.ax_network.plot(self.network_x_vals, self.network_y_vals2, label="Bytes received")
        self.ax_network.set_xlabel("Time (s)")
        self.ax_network.set_ylabel("Bytes count (Kb)")
        self.ax_network.legend(loc = "upper right")


    def animate_process(self, i):
        self.process_x_vals.append(next(self.index))
        self.process_y_vals.append(len(psutil.pids()))
        self.ax_process.clear()
        self.ax_process.plot(self.process_x_vals, self.process_y_vals)
        self.ax_process.set_xlabel("Time (s)")
        self.ax_process.set_ylabel("Number of Processes")

    def animate_disk(self, i):
        self.disk_x_vals.append(next(self.index))
        self.disk_y_vals.append(psutil.disk_usage('/').percent)
        self.ax_disk.clear()
        self.ax_disk.plot(self.disk_x_vals, self.disk_y_vals)
        self.ax_disk.set_xlabel("Time (s)")
        self.ax_disk.set_ylabel("Disk Usage (%)")
#-----------------------------------------------------------------------------------------------------------------------------------
    def display_overall(self):
        self.clear_frame()
        self.set_header("Overall")
        Label(self.frame, text="Overall Page Content").pack()

    def display_cpu(self):
        self.clear_frame()
        self.set_header("CPU Usage")
        index = itertools.count()
        self.cpu_ani = FuncAnimation(self.fig_cpu, self.animate_cpu, frames=index, interval=1000)
        canvas_cpu = FigureCanvasTkAgg(self.fig_cpu, master=self.frame)
        canvas_widget_cpu = canvas_cpu.get_tk_widget()
        canvas_widget_cpu.pack()
        self.cpu_info_label = Label(self.frame, text="", font = (hasattr, 18))
        self.cpu_info_label.pack()

    def display_memory(self):
        self.clear_frame()
        self.set_header("Memory Usage")
        index = itertools.count()
        self.memory_ani = FuncAnimation(self.fig_memory, self.animate_memory, frames=index, interval=1000)
        canvas_memory = FigureCanvasTkAgg(self.fig_memory, master=self.frame)
        canvas_widget_memory = canvas_memory.get_tk_widget()
        canvas_widget_memory.pack()

    def display_network(self):
        self.clear_frame()
        self.set_header("Network")
        index = itertools.count()
        self.network_ani = FuncAnimation(self.fig_network, self.animate_network, frames = index, interval = 1000)
        canvas_network = FigureCanvasTkAgg(self.fig_network, master=self.frame)
        canvas_widgit_memory = canvas_network.get_tk_widget()
        canvas_widgit_memory.pack()

    def display_process(self):
        self.clear_frame()
        self.set_header("Process")
        Label(self.frame, text="Process Page Content").pack()

    def display_disk(self):
        self.clear_frame()
        self.set_header("Disk Usage")
        index = itertools.count()
        self.disk_ani = FuncAnimation(self.fig_disk, self.animate_disk, frames=index, interval=1000)
        canvas_disk= FigureCanvasTkAgg(self.fig_disk, master=self.frame)
        canvas_widget_disk = canvas_disk.get_tk_widget()
        canvas_widget_disk.pack()

    def display_temperature(self):
        self.clear_frame()
        self.set_header("Temperature")
        Label(self.frame, text="Temperature Page Content").pack()

    def display_battery(self):
        self.clear_frame()
        self.set_header("Battery")
        Label(self.frame, text="Battery Page Content").pack()
#-----------------------------------------------------------------------------------------------------------------------------------
System()
