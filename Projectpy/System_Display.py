import tkinter as tk
from tkinter import Menu, Label
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import itertools
import psutil
from psutil import disk_partitions, disk_usage
from tabulate import tabulate

class System:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("System status display")
        
        self.frame = tk.Frame(self.window, width=1200, height=700)
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
        self.data = disk_partitions(all = False)
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

    def gigabytes_convert(self, byte):
        one_gb = 1073741824
        giga = byte / one_gb
        giga = "{0:.1f}".format(giga)
        return giga
    
    def megabytes_convert(self, byte):
        one_mb = 1048576
        mega = byte/ one_mb
        mega = "{0:.2f}".format(mega)
        return mega

    def details(self,device_name):
        for i in self.data:
            if i.device == device_name:
                return i
            
    def get_device_name(self):
        return [i.device for i in self.data]
    
    def disk_info(self,device_name):
        disk_info = {}
        try:
            usage = disk_usage(device_name)
            disk_info["Device"] = device_name
            disk_info["Total"] = f"{self.gigabytes_convert(usage.used + usage.free)} GB"
            disk_info["Used"] = f"{self.gigabytes_convert(usage.used)} GB"
            disk_info["Free"] = f"{self.gigabytes_convert(usage.free)} GB"
            disk_info["Percent"] = f"{usage.percent} GB"
        except PermissionError:
            pass
        except FileNotFoundError:
            pass
        info = self.details(device_name)
        disk_info.update({"Device":info.device})
        disk_info["Mount Point"] = info.mountpoint
        disk_info["FS-Type"] = info.fstype
        disk_info["Opts"] = info.opts
        return disk_info
    
    def all_disk_info(self):
        return_all = []
        for i in self.get_device_name():
            return_all.append(self.disk_info(i))
        return return_all
    
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
        self.cpu_info_label.config(text=f"Current CPU usage = {self.cpu_y_vals[-1]}%")

    def animate_memory(self, i):
        self.memory_x_vals.append(next(self.index))
        self.memory_y_vals.append(psutil.virtual_memory().percent)
        self.ax_memory.clear()
        self.ax_memory.plot(self.memory_x_vals, self.memory_y_vals)
        self.ax_memory.set_xlabel("Time (s)")
        self.ax_memory.set_ylabel("Memory Usage (%)")
        self.memory_info_label.config(text=f"Ram Usage = {self.gigabytes_convert(psutil.virtual_memory().used)} GB / {self.gigabytes_convert(psutil.virtual_memory().total)} GB ({psutil.virtual_memory().percent}%)")

    def animate_network(self, i):
        self.network_x_vals.append(next(self.index))
        self.network_y_vals1.append(psutil.net_io_counters().bytes_sent)
        self.network_y_vals2.append(psutil.net_io_counters().bytes_recv)
        self.ax_network.clear()
        self.ax_network.plot(self.network_x_vals, self.network_y_vals1, label="Bytes sent")
        self.ax_network.plot(self.network_x_vals, self.network_y_vals2, label="Bytes received")
        self.ax_network.set_xlabel("Time (s)")
        self.ax_network.set_ylabel("Bytes counts")
        self.ax_network.legend(loc = "upper right")
        sent = psutil.net_io_counters().bytes_sent
        rec = psutil.net_io_counters().bytes_recv
        if sent > 1073741824/10 and rec >1073741824/10:
            self.network_info_label.config(text = f" Bytes sent = {sent} Bytes ({self.gigabytes_convert(sent)} GB)\nBytes received = {rec} Bytes ({self.gigabytes_convert(rec)} GB)")
        elif sent > 1048576/10 and rec > 1048576/10:
             self.network_info_label.config(text = f" Bytes sent = {sent} Bytes ({self.megabytes_convert(sent)} MB)\nBytes received = {rec} Bytes ({self.megabytes_convert(rec)} MB)")




    def animate_process(self, i):
        self.process_x_vals.append(next(self.index))
        self.process_y_vals.append(len(psutil.pids()))
        self.ax_process.clear()
        self.ax_process.plot(self.process_x_vals, self.process_y_vals)
        self.ax_process.set_xlabel("Time (s)")
        self.ax_process.set_ylabel("Number of Processes")


    def animate_disk(self, i):
        self.disk_x_vals.append(next(self.index))
        device_names = self.get_device_name()

        while len(self.disk_y_vals) < len(device_names):
            self.disk_y_vals.append([])

        for i, name in enumerate(device_names):
            try:
                usage = disk_usage(name).percent
                self.disk_y_vals[i].append(usage)
            except (PermissionError, FileNotFoundError):
                self.disk_y_vals[i].append(None)

        self.ax_disk.clear() 
        self.ax_disk.set_xlabel("Time (s)")
        self.ax_disk.set_ylabel("Disk Usage (%)")

       
        for i, name in enumerate(device_names):
            self.ax_disk.plot(self.disk_x_vals, self.disk_y_vals[i], label=name)

        self.ax_disk.legend(loc='upper left')  

      
        disk_info = self.all_disk_info()
        
       
        for info in disk_info:
            info['Device'] = f" {info['Device']}"
            info['Total'] = f" {info['Total']}"
            info['Used'] = f" {info['Used']}"
            info['Free'] = f" {info['Free']}"
            info['Percent'] = f" {info['Percent']}"

        disk_info_text = tabulate(
            disk_info,
            headers="keys",
            tablefmt="grid",
            showindex=False,
            numalign="center",
            stralign="left",   
            colalign=("center",) * len(disk_info[0].keys()),
        )

        self.disk_info_label.config(text=disk_info_text, font=("Helvetica", 10))
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
        self.memory_info_label = Label(self.frame, text="", font = (hasattr, 18) )
        self.memory_info_label.pack()

    def display_network(self):
        self.clear_frame()
        self.set_header("Network")
        index = itertools.count()
        self.network_ani = FuncAnimation(self.fig_network, self.animate_network, frames = index, interval = 1000)
        canvas_network = FigureCanvasTkAgg(self.fig_network, master=self.frame)
        canvas_widgit_memory = canvas_network.get_tk_widget()
        canvas_widgit_memory.pack()
        self.network_info_label = Label(self.frame, text ="", font = (hasattr, 18))
        self.network_info_label.pack()

    def display_process(self):
        self.clear_frame()
        self.set_header("Process")
        Label(self.frame, text="Process Page Content").pack()

    def display_disk(self):
        self.clear_frame()
        self.set_header("Disk Usage")
        
        index = itertools.count()
        self.disk_ani = FuncAnimation(self.fig_disk, self.animate_disk, frames=index, interval=1000)
        canvas_disk = FigureCanvasTkAgg(self.fig_disk, master=self.frame)
        canvas_widget_disk = canvas_disk.get_tk_widget()
        canvas_widget_disk.pack()
        
        self.disk_info_label = Label(self.frame, text="", font=("Helvetica", 12))
        self.disk_info_label.pack()

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


import tkinter as tk
from tkinter import Menu, Label
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import itertools
import psutil
from tabulate import tabulate

class SystemDisplayBase:
    def __init__(self, window, frame, title):
        self.window = window
        self.frame = frame
        self.fig, self.ax = plt.subplots()
        self.title = title
        self.index = itertools.count()
        self.ani = None

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def set_header(self, title = ""):
        self.clear_frame()
        Label(self.frame, text=title, font=("Helvetica", 24)).pack()

    def animate(self, i):
        pass

    def display(self):
        pass


class CPUDisplay(SystemDisplayBase):
    def __init__(self, window, frame):
        super().__init__(window, frame, "CPU Usage")
        self.cpu_info_label = Label(self.frame, text="", font=("Helvetica", 18))
        self.cpu_info_label.pack()
        self.cpu_x_vals = []
        self.cpu_y_vals = []

    def animate(self, i):
        self.cpu_x_vals.append(next(self.index))
        self.cpu_y_vals.append(psutil.cpu_percent())
        self.ax.clear()
        self.ax.plot(self.cpu_x_vals, self.cpu_y_vals)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("CPU Usage (%)")
        self.cpu_info_label.config(text=f"Current CPU usage = {self.cpu_y_vals[-1]}%")

        canvas_widget = FigureCanvasTkAgg(self.fig, master=self.frame)
        canvas_widget.get_tk_widget().pack()
        canvas_widget.draw_idle()

    def display(self):
        super().display()
        self.clear_frame()
        self.set_header("CPU Usage")
        self.ani = FuncAnimation(self.fig, self.animate, frames=100, interval=1000)
        canvas_cpu = FigureCanvasTkAgg(self.fig, master=self.frame)
        canvas_widget_cpu = canvas_cpu.get_tk_widget()
        canvas_widget_cpu.pack()


class MemoryDisplay(SystemDisplayBase):
    def __init__(self, window, frame, fig):
        super().__init__(window, frame,"Memory Usage")
        self.memory_info_label = Label(self.frame, text="", font=("Helvetica", 18))
        self.memory_info_label.pack()

    def animate(self, i):
        self.memory_x_vals.append(next(self.index))
        self.memory_y_vals.append(psutil.virtual_memory().percent)
        self.ax.clear()
        self.ax.plot(self.memory_x_vals, self.memory_y_vals)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Memory Usage (%)")
        self.memory_info_label.config(text=f"Ram Usage = {self.gigabytes_convert(psutil.virtual_memory().used)} GB / {self.gigabytes_convert(psutil.virtual_memory().total)} GB ({psutil.virtual_memory().percent}%)")

    def display(self):
        super().display()
        self.clear_frame()
        self.set_header("Memory Usage")
        index = itertools.count()
        self.ani = FuncAnimation(self.fig_memory, self.animate_memory, frames=index, interval=1000)
        canvas_memory = FigureCanvasTkAgg(self.fig_memory, master=self.frame)
        canvas_widget_memory = canvas_memory.get_tk_widget()
        canvas_widget_memory.pack()
        self.memory_info_label = Label(self.frame, text="", font = (hasattr, 18) )
        self.memory_info_label.pack()

class NetworkDisplay(SystemDisplayBase):
    def __init__(self, window, frame, fig):
        super().__init__(window, frame,"Network")
        self.network_info_label = Label(self.frame, text="", font=("Helvetica", 18))
        self.network_info_label.pack()

    def animate(self, i):
        self.network_x_vals.append(next(self.index))
        self.network_y_vals1.append(psutil.net_io_counters().bytes_sent)
        self.network_y_vals2.append(psutil.net_io_counters().bytes_recv)
        self.ax.clear()
        self.ax.plot(self.network_x_vals, self.network_y_vals1, label="Bytes sent")
        self.ax.plot(self.network_x_vals, self.network_y_vals2, label="Bytes received")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Bytes counts")
        self.ax.legend(loc = "upper right")
        sent = psutil.net_io_counters().bytes_sent
        rec = psutil.net_io_counters().bytes_recv
        if sent > 1073741824/10 and rec >1073741824/10:
            self.network_info_label.config(text = f" Bytes sent = {sent} Bytes ({self.gigabytes_convert(sent)} GB)\nBytes received = {rec} Bytes ({self.gigabytes_convert(rec)} GB)")
        elif sent > 1048576/10 and rec > 1048576/10:
             self.network_info_label.config(text = f" Bytes sent = {sent} Bytes ({self.megabytes_convert(sent)} MB)\nBytes received = {rec} Bytes ({self.megabytes_convert(rec)} MB)")

    def display(self):
        super().display()
        self.clear_frame()
        self.set_header("Network")
        index = itertools.count()
        self.ani = FuncAnimation(self.fig_network, self.animate_network, frames = index, interval = 1000)
        canvas_network = FigureCanvasTkAgg(self.fig_network, master=self.frame)
        canvas_widgit_memory = canvas_network.get_tk_widget()
        canvas_widgit_memory.pack()
        self.network_info_label = Label(self.frame, text ="", font = (hasattr, 18))
        self.network_info_label.pack()

class DiskDisplay(SystemDisplayBase):
    def __init__(self, window, frame, fig):
        super().__init__(window, frame,"Disk Usage")
        self.disk_info_label = Label(self.frame, text="", font=("Helvetica", 12))
        self.disk_info_label.pack()

    def animate(self, i):
        self.disk_x_vals.append(next(self.index))
        device_names = self.get_device_name()

        while len(self.disk_y_vals) < len(device_names):
            self.disk_y_vals.append([])

        for i, name in enumerate(device_names):
            try:
                usage = disk_usage(name).percent
                self.disk_y_vals[i].append(usage)
            except (PermissionError, FileNotFoundError):
                self.disk_y_vals[i].append(None)

        self.ax.clear() 
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Disk Usage (%)")

       
        for i, name in enumerate(device_names):
            self.ax.plot(self.disk_x_vals, self.disk_y_vals[i], label=name)

        self.ax.legend(loc='upper left')  

      
        disk_info = self.all_disk_info()
        
       
        for info in disk_info:
            info['Device'] = f" {info['Device']}"
            info['Total'] = f" {info['Total']}"
            info['Used'] = f" {info['Used']}"
            info['Free'] = f" {info['Free']}"
            info['Percent'] = f" {info['Percent']}"

        disk_info_text = tabulate(
            disk_info,
            headers="keys",
            tablefmt="grid",
            showindex=False,
            numalign="center",
            stralign="left",   
            colalign=("center",) * len(disk_info[0].keys()),
        )

        self.disk_info_label.config(text=disk_info_text, font=("Helvetica", 10))

    def display(self):
        super().display()
        self.clear_frame()
        self.set_header("Disk Usage")
        
        index = itertools.count()
        self.ani = FuncAnimation(self.fig_disk, self.animate_disk, frames=index, interval=1000)
        canvas_disk = FigureCanvasTkAgg(self.fig_disk, master=self.frame)
        canvas_widget_disk = canvas_disk.get_tk_widget()
        canvas_widget_disk.pack()
        
        self.disk_info_label = Label(self.frame, text="", font=("Helvetica", 12))
        self.disk_info_label.pack()

class System:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("System status display")

        self.frame = tk.Frame(self.window, width=1200, height=700)
        self.frame.pack()

        menubar = Menu(self.window)
        self.window.config(menu=menubar)

        options_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=options_menu)

        self.display_types = {
            "Overall": SystemDisplayBase(self.window, self.frame, "Overall"),
            "CPU": CPUDisplay(self.window, self.frame),
            "Memory": MemoryDisplay(self.window, self.frame, plt.subplots()),
            "Network": NetworkDisplay(self.window, self.frame, plt.subplots()),
            "Disk": DiskDisplay(self.window, self.frame, plt.subplots()),
        }

        for label, display in self.display_types.items():
            options_menu.add_command(label=label, command=display.display)

        self.display_overall()
        self.window.mainloop()

    def display_overall(self):
        self.display_types["Overall"].display()

System()
