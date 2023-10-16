import tkinter as tk
from tkinter import Menu, Label, Canvas, Scrollbar, ttk
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import itertools
import psutil
from psutil import disk_partitions, disk_usage
from tabulate import tabulate
import psutil
import pandas as pd
import wmi
import re




plt.style.use('dark_background')
#-----------------------------------------------------------------------------------------------------------------------------------
#BASE CLASS
class SystemDisplayBase:
    def __init__(self, window, frame, title):
        self.window = window
        self.frame = frame
        self.fig, self.ax = plt.subplots()
        self.title = title
        self.index = itertools.count()
        self.ani = None
        self.pc = wmi.WMI()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def set_header(self, title = ""):
        self.clear_frame()
        Label(self.frame, text=title, font=("Tahoma", 24) ,bg="Black", fg= "Green").pack()

    def animate(self, i):
        pass

    def display(self):
        pass

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

#-----------------------------------------------------------------------------------------------------------------------------------

class OverallDisplay(SystemDisplayBase):
    def __init__(self, window, frame, fig):
        super().__init__(window, frame, "Overall Usage")
        self.cpu_x_vals = []
        self.cpu_y_vals = []

        self.memory_x_vals = []
        self.memory_y_vals = []

        self.network_x_vals = []
        self.network_y_vals1 = []
        self.network_y_vals2 = []

        self.disk_x_vals = []
        self.disk_y_vals = []

    def create_subplots(self):
        # Create a single large subplot for the overall display
        self.fig.set_size_inches(10, 5)  # Increase the figure size

        # Use gridspec_kw to control the layout and spacing
        gs = self.fig.add_gridspec(2, 2, wspace=0.3, hspace=0.3)  # Adjust spacing as needed

        # Create a 2x2 grid layout within the large subplot
        self.ax1 = self.fig.add_subplot(gs[0, 0])  # Top-left
        self.ax2 = self.fig.add_subplot(gs[0, 1])  # Top-right
        self.ax3 = self.fig.add_subplot(gs[1, 0])  # Bottom-left
        self.ax4 = self.fig.add_subplot(gs[1, 1])  # Bottom-right

    def animate(self, i):
        # Update CPU graph
        self.cpu_x_vals.append(next(self.index))
        self.cpu_y_vals.append(psutil.cpu_percent())
        self.ax1.clear()
        self.ax1.plot(self.cpu_x_vals, self.cpu_y_vals, label="CPU Usage", color="red")

        # Update Memory graph
        self.memory_x_vals.append(next(self.index))
        self.memory_y_vals.append(psutil.virtual_memory().percent)
        self.ax2.clear()
        self.ax2.plot(self.memory_x_vals, self.memory_y_vals, label="Memory Usage", color="blue")

        # Update Network graph
        self.network_x_vals.append(next(self.index))
        self.network_y_vals1.append(psutil.net_io_counters().bytes_sent)
        self.network_y_vals2.append(psutil.net_io_counters().bytes_recv)
        self.ax3.clear()
        self.ax3.plot(self.network_x_vals, self.network_y_vals1, label="Bytes sent", color="green")
        self.ax3.plot(self.network_x_vals, self.network_y_vals2, label="Bytes received", color="orange")

        # Update Disk graph
        self.disk_x_vals.append(next(self.index))
        disk_usage = psutil.disk_usage('/')
        self.disk_y_vals.append(disk_usage.percent)
        self.ax4.clear()
        self.ax4.plot(self.disk_x_vals, self.disk_y_vals, label="Disk Usage", color="purple")

        # Update CPU and Memory info labels
        cpu_info = f"- CPU Name -\n\t{self.pc.Win32_Processor()[0].name}\nCurrent CPU usage = {self.cpu_y_vals[-1]}%"
        memory_info = f"Ram Usage = {self.gigabytes_convert(psutil.virtual_memory().used)} GB / {self.gigabytes_convert(psutil.virtual_memory().total)} GB ({psutil.virtual_memory().percent}%)"

        # Update network info label
        sent = psutil.net_io_counters().bytes_sent
        rec = psutil.net_io_counters().bytes_recv
        network_info = f"Bytes sent = {sent} Bytes ({self.gigabytes_convert(sent)} GB)\nBytes received = {rec} Bytes ({self.gigabytes_convert(rec)} GB)"

        # Update disk info label
        disk_info = f"Disk Usage = {disk_usage.percent}%"

        self.cpu_info_label.config(text=cpu_info)
        self.memory_info_label.config(text=memory_info)
        self.network_info_label.config(text=network_info)
        self.disk_info_label.config(text=disk_info)

    def display(self):
        super().display()
        self.clear_frame()
        self.set_header("Overall Usage")
        self.create_subplots()
        index = itertools.count()
        self.ani = FuncAnimation(self.fig, self.animate, frames=index, interval=1000)
        canvas_overall = FigureCanvasTkAgg(self.fig, master=self.frame)
        canvas_widget_overall = canvas_overall.get_tk_widget()
        canvas_widget_overall.pack()
        self.cpu_info_label = Label(self.frame, text="", font=("Tahoma", 18), bg="Black", fg="Green")
        self.cpu_info_label.pack()
        self.memory_info_label = Label(self.frame, text="", font=("Tahoma", 18), bg="Black", fg="Green")
        self.memory_info_label.pack()
        self.network_info_label = Label(self.frame, text="", font=("Tahoma", 18), bg="Black", fg="Green")
        self.network_info_label.pack()
        self.disk_info_label = Label(self.frame, text="", font=("Tahoma", 18), bg="Black", fg="Green")
        self.disk_info_label.pack()


class CPUDisplay(SystemDisplayBase):
    def __init__(self, window, frame):
        super().__init__(window, frame, "CPU Usage")
        self.cpu_info_label = Label(self.frame, text="", font=("Tahoma", 18) ,bg="Black", fg= "Green")
        self.cpu_info_label.pack()
        self.cpu_x_vals = []
        self.cpu_y_vals = []

    def animate(self, i):
        self.cpu_x_vals.append(next(self.index))
        self.cpu_y_vals.append(psutil.cpu_percent())
        self.ax.clear()
        self.ax.plot(self.cpu_x_vals, self.cpu_y_vals,color= "red")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("CPU Usage (%)")
        self.cpu_info_label.config(text=f"- CPU Name -\n\t{self.pc.Win32_Processor()[0].name}\nCurrent CPU usage = {self.cpu_y_vals[-1]}%")

    def display(self):
        self.clear_frame()
        self.set_header("CPU Usage")
        self.ani = FuncAnimation(self.fig, self.animate, frames=100, interval=1000)
        canvas_cpu = FigureCanvasTkAgg(self.fig, master=self.frame)
        canvas_widget_cpu = canvas_cpu.get_tk_widget()
        canvas_widget_cpu.pack()
        self.cpu_info_label = Label(self.frame, text="", font = (hasattr, 18), bg="Black", fg= "Green")
        self.cpu_info_label.pack()

#-----------------------------------------------------------------------------------------------------------------------------------

class MemoryDisplay(SystemDisplayBase):
    def __init__(self, window, frame, fig):
        super().__init__(window, frame,"Memory Usage")
        self.memory_info_label = Label(self.frame, text="", font=("Tahoma", 18),bg="Black", fg= "Green")
        self.memory_info_label.pack()
        self.memory_x_vals = []
        self.memory_y_vals = []
        

    def animate(self, i):
        self.memory_x_vals.append(next(self.index))
        self.memory_y_vals.append(psutil.virtual_memory().percent)
        self.ax.clear()
        self.ax.plot(self.memory_x_vals, self.memory_y_vals,color= "red")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Memory Usage (%)")
        self.memory_info_label.config(text=f"GPU Name = {self.pc.Win32_VideoController()[0].name}\nRam Usage = {self.gigabytes_convert(psutil.virtual_memory().used)} GB / {self.gigabytes_convert(psutil.virtual_memory().total)} GB ({psutil.virtual_memory().percent}%)")


    def display(self):
        self.clear_frame()
        self.set_header("Memory Usage")
        self.ani = FuncAnimation(self.fig, self.animate, frames=100, interval=1000)
        canvas_mem = FigureCanvasTkAgg(self.fig, master=self.frame)
        canvas_widget_mem = canvas_mem.get_tk_widget()
        canvas_widget_mem.pack()
        self.memory_info_label = Label(self.frame, text="", font = (hasattr, 18),bg="Black", fg= "Green" )
        self.memory_info_label.pack()

#-----------------------------------------------------------------------------------------------------------------------------------

class NetworkDisplay(SystemDisplayBase):
    def __init__(self, window, frame, fig):
        super().__init__(window, frame,"Network")
        self.network_info_label = Label(self.frame, text="", font=("Tahoma", 18),bg="Black", fg= "Green")
        self.network_info_label.pack()
        self.network_x_vals = []
        self.network_y_vals1 = []
        self.network_y_vals2 = []

    def animate(self, i):
        self.network_x_vals.append(next(self.index))
        self.network_y_vals1.append(psutil.net_io_counters().bytes_sent)
        self.network_y_vals2.append(psutil.net_io_counters().bytes_recv)
        self.ax.clear()
        self.ax.plot(self.network_x_vals, self.network_y_vals1, label="Bytes sent",color= "red")
        self.ax.plot(self.network_x_vals, self.network_y_vals2, label="Bytes received", color = "Blue")
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
        self.ani = FuncAnimation(self.fig, self.animate, frames = index, interval = 1000)
        canvas_network = FigureCanvasTkAgg(self.fig, master=self.frame)
        canvas_widgit_memory = canvas_network.get_tk_widget()
        canvas_widgit_memory.pack()
        self.network_info_label = Label(self.frame, text ="", font = (hasattr, 18),bg="Black", fg= "Green")
        self.network_info_label.pack()

#-----------------------------------------------------------------------------------------------------------------------------------

class DiskDisplay(SystemDisplayBase):
    def __init__(self, window, frame, fig):
        super().__init__(window, frame,"Disk Usage")
        self.disk_info_label = Label(self.frame, text="", font=("Tahoma", 12),bg="Black", fg= "Green")
        self.disk_info_label.pack()
        self.disk_x_vals = []
        self.disk_y_vals = []
        self.data = disk_partitions(all = False)

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
            self.ax.plot(self.disk_x_vals, self.disk_y_vals[i], label=name,color= "Red")

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

        self.disk_info_label.config(text=disk_info_text, font=("Tahoma", 10),bg="Black", fg= "Green")

    def display(self):
        super().display()
        self.clear_frame()
        self.set_header("Disk Usage")
        
        index = itertools.count()
        self.ani = FuncAnimation(self.fig, self.animate, frames=index, interval=1000)
        canvas_disk = FigureCanvasTkAgg(self.fig, master=self.frame)
        canvas_widget_disk = canvas_disk.get_tk_widget()
        canvas_widget_disk.pack()
        
        self.disk_info_label = Label(self.frame, text="", font=("Tahoma", 12),bg="Black", fg= "Green")
        self.disk_info_label.pack()


#-----------------------------------------------------------------------------------------------------------------------------------

class ProcessDisplay(SystemDisplayBase):
    def __init__(self, window, frame):
        super().__init__(window, frame, "Process Monitor")
        self.process_table_label = Label(self.frame, text="", font=("Tahoma", 12),bg="Black", fg= "Green")
        self.process_table_label.pack()
        self.process_x_vals = []
        self.process_y_vals = []
        self.selected_process_pid = None  # Store the PID of the selected process

        self.fig, self.ax = plt.subplots()

    def animate(self, i):
            self.process_x_vals.append(next(self.index))

            # Check if a process is selected
            if self.selected_process_pid is not None:
                # Fetch memory usage for the selected process
                selected_process = psutil.Process(self.selected_process_pid)
                memory_percent = selected_process.memory_percent()
                self.process_y_vals.append(memory_percent)
                selected_process = psutil.Process(self.selected_process_pid)
                selected_process_name = selected_process.name()
                selected_process_memory_usage = selected_process.memory_percent()
                selected_process_info = f"Overall memory usage : {psutil.virtual_memory().percent}%\n\nSelected Process: {selected_process_name}\n\nMemory Usage: {selected_process_memory_usage:.2f}% / {psutil.virtual_memory().percent}%"

                # Create a label to display the selected process info
                self.process_table_label.config(text=selected_process_info, font=("Tahoma", 15),bg="Black", fg= "Green")
                self.process_table_label.pack()
            else:
                # Display overall memory usage if no process is selected
                memory_percent = psutil.virtual_memory().percent
                self.process_y_vals.append(memory_percent)
                self.process_table_label.config(text=f"Overall memory usage : {memory_percent}% ", font=("Tahoma", 15),bg="Black", fg= "Green")
                self.process_table_label.pack()

            # Update the graph
            self.ax.clear()
            self.ax.plot(self.process_x_vals, self.process_y_vals,color= "red")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Memory Usage (%)")
        
    def display(self):
        super().display()
        self.clear_frame()
        self.set_header("Process Monitor")

        index = itertools.count()
        self.ani = FuncAnimation(self.fig, self.animate, frames=index, interval=1000)
        canvas_process = FigureCanvasTkAgg(self.fig, master=self.frame)
        canvas_widget_process = canvas_process.get_tk_widget()
        canvas_widget_process.pack()
        self.process_table_label = Label(self.frame, text="", font=("Tahoma", 12),bg="Black", fg= "Green")
        process_treeview = self.create_process_treeview(self.frame, self.get_top_memory_processes())
        process_treeview.bind("<Double-1>", self.on_process_row_double_click)

    def create_process_treeview(self, frame, process_data):
        # Create a frame to hold the Treeview and the scrollbar
        table_frame = tk.Frame(frame)
        table_frame.pack(side=tk.LEFT, padx=10, pady=10)  # Adjust padding as needed

        # Create the Treeview widget inside the table frame
        treeview = ttk.Treeview(table_frame, columns=("PID", "Name", "Status"), show="headings")
        treeview.heading("PID", text="PID")
        treeview.heading("Name", text="Name")
        treeview.heading("Status", text="Status")

        for data in process_data:
            treeview.insert("", "end", values=data)

        treeview.pack(side=tk.LEFT)  # Pack the Treeview to the left within the table frame

        # Add a vertical scrollbar to the right of the table frame
        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=treeview.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the Treeview to use the scrollbar
        treeview.configure(yscrollcommand=y_scrollbar.set)

        return treeview
    
    def display_process_graph(self):
        self.process_x_vals = []
        self.process_y_vals = []

        self.clear_frame()
        self.set_header("Process Monitor")

        index = itertools.count()
        self.ani = FuncAnimation(self.fig, self.animate, frames=index, interval=1000)  # Update every 2 seconds
        canvas_process = FigureCanvasTkAgg(self.fig, master=self.frame)
        canvas_widget_process = canvas_process.get_tk_widget()
        canvas_widget_process.pack()
        self.process_table_label = Label(self.frame, text="", font=("Tahoma", 12),bg="Black", fg= "Green")
        self.process_table_label.pack()

        # Bind a double-click event to the process table to select a process
        process_treeview = self.create_process_treeview(self.frame, self.get_top_memory_processes())
        process_treeview.bind("<Double-1>", self.on_process_row_double_click)

        # Display selected process name and memory usage
        self.process_table_label = Label(self.frame, text ="", font = (hasattr, 18),bg="Black", fg= "Green")
        self.process_table_label.pack()

    def on_process_row_double_click(self, event):
        item = event.widget.selection()[0]
        process_pid_str = event.widget.item(item, "values")[0]

        # Use regular expressions to extract the numeric part
        process_pid_match = re.search(r'(\d+)', process_pid_str)
        if process_pid_match:
            process_pid = int(process_pid_match.group(1))
            self.select_process(process_pid)

    def clear_graph_data(self):
        self.process_x_vals = []
        self.process_y_vals = []

    def select_process(self, process_pid):
        self.selected_process_pid = process_pid
        self.clear_graph_data()
        self.display_process_graph()

    def get_top_memory_processes(self):
        processes = list(psutil.process_iter(attrs=['pid', 'name', 'memory_percent']))
        return sorted(processes, key=lambda x: x.info['memory_percent'], reverse=True)

#-----------------------------------------------------------------------------------------------------------------------------------

class TemperatureDisplay(SystemDisplayBase):
    def __init__(self, window, frame, fig):
        super().__init__(window, frame, "Temperature")
        self.temperature_info_label = Label(self.frame, text="", font=("Tahoma", 18),bg="Black", fg= "Green")
        self.temperature_info_label.pack()
        self.temperature_x_vals = []
        self.temperature_y_vals = []

    def animate(self, i):
        self.temperature_x_vals.append(next(self.index))
        try:
            temperatures = psutil.sensors_temperatures()

            if 'coretemp' in temperatures:
                core_temp = temperatures['coretemp']
                if core_temp:
                    temperature = core_temp[0].current
                    self.temperature_y_vals.append(temperature)
                    self.ax.clear()
                    self.ax.plot(self.temperature_x_vals, self.temperature_y_vals,color= "red")
                    self.ax.set_xlabel("Time (s)")
                    self.ax.set_ylabel("Temperature (°C)")
                    self.temperature_info_label.config(text=f"CPU Temperature = {temperature}°C")
                else:
                    self.handle_sensor_data_unavailable()
            else:
                self.handle_sensor_data_unavailable()
        except Exception as e:
            self.handle_sensor_data_unavailable()

    def handle_sensor_data_unavailable(self):
        self.ax.clear()
        self.temperature_info_label.config(text="No CPU temperature data available on this platform\nNote: The program is using psutil.sensors_temperatures() \nwhich might not work on some platform like window.")
        self.ax.axis('off')

    def display(self):
        super().display()
        self.clear_frame()
        self.set_header("Temperature")
        index = itertools.count()
        self.ani = FuncAnimation(self.fig, self.animate, frames=index, interval=1000)
        canvas_temp = FigureCanvasTkAgg(self.fig, master=self.frame)
        canvas_widget_temp = canvas_temp.get_tk_widget()
        canvas_widget_temp.pack()
        self.temperature_info_label = Label(self.frame, text="", font=("Tahoma", 18),bg="Black", fg= "Green")
        self.temperature_info_label.pack()


#-----------------------------------------------------------------------------------------------------------------------------------
class BatteryDisplay(SystemDisplayBase):
    def __init__(self, window, frame, fig):
        super().__init__(window, frame, "Battery Status")
        self.battery_info_label = Label(self.frame, text="", font=("Tahoma", 18),bg="Black", fg= "Green")
        self.battery_info_label.pack()
        self.battery_x_vals = []
        self.battery_y_vals = []

    def animate(self, i):
        self.battery_x_vals.append(next(self.index))
        battery = psutil.sensors_battery()
        if battery:
            battery_percent = battery.percent
            self.battery_y_vals.append(battery_percent)
            self.ax.clear()
            self.ax.plot(self.battery_x_vals, self.battery_y_vals,color= "red")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Battery Status (%)")
            self.battery_info_label.config(text=f"Battery Status = {battery_percent}%")
        else:
            self.handle_battery_data_unavailable()

    def handle_battery_data_unavailable(self):
        self.ax.clear()
        self.battery_info_label.config(text="No Battery data available on this platform\nNote: The program is using psutil.sensors_temperatures() \nwhich might not work on some platform like window.")
        self.ax.axis('off')

    def display(self):
        super().display()
        self.clear_frame()
        self.set_header("Battery Status")

        index = itertools.count()
        self.ani = FuncAnimation(self.fig, self.animate, frames=index, interval=1000)
        canvas_battery = FigureCanvasTkAgg(self.fig, master=self.frame)
        canvas_widget_battery = canvas_battery.get_tk_widget()
        canvas_widget_battery.pack()
        self.battery_info_label = Label(self.frame, text="", font=("Tahoma", 18),bg="Black", fg= "Green")
        self.battery_info_label.pack()

    
#-----------------------------------------------------------------------------------------------------------------------------------


class System:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("System status display")

        self.frame = tk.Frame(self.window, width=1200, height=700, bg="Black")
        self.frame.pack()

        menubar = Menu(self.window)
        self.window.config(menu=menubar)

        options_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=options_menu)

        self.display_types = {
            "Overall": OverallDisplay(self.window, self.frame, plt.subplots()),
            "CPU": CPUDisplay(self.window, self.frame),
            "Memory": MemoryDisplay(self.window, self.frame, plt.subplots()),
            "Network": NetworkDisplay(self.window, self.frame, plt.subplots()),
            "Disk": DiskDisplay(self.window, self.frame, plt.subplots()),
            "Process": ProcessDisplay(self.window, self.frame),
            "Temperature" : TemperatureDisplay(self.window, self.frame, plt.subplot()),
            "Battery" : BatteryDisplay(self.window, self.frame, plt.subplot()), 
        }

        for label, display in self.display_types.items():
            options_menu.add_command(label=label, command=display.display)

        self.display_overall()
        self.window.mainloop()

    def display_overall(self):
        self.display_types["Overall"].display()

System()
