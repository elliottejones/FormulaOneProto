import tkinter as tk
from tkinter import Toplevel, Listbox
from PIL import Image, ImageTk
import pandas
from urllib.request import urlopen
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import time
from tkinter.scrolledtext import ScrolledText

class analysis(object):

    def __init__(self):

        self.chatList = []

        self.API_URL = "https://api-inference.huggingface.co/models/google/gemma-2b-it"
        self.headers = {"Authorization": "Bearer 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"}

        self.selectedDriver = None
        self.selectedDriverNumber = None

        sessions = urlopen("https://api.openf1.org/v1/sessions?")
        sessionData = json.loads(sessions.read().decode('utf-8'))
        self.session = sessionData[-1]["session_key"]
        newUrl = "https://api.openf1.org/v1/drivers?session_key=" + str(self.session)
        drivers = urlopen(newUrl)
        self.driversData = json.loads(drivers.read().decode('utf-8'))
    
        self.root = tk.Tk()
        self.root.title("F1 Proto")

        # initialize the flags
        self.driver_window_open = False
        self.mode_window_open = False
        self.chatbotOpen = False

        width = 1280
        height = 720
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(alignstr)
        self.root.resizable(width=False, height=False)

        # Background image setup
        bg_image = Image.open("interfaceFiles/liveMenu.png")
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.root, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        # Keep a reference to prevent garbage collection
        bg_label.image = bg_photo

        self.chatbotWindowButton = tk.Button(self.root, text="Open AI Analyst", command=self.chatbotWindow,bg="#68c6c3",fg="black")
        self.chatbotWindowButton.place(x=470,y=700)

        self.open_driver_window_button = tk.Button(self.root, text="Open Driver Select", command=self.driverWindow,bg="#68c6c3",fg="black")
        self.open_driver_window_button.place(x=10,y=700)

        self.open_mode_window_button = tk.Button(self.root, text="Open Mode Select", command=self.modeWindow,bg="#68c6c3",fg="black")
        self.open_mode_window_button.place(x=230,y=700)

        self.selected_driver_label = tk.Label(self.root, text="No driver selected", bg="#68c6c3",fg="black")
        self.selected_driver_label.place(x=10, y=680) 

        self.mode_window_label = tk.Label(self.root, text="Default Mode: Single Sector Mode", bg="#68c6c3",fg="black")
        self.mode_window_label.place(x=230,y=680)

        self.selectedMode = "Single Sector Mode"

        self.chatHistory = ""

        self.start_updating()
        self.root.mainloop()

    def query(self, input):
            
            payload = {

                "inputs": self.chatHistory,
                "parameters": {"max_new_tokens": 250}
            }
            
            response = requests.post(self.API_URL, headers=self.headers, json=payload).json()
            generated_text = response[0]["generated_text"]
            answer_prefix = 'model'
            actual_response = generated_text.rsplit(answer_prefix)[-1].strip()
            self.chatList.append(input)
            self.update_chat_history("Analyst: " + actual_response)
            self.update_chat_history("\n")
            return actual_response
    
    def send_message(self, event):

        user_message = self.chat_input.get()

        # Add user input to chat history 
        self.update_chat_history(f"You: {user_message}")
        self.update_chat_history("\n")

        # Clear the entry widget
        self.chat_input.delete(0, tk.END)

        self.chatHistory += ("<rules> you are an f1 data analyst. please try to keep your answers super short <start_of_turn>user " + user_message + "<end_of_turn> <start_of_turn>model")

        self.query(user_message)

    def chatbotWindow(self):
        if not self.chatbotOpen:
            self.chatbotOpen = True
            self.cwin = Toplevel(self.root)
            self.cwin.title("AI Analyst")

            width = 640
            height = 360
            screenwidth = self.cwin.winfo_screenwidth()
            screenheight = self.cwin.winfo_screenheight()
            alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) // 2, (screenheight - height) // 2)
            self.cwin.geometry(alignstr)
            self.cwin.resizable(width=False, height=False)

            self.chat_history = ScrolledText(self.cwin, state='disabled', wrap=tk.WORD)
            self.chat_history.place(x=0,y=0, relheight=0.8,relwidth=1)

            self.chat_input = tk.Entry(self.cwin)
            self.chat_input.place(rely=0.82,x=0, relheight=0.15,relwidth=1)
            self.chat_input.bind("<Return>", self.send_message)

    def update_chat_history(self, message):
        # Ensure the ScrolledText widget is in normal state before inserting text
        self.chat_history.configure(state='normal')
        self.chat_history.insert(tk.END, message + "\n")
        self.chat_history.configure(state='disabled')

        # Scroll to the end of the chat history
        self.chat_history.yview(tk.END)


    def driverWindow(self):
        if not self.driver_window_open:  # Check if the window is already open
            self.driver_window_open = True  # Set the flag to indicate the window is open
            self.dwin = Toplevel(self.root)
            self.dwin.title("Driver Select")
            
            self.dwin.protocol("WM_DELETE_WINDOW", self.on_driver_window_close)  # Handle window close
            
            # Create a Listbox in the new window
            self.driver_listbox = Listbox(self.dwin)
            self.driver_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
            
            confirm_button = tk.Button(self.dwin, text="Confirm", command=self.confirm_driver)
            confirm_button.pack(pady=10)

            # Example items for the Listbox
            driversSet = set()

            for driver in self.driversData:
                driversSet.add(driver["full_name"])

            for driver in driversSet:
                self.driver_listbox.insert(tk.END, driver)
    
    def modeWindow(self):
        if not self.mode_window_open:
            self.mode_window_open = True
            self.mwin = Toplevel(self.root)
            self.mwin.title = ("Mode Select")

            self.mwin.protocol("WM_DELETE_WINDOW", self.on_mode_window_close)

            self.mode_listbox = Listbox(self.mwin)
            self.mode_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            confirm_mode_button = tk.Button(self.mwin, text="Confirm", command=self.confirm_mode)
            confirm_mode_button.pack(pady=10)

            self.mode_listbox.insert(tk.END, "Single Sector")
            self.mode_listbox.insert(tk.END, "Compare Sector")
            self.mode_listbox.insert(tk.END, "Per Sector Gap")        

    def on_driver_window_close(self):
        self.driver_window_open = False
        self.dwin.destroy()
    
    def on_mode_window_close(self):
        self.mode_window_open = False
        self.mwin.destroy()
    
    def confirm_driver(self):
        selected_index = self.driver_listbox.curselection()
        if selected_index:
            self.selectedDriver = self.driver_listbox.get(selected_index[0])

            for driver in self.driversData:
                if driver["full_name"] == self.selectedDriver:
                    self.selectedDriverNumber = driver["driver_number"]
                    print(self.selectedDriverNumber)

            self.selected_driver_label.config(text=f"Selected Driver: {self.selectedDriver}")
            self.dwin.destroy()
            self.driver_window_open = False
        else:
            print("No driver selected")
    
    def confirm_mode(self):
        selected_index = self.mode_listbox.curselection()
        if selected_index:
            self.selectedMode = self.mode_listbox.get(selected_index[0])
        
        self.mode_window_label.config(text=f"Selected Mode: {self.selectedMode}")
        self.mwin.destroy()
        self.mode_window_open = False

    def start_updating(self):
        
        if self.selectedDriverNumber:

            lapUrl = "https://api.openf1.org/v1/laps?session_key="+str(self.session)+"&driver_number="+str(self.selectedDriverNumber)
            lapJson = urlopen(lapUrl) 
            lapData = json.loads(lapJson.read().decode('utf-8'))
            df = pd.DataFrame(lapData)

            # Set the background color of the plot to black, and line colors as desired
            plt.figure(figsize=(12, 6))
            
            # Set the face and edge color to black
            plt.rcParams['axes.facecolor'] = 'black'
            plt.rcParams['axes.edgecolor'] = 'white'
            plt.rcParams['axes.labelcolor'] = 'white'
            plt.rcParams['xtick.color'] = 'white'
            plt.rcParams['ytick.color'] = 'white'
            plt.rcParams['grid.color'] = 'white'

            if self.selectedMode == "Single Sector":
                plt.plot(df['lap_number'], df['duration_sector_1'], color='cyan', label='Sector 1')
                plt.plot(df['lap_number'], df['duration_sector_2'], color='magenta', label='Sector 2')
                plt.plot(df['lap_number'], df['duration_sector_3'], color='yellow', label='Sector 3')

            elif self.selectedMode == "Per Sector Gap":
                print("N/A - Feature not present yet.")

            # Title and labels
            plt.title('Lap Duration Over Laps: ' + self.selectedDriver)
            plt.xlabel('Lap Number', color = 'white')
            plt.ylabel('Lap Duration (seconds)',color = 'white')

            # Enable the grid
            plt.grid(True)
            
            legend = plt.legend(facecolor='lightgray')  # Set the background color of the legend
            plt.setp(legend.get_texts(), color='black')

            # Save the figure
            plt.savefig("data/lap_times.png", facecolor='black')
            plt.close()

            graph_image = Image.open("data/lap_times.png")
            graph_photo = ImageTk.PhotoImage(graph_image)
            graph_label = tk.Label(self.root, image=graph_photo)
            graph_label.place(x=100,rely=0.14, width=1100, relheight= 0.8)
            graph_label.image = graph_photo

        self.root.after(1000, self.start_updating)


    
if __name__ == "__main__":
    app = analysis()

