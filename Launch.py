# Raw Packages
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from pandas import DataFrame


# Gui Packages
import tkinter
from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Data Source
import fxcmpy

# Token
TOKEN = "8ee215b13f266c6fc67cd1523a0d9d775cf0b062" # Change this

# Establishes connection to FXCM server
con = fxcmpy.fxcmpy(access_token= TOKEN, server='demo') # change to real
print ("Connection established")


# perimeters
DATA_POINTS = 10000 # Number of data points pulled from the server (0-10,000)
ping_speed = 600000 # ping every minute(miliseconds)
period_length = "m5" # Frquency of data points
history_length = int(period_length[1: len(period_length)])# Length of history pulled from the server (minutes)
gap = 90000 # Placeholder for rolling average (# of data points)

# Instantiates our objects
market_table = DataFrame()
data = con.get_candles('USD/CAD', period = period_length, number = DATA_POINTS)
GUI = tkinter.Tk()
GUI.title("USD/CAD")
GUI.geometry('1000x600')
frame = Frame(GUI, width = 1000, height = 600)
frame.place(x= 0, y = 0)


# Instantiates our data

length = 0 # Placeholder for the length of the data
mvavg = []
pr = []
upper_band = []
lower_band = []
ind = []
time = []

def fxcm_data_collect():
    data = con.get_candles('USD/CAD', period = period_length, number = DATA_POINTS) # Collects data 1 * 150,0000 minutes back
    length = len(data)
    for i in range (0, length):
        mean = data['askclose'][-gap: -2].mean()
        mvavg.append(mean)
        upper_band.append(mean + 2 * data['askclose'][-gap: -2].std())
        lower_band.append(mean - 2 * data['askclose'][-gap: -2].std())
        ind.append(i)
        time_of_trade = datetime.now() - timedelta(hours=0, minutes= int(period_length[1: len(period_length)]) * (length - i))
        time.append(time_of_trade)


def compile_plot():
    table = {'Time' : time[-9998: -2],
    'Closing Price' : data['askclose'][-9998: -2],
    'Moving Average': mvavg[-9998: -2], 
    'Upper Band' : upper_band[-9998: -2],
    'Lower Band' : lower_band[-9998: -2]}

    return DataFrame(table, columns = ['Time', 'Moving Average', 'Closing Price', 'Upper Band', 'Lower Band'])



# Creates window with Upper and Lower Bounds
def load_gui(market_table):
    for widget in frame.winfo_children(): # clears_data_on_window
       widget.destroy()

    # Latest closing price
    closing_price = tkinter.Label(frame, text = "Closing price is " + "{:.5f}".format(data['askclose'][-2]), font = ("Times New Roman", 18)).pack()
    # Latest moving average
    moving_average = tkinter.Label(frame, fg = "blue", text = "Moving average is " + "{:.5f}".format(mvavg[-2]), font = ("Times New Roman", 18)).pack()
    # Latest upper bound
    upper_bound = tkinter.Label(frame, fg = "green", text = "Upper Band is " + "{:.5f}".format(upper_band[-2]), font = ("Times New Roman", 18)).pack()
    # Latest lower bound
    lower_bound = tkinter.Label(frame, fg = "green", text = "Lower Band is " + "{:.5f}".format(lower_band[-2]), font = ("Times New Roman", 18)).pack()

    # Market graph
    figure = plt.Figure(figsize=(5,4), dpi=100) # Size of plot
    axis = figure.add_subplot(111) # position of graph
    line2 = FigureCanvasTkAgg(figure, frame) # embedding graph in GUI

    line2.get_tk_widget().pack(side=tkinter.LEFT, fill=tkinter.BOTH)

    #market_graph = market_table[['Time', 'Moving Average', 'Closing Price', 'Upper Band', 'Lower Band']].groupby('Time').sum()
        
    market_graph = market_table['Closing Price'][-10:-2].groupby(market_table['Time'][-10:-2]).sum()
    market_graph.plot(kind='line', legend=True, ax=axis, color = 'k', fontsize=8, linewidth= 2.5)

    market_graph = market_table['Moving Average'][-10:-2].groupby(market_table['Time'][-10:-2]).sum()
    market_graph.plot(kind='line', legend=True, ax=axis, color='b', fontsize=8, linewidth= 2.5)


    market_graph = market_table['Upper Band'][-10:-2].groupby(market_table['Time'][-10:-2]).sum()
    market_graph.plot(kind='line', legend=True, ax=axis, color='g', fontsize=8, linewidth= 2.5)

    market_graph = market_table['Lower Band'][-10:-2].groupby(market_table['Time'][-10:-2]).sum()
    market_graph.plot(kind='line', legend=True, ax=axis, color='g', fontsize=8, linewidth= 2.5)

    
    axis.set_title('USD/CAD')
    frame.pack()

def closes_fxcm_connection(con):
    con.close()
    print ("Connection terminated")

def run_gui():
    GUI.mainloop()

def clear_data():
    data = None
    length = 0 # Placeholder for the length of the data
    mvavg = []
    pr = []
    upper_band = []
    lower_band = []
    ind = []

def ping():
    clear_data()
    print("fetching data...")
    fxcm_data_collect()
    market_table = compile_plot()
    load_gui(market_table)
    print("fetched data")
    GUI.after(60000, ping)



def main():
    ping()
    run_gui()
    closes_fxcm_connection(con)

main()