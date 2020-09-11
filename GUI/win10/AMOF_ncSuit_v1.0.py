"""
   This program is driven from a GUI and allows the user to:
   1. select a single file
   2. opens the file and provieds a summary pane 
   3. starts a child window with three tabs
          Glaobal attrib8utes
          Dimensions
          Varaibales
   4. Variables are selectable - when clicked the attributes of that variable are diplayed
          The selected variable is plottable at this point
"""

# !/usr/bin/python3
import os
from os import path
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from netCDF4 import Dataset
import numpy as np  
import xlsxwriter
import warnings

"""
   Function to get file from a ask dialogue box:
      askopenfilename
   This return the file name butdoe not open it.
   
   An attempt is made to open the file and to test iif it is valid.
   An exception is raised and acted upon if there is a problem
   Error message displyed in popup message box.
   Only if no error occurs does a child window open
   nc file if closed 
"""   
def get_file():
   """
      Make the file name a global variable 
   """
   global fn
   # get the filenme
   fn =  filedialog.askopenfilename(initialdir = "/",title = "Select nc file",filetypes = (("nc files","*.nc"),("all files","*.*")))
   # clear the list boxes 
   TT1.delete("1.0", END) #clear file pane
   TT2.delete("1.0", END) #clear summary pane
   # try to open the file
   try:
      # open the file
      ncid = Dataset(fn, mode='r')
      # close again if no error
      ncid.close() 
      # show file name in list box      
      TT1.insert(END, fn)
      # populate summary pane      
      summary_callback()  
      # go to function that give tabbed child window      
      view_callback()
   except:
      # if an error occurs give message in popup box
      message = "Unable to open file:\n{}".format(fn)
      messagebox.showerror("Opening NC file", message)
      TT1.insert(END, "*.nc") 

"""
   If close file is selected from menu.
   Clear the list boes on main frame
   Close all child windows - this will clear all variables associated
   NC file will be closed at this point - open-extract-close protocol operating
"""
def close_file():
   # clear file pane
   TT1.delete("1.0", END)
   # clear summary pane
   TT2.delete("1.0", END)
   TT1.insert(END, "*.nc") 
   
   #close file inspection child windows if open
   try:
      viw.destroy()
   except:
      pass
   #close plot child windows if open
   try:
      v_plt.destroy()
   except:
      pass  
   #close graph variable child windows if open
   try:
      v_gv.destroy()
   except:
      pass        
      
"""
   When an nc file is selected and shown to exists
        open_file tries to open and if successful closes it again and moves on
   The file is interogated to and a summary report is presented in the 
   report paneof the main window. 
   Try except used to capture exceptions.
   Once the summary is complete the nc file is closed.    
"""
def summary_callback(): 
   ncid = Dataset(fn, mode='r') # open the source file
      
   # get a listof all the variables
   nc_vars = [var for var in ncid.variables]
   try:
      message = "No Variables: {}\n".format(len(nc_vars))
   except:
      message = "No Variables: error\n"
   TT2.insert(END, message)
   #Pull out basic information from Global attributes
   try:
      message = "Source Instrument: {}\n".format(ncid.getncattr('source'))
   except:
      message = "Source Instrument: error\n"
   TT2.insert(END, message)   
   try:
      message = "Feature Type: {}\n".format(ncid.getncattr('featureType'))
   except:
      message = "Feature Type: error\n"
   TT2.insert(END, message) 
   try:
      message = "Type of Platform: {}\n".format(ncid.getncattr('platform_type'))
   except:
      message = "Type of Platform: error\n"
   TT2.insert(END, message) 
   try:
      message = "Mode of Deployment: {}\n".format(ncid.getncattr('deployment_mode'))
   except:
      message = "Mode of Deployment: error\n"
   TT2.insert(END, message) 
   try:
      message = "Deplyment Position: {}\n".format(ncid.getncattr('geospatial_bounds'))
   except:
      message = "Deplyment Position: error\n"
   TT2.insert(END, message) 
   try:   
      message = "Start of Data Coverage: {}\n".format(ncid.getncattr('time_coverage_start'))
   except:
      message = "Start of Data Coverage: error\n"
   TT2.insert(END, message) 
   try:   
      message = "End of Data Coverage: {}\n".format(ncid.getncattr('time_coverage_end'))
   except:
      message = "End of Data Coverage: error\n"
   TT2.insert(END, message)
   
   ncid.close() #close the source file

"""
   This function when a variable is selected and the plot button clicked
   It creates a child window
   An interactive matplotlig figure with toolbar is placed on window
   Tool bar provides svae function
   Print not provided
"""
def GraphVar_callback(selected_var_name, D1, D2, D3, log, qc, log_x, log_y):
   from matplotlib.backends.backend_tkagg import (
   FigureCanvasTkAgg, NavigationToolbar2Tk)
   # Implement the default Matplotlib key bindings.
   from matplotlib.backend_bases import key_press_handler
   import matplotlib.dates as mdates
   import matplotlib.pyplot as plt
   import time
   
   # create child window and make hadle a global variable
   global v_gv
   v_gv = Toplevel(root)
   # confgure child window
   v_gv.geometry('700x500+200+200')
   # stop child window being resized
   v_gv.resizable(0, 0)
   #disable tool window
   v_gv.title('AMOF NC Tools: Graph Variable')
   v_gv.iconbitmap('AMOF.ico')
   
   #create a figure instance for plotting
   fig = plt.figure(figsize = (5, 4), dpi = 100)
   
   #create canvas for plotting on
   canvas = FigureCanvasTkAgg(fig, master = v_gv)  # A tk.DrawingArea.
   canvas.draw()
   canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = 1)
   
   # makes things interactive toolbar includes a save fuction 
   toolbar = NavigationToolbar2Tk(canvas, v_gv)
   toolbar.update()
   canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = 1)
   
   """   
      Data preparation 
   """
   #open the source file
   ncid = Dataset(fn, mode='r')
   if qc == True:
      ncid.set_auto_maskandscale(True) # masked array
   else:
      ncid.set_auto_maskandscale(False) # raw data
   
   #get dimensions of selected variable
   nc_dims = ncid.variables[selected_var_name].dimensions 
   #get the data try the three different structures that might be present
   try:
      dd = ncid.variables[selected_var_name][:]
   except:
      dd = ncid.variables[selected_var_name][:][:]
   finally:
      dd = ncid.variables[selected_var_name][:][:][:]   
   
   # apply qc if selected
   if qc == True:
      try:
         # get valid min and max
         dd_min = ncid.variables[selected_var_name].getncattr('valid_min')
         dd_max = ncid.variables[selected_var_name].getncattr('valid_max')
      except:
         dd_min = np.min(dd)
         dd_max = np.max(dd)
   else:
      dd_min = np.min(dd)
      dd_max = np.max(dd)
      
   #get data long name, units attributes and if present the practicle units
   try:
      dd_n = ncid.variables[selected_var_name].getncattr('long_name')
   except:
      dd_n = selected_var_name
   
   dd_u = 'Unitless'
   try:
      dd_u = ncid.variables[selected_var_name].getncattr('practical_units')
   except:
      dd_u = ncid.variables[selected_var_name].getncattr('units')   
      
   dd_label = "{} ({})".format(dd_n, dd_u)
   
   """
      log the selected variable if checkbox was selected
   """
   # log data if selected
   if log == True:
      dd = np.log10(dd) # nans returned for data <=0
      dd_min = np.log10(dd_min)
      dd_max = np.log10(dd_max)
      dd_label = "log10({})".format(dd_label)
   
   """
      Apply QC flag if selected
      Files may have a number of qc_flags so choise the most appropriate
   """
   if qc == True:
      flags = []
      ff = []
      #get list of all qc flags in file
      nc_vars = [var for var in ncid.variables]     
      for var in nc_vars:
         if 'qc' in var:
            flags.append(var)
      # if there is only one qc_flag in the file
      if len(flags) == 1:      
         ff = flags[0]
      else: #look for a qc_flag that has the variable name in it
         for n in range(len(flags)):
            if flags[n].strip("qc_flag_").lower() in selected_var_name.lower():
               ff = flags[n]
      # if a flag still has not been selected look for one that has the cheminacle species in (could be upper or lower case)  
      if len(ff) < 1:
         for n in range(len(flags)):
            try:
               if flags[n].strip("qc_flag_").lower() == ncid.variables[selected_var_name].getncattr('chemical_species').lower():
                  ff = flags[n]
            except:
               pass            
      # only if you succed in allocating a flag apply it
      if len(ff) > 0:
         # try the following - get the data associated with qc_flag found
         try: 
            flag = ncid.variables[ff][:]
         except:
            flag = ncid.variables[ff][:][:]
         finally:
            flag = ncid.variables[ff][:][:][:]
         #try to apply the flag - if no flag data will come with no qc applied   
         try:
            if flag.shape == dd.shape:     
               np.putmask(dd, (flag !=1 ), np.nan)
         except:
            pass
         
   """
      Data preparation - dependent variable 1
   """
   if len(D1) > 1:
      # get the data
      try:
         d1 = ncid.variables[D1[0]][:]
         d1_min = D1[2]
         d1_max = D1[3]
      except:
         d1 = np.arange(0, len(ncid.dimensions[D1[0]]), 1)
         d1_min = D1[2]
         d1_max = D1[3]
   
      # get the unitis
      try:
         u1 = ncid.variables[D1[0]].getncattr('units')
      except:
         u1 = 'Unitless'
   
      # get label   
      try: 
         n1 = ncid.variables[D1[0]].getncattr('long_name')
      except:
         n1 = D1[0]
   
      # if dimension 1 is time
      if "time" in D1[0]:
         d1_ti = "Time (UTC)"
         t_file = d1
         d1 = []
         # need to conver epoch time to something matplotlib understands 
         for n in range(len(t_file)):
            d1.append(mdates.datestr2num(time.asctime(time.gmtime(t_file[n]))))
         # set the limits as selected by the user   
         d1_min = mdates.datestr2num(time.asctime(time.gmtime(D1[2])))
         d1_max = mdates.datestr2num(time.asctime(time.gmtime(D1[3])))
      else:
         d1_ti = "{} ({})".format(n1, u1)
   
   """
      Data preparation - dependent variable 2
   """
   # if there is a second dependent varaible (2D data) get the details 
   if len(D2) > 1:
      # get the data
      try:
         d2 = ncid.variables[D2[0]][:]
         d2_min = D2[2]
         d2_max = D2[3]
      except:
         d2 = np.arange(0, len(ncid.dimensions[D2[0]]), 1)
         d2_min = D2[2]
         d2_max = D2[3]
   
      # get the unitis
      try:
         u2 = ncid.variables[D2[0]].getncattr('units')
      except:
         u2 = 'Unitless'
   
      # get label   
      try: 
         n2 = ncid.variables[D2[0]].getncattr('long_name')
      except:
         n2 = D2[0]
         
      # if dimension 2 is time
      if "time" in D2[0]:
         d2_ti = "Time (UTC)"
         t_file = d2
         d2 = []
         # need to conver epoch time to something matplotlib understands 
         for n in range(len(t_file)):
            d2.append(mdates.datestr2num(time.asctime(time.gmtime(t_file[n]))))
         # set the limits as selected by the user   
         d2_min = mdates.datestr2num(time.asctime(time.gmtime(D2[2])))
         d2_max = mdates.datestr2num(time.asctime(time.gmtime(D2[3])))
      else:
         d2_ti = "{} ({})".format(n2, u2)
   
   """
      Data preparation - dependent variable 3
   """
   # if there is a third dependent varaible (3D data) get the details 
   # axes and lables
   if len(D3) > 1:
      # get the data
      try:
         d3 = ncid.variables[D3[0]][:]
         d3_min = D3[2]
         d3_max = D3[3]
      except:
         d3 = np.arange(0, len(ncid.dimensions[D3[0]]), 1)
         d3_min = D3[2]
         d3_max = D3[3]
   
      # get the unitis
      try:
         u3 = ncid.variables[D3[0]].getncattr('units')
      except:
         u3 = 'Unitless'
   
      # get label   
      try: 
         n3 = ncid.variables[D3[0]].getncattr('long_name')
      except:
         n3 = D3[0]
         
      # if dimension 3 is time
      if "time" in D2[0]:
         d3_ti = "Time (UTC)"
         t_file = d3
         d3 = []
         # need to conver epoch time to something matplotlib understands 
         for n in range(len(t_file)):
            d3.append(mdates.datestr2num(time.asctime(time.gmtime(t_file[n]))))
         # set the limits as selected by the user   
         d3_min = mdates.datestr2num(time.asctime(time.gmtime(D3[2])))
         d3_max = mdates.datestr2num(time.asctime(time.gmtime(D3[3])))
      else:
         d3_ti = "{} ({})".format(n3, u3)
   
   """
      Plot title
   """
   try:
      ti = "{}".format(ncid.variables[selected_var_name].getncattr('long_name'))
   except:
      ti = "{}".format(selected_var_name)
   #close the source file
   ncid.close()         
   
   """
      set the axis and reshape the arrays if needed
   """  
   # set D1 to either the x, y or z axis depending on slection   
   if len(nc_dims) == 1:# if 1d data
      if D1[1] == 'x':
         x = d1 
         x_label = d1_ti
         x_min = d1_min
         x_max = d1_max
         y = dd
         y_label = dd_label
         y_min = dd_min
         y_max = dd_max
      else:
         x = dd
         x_label = dd_label
         x_min = dd_min
         x_max = dd_max
         y = d1 
         y_label = d1_ti
         y_min = d1_min
         y_max = d1_max
   if len(nc_dims) == 2:# if 2d data
      if D1[1] == 'x':
         x = d1 
         x_label = d1_ti
         x_min = d1_min
         x_max = d1_max
         y = d2
         y_label = d2_ti
         y_min = d2_min
         y_max = d2_max
      else:
         x = d2
         x_label = d2_ti
         x_min = d2_min
         x_max = d2_max
         y = d1 
         y_label = d1_ti
         y_min = d1_min
         y_max = d1_max       
   if len(nc_dims) == 3: # if 3d data  
      if D1[1] == 'x':
         x = d1 
         x_label = d1_ti
         x_min = d1_min
         x_max = d1_max
      if D1[1] == 'y':
         y = d1
         y_label = d1_ti
         y_min = d1_min
         y_max = d1_max
      if D2[1] == 'x':
         x = d2 
         x_label = d2_ti
         x_min = d2_min
         x_max = d2_max
      if D2[1] == 'y':
         y = d2
         y_label = d2_ti
         y_min = d2_min
         y_max = d2_max
      if D3[1] == 'x': 
         x = d3 
         x_label = d3_ti
         x_min = d3_min
         x_max = d3_max
      if D3[1] == 'y':
         y = d3
         y_label = d3_ti
         y_min = d3_min
         y_max = d3_max
      
      # reshape the data
      temp = dd
      if D1[1] == 'z':
         xx = np.where(t_file >= D1[2])
         dd = np.reshape(temp[xx[0][0],:,:], (temp.shape[1], temp.shape[2]))
         dd_min = np.nanmin(dd)
         dd_max = np.nanmax(dd)
      if D2[1] == 'z':
         xx = np.where(d2 == D2[2])
         dd = np.reshape(temp[:,xx[0][0],:], (temp.shape[0], temp.shape[2]))
         dd_min = np.nanmin(dd)
         dd_max = np.nanmax(dd)
      if D3[1] == 'z':
         xx = np.where(d3 == D3[2])
         dd = np.reshape(temp[:,:,xx[0][0]], (temp.shape[0], temp.shape[1]))
         dd_min = np.nanmin(dd)
         dd_max = np.nanmax(dd)
   """
      plot data 1D
   """   
   if len(nc_dims) == 1:
      ax = fig.add_subplot(111, ylabel = y_label, xlabel = x_label, title = ti)
      ax.plot(x,y)
      ax.set_xlim(x_min, x_max)
      ax.set_ylim(y_min, y_max)
      if log_x == True:
         ax.set_xscale('log')
      if log_y == True:
         ax.set_yscale('log')  
      ax.grid(True)
      
   """
      plot data 2D
   """
   if len(x) == dd.shape[0]:
      temp = dd
      dd = np.transpose(temp)
    
   if len(nc_dims) > 1:
      ax = fig.add_subplot(111, ylabel = y_label, xlabel = x_label, title = ti)
      pc = ax.pcolor(x, y, dd, cmap='viridis', vmin = dd_min, vmax = dd_max)
      ax.set_xlim(x_min, x_max)
      ax.set_ylim(y_min, y_max)
      if log_x == True:
         ax.set_xscale('log')
      if log_y == True:
         ax.set_yscale('log')
      ax.grid(True)
      cb = fig.colorbar(pc, ax = ax, orientation = 'vertical')  
      cb.set_label(dd_label)    
      
   #autoformat time axis 
   locator = mdates.AutoDateLocator(minticks=3, maxticks=12)
   formatter = mdates.ConciseDateFormatter(locator)
   if x_label == "Time (UTC)":
      ax.xaxis.set_major_locator(locator)
      ax.xaxis.set_major_formatter(formatter)
   if y_label == "Time (UTC)":
      ax.yaxis.set_major_locator(locator)
      ax.yaxis.set_major_formatter(formatter) 

"""
   This function when a variable is selected and the plot button clicked
   It creates a child window to allow range and axes to be selected
"""   
def plot_callback(selected_var_name):  
   # create 2 child windows
   global v_plt
   v_plt = Toplevel(root)
   # confgure child window
   v_plt.geometry('750x250+150+150')
   # stop child window being resized
   v_plt.resizable(0, 0)
   #disable tool window
   v_plt.title('AMOF NC Tools: Set up plot')
   v_plt.iconbitmap('AMOF.ico')
   
   #add labelled frame - axes
   f3 = LabelFrame(v_plt, text = "Axes", relief = GROOVE, borderwidth = 2, height = 150)#, width = 893)
   f3.grid(row = 0, column = 0, padx = 3, pady = 3, sticky = 'nw')
   
   #add labelled frame - data
   f4 = LabelFrame(v_plt, text = "Data", relief = GROOVE, borderwidth=2, height = 80)#, width = 593)
   f4.grid(row = 1, column = 0, padx = 3, pady = 3, sticky = 'nw')
   
   """
      This is called Whne the Graph button is clicked
   """
   def gra_callback():
      # set up a tuple holding the information set by the user for the
      # thre possibe dependent variables. 
      # name, axis, min, max
      D1 = []
      D2 = []
      D3 = []
      # D1
      D1.append(D1Name.cget("text"))
      if dim1_x.get() == True:
         D1.append('x')
      if dim1_y.get() == True: 
         D1.append('y')
      if dim1_z.get() == True: 
         D1.append('z')    
      if D1MAX.get() <= D1MIN.get():   
         D1.append(D1MAX.get())
         D1.append(D1MIN.get())
      else:
         D1.append(D1MIN.get())
         D1.append(D1MAX.get())
      
      # D2
      try:
         D2.append(D2Name.cget("text"))
         if dim2_x.get() == True:
            D2.append('x')
         if dim2_y.get() == True: 
            D2.append('y')
         if dim2_z.get() == True: 
            D2.append('z')
         if D2MAX.get() <= D2MIN.get():   
            D2.append(D2MAX.get())
            D2.append(D2MIN.get())
         else:
            D2.append(D2MIN.get())
            D2.append(D2MAX.get())
      except:
         pass
      
      # D3
      try: 
         D3.append(D3Name.cget("text"))
         if dim3_x.get() == True:
            D3.append('x')
         if dim3_y.get() == True: 
            D3.append('y')
         if dim3_z.get() == True: 
            D3.append('z')
         if D3MAX.get() <= D3MIN.get():   
            D3.append(D3MAX.get())
            D3.append(D3MIN.get())
         else:
            D3.append(D3MIN.get())
            D3.append(D3MAX.get())   
      except:
         pass
      
      # now all the inforamation has been gathered call the graphing function 
      GraphVar_callback(selected_var_name, D1, D2, D3, log_dat.get(), QC.get(), log_x.get(), log_y.get())
   
   """
       what to do if the dims checkuttons are clicked
   """     
   def Dims_callback():
      # 1D
      if len(xyz) == 1:
         if ((dim1_x.get() == True) and (dim1_y.get() == True)):
            D1X.deselect()
            D1Y.select()   
         if ((dim1_x.get() == False) and (dim1_y.get() == False)):
            D1X.select()
      #2D      
      if len(xyz) == 2:
         if ((dim1_x.get() == True) and (dim1_y.get() == True)):
            D1X.deselect()
            D1Y.select()
            D2X.select()
            D2Y.deselect()  
         if ((dim2_x.get() == True) and (dim2_y.get() == True)):
            D1X.select()
            D1Y.deselect()
            D2X.deselect()
            D2Y.select()
         if ((dim1_x.get() == False) and (dim1_y.get() == False)):
            D1X.select()            
            D1Y.deselect() 
            D2X.deselect() 
            D2Y.select() 
         if ((dim2_x.get() == False) and (dim2_y.get() == False)):
            D1X.select()            
            D1Y.deselect() 
            D2X.deselect() 
            D2Y.select()   
     
      #3D            
      if len(xyz) == 3:
        if dim1_z.get() == True:
           D1X.deselect()
           D1Y.deselect()
           D2Z.deselect()
           D3Z.deselect()
           if ((dim3_x.get() == True) and (dim3_y.get() == True)):
              D3X.deselect()
              D3Y.select()
              D2X.select()
              D2Y.deselect()  
           if ((dim2_x.get() == True) and (dim2_y.get() == True)):
              D3X.select()
              D3Y.deselect()
              D2X.deselect()
              D2Y.select()
           if ((dim3_x.get() == False) and (dim3_y.get() == False)):
              D3X.select()            
              D3Y.deselect() 
              D2X.deselect() 
              D2Y.select() 
           if ((dim2_x.get() == False) and (dim2_y.get() == False)):
              D3X.select()            
              D3Y.deselect() 
              D2X.deselect() 
              D2Y.select()
        if dim2_z.get() == True:
           D1Z.deselect()
           D2X.deselect()
           D2Y.deselect()
           D3Z.deselect()
           if ((dim1_x.get() == True) and (dim1_y.get() == True)):
              D1X.deselect()
              D1Y.select()
              D3X.select()
              D3Y.deselect()  
           if ((dim3_x.get() == True) and (dim3_y.get() == True)):
              D1X.select()
              D1Y.deselect()
              D3X.deselect()
              D3Y.select()
           if ((dim1_x.get() == False) and (dim1_y.get() == False)):
              D1X.select()            
              D1Y.deselect() 
              D3X.deselect() 
              D3Y.select() 
           if ((dim3_x.get() == False) and (dim3_y.get() == False)):
              D1X.select()            
              D1Y.deselect() 
              D3X.deselect() 
              D3Y.select()
        if dim3_z.get() == True:
           D1Z.deselect()
           D2Z.deselect()
           D3X.deselect()
           D3Y.deselect()
           if ((dim1_x.get() == True) and (dim1_y.get() == True)):
              D1X.deselect()
              D1Y.select()
              D2X.select()
              D2Y.deselect()  
           if ((dim2_x.get() == True) and (dim2_y.get() == True)):
              D1X.select()
              D1Y.deselect()
              D2X.deselect()
              D2Y.select()
           if ((dim1_x.get() == False) and (dim1_y.get() == False)):
              D1X.select()            
              D1Y.deselect() 
              D2X.deselect() 
              D2Y.select() 
           if ((dim2_x.get() == False) and (dim2_y.get() == False)):
              D1X.select()            
              D1Y.deselect() 
              D2X.deselect() 
              D2Y.select()
        if ((dim1_z.get() == False) and (dim2_z.get() == False) and (dim3_z.get() == False)):
           D1X.select()            
           D1Y.deselect() 
           D1Z.deselect()
           D2X.deselect() 
           D2Y.select() 
           D2Z.deselect()
           D3X.deselect()            
           D3Y.deselect() 
           D3Z.select()
           
   """
      create widgets for data frame - f4
   """
   log_dat = BooleanVar()
   QC = BooleanVar()
   log_x = BooleanVar()
   log_y = BooleanVar()
   log_dat.set(False)
   QC.set(False)
   log_x.set(False)
   log_y.set(False)
   data_button       = Button(f4, text = "Graph Variable", height = 1, width = 15, command = gra_callback)
   qc_CHbutton       = Checkbutton(f4, height = 1, width = 13, text = "Apply QC flag", variable = QC)
   logData_CHbutton  = Checkbutton(f4, height = 1, width = 13, text = "Log data value", variable = log_dat)
   logAxisX_CHbutton = Checkbutton(f4, height = 1, width = 14, text = "Log x-axis", variable = log_x)
   logAxisY_CHbutton = Checkbutton(f4, height = 1, width = 14, text = "Log y-axis", variable = log_y)
   #place on frame4
   qc_CHbutton.grid(row = 0, column = 0, padx = 13, pady = 3)
   logData_CHbutton.grid(row = 0, column = 1, padx = 13, pady = 3)
   logAxisX_CHbutton.grid(row = 0, column = 2, padx = 13, pady = 3)
   logAxisY_CHbutton.grid(row = 0, column = 3, padx = 13, pady = 3)
   data_button.grid(row = 0, column = 4, padx = 13, pady = 3)
   
   """
      create widgets for data frame - f3
   """
   #labels
   vl1 = Label(f3, text = "Dependent Vaiable", height = 1, width = 20)
   vl2 = Label(f3, text = "Name", height = 1, width = 10)
   vl3 = Label(f3, text = "Units", height = 1, width = 10)
   vl4 = Label(f3, text = "x", height = 1, width = 1)
   vl5 = Label(f3, text = "y", height = 1, width = 1)
   vl6 = Label(f3, text = "z", height = 1, width = 7)
   vl7 = Label(f3, text = "Start", height = 1, width = 3)
   vl8 = Label(f3, text = "End", height = 1, width = 3)
   #layout label widgets on axes frame
   vl1.grid(row = 0, column = 2, columnspan = 3)
   vl2.grid(row = 1, column = 0)
   vl3.grid(row = 1, column = 1)
   vl4.grid(row = 1, column = 2)
   vl5.grid(row = 1, column = 3)
   vl6.grid(row = 1, column = 4)
   vl7.grid(row = 1, column = 5)
   vl8.grid(row = 1, column = 6)
   #D1 widget variables
   d1_name = StringVar()
   d1_units = StringVar()
   min_1 = DoubleVar()
   max_1 = DoubleVar()
   mn1 = 0
   mx1 = 0
   dim1_x = BooleanVar()
   dim1_y = BooleanVar()
   dim1_z = BooleanVar()
   #D2 widget variables
   d2_name = StringVar()
   d2_units = StringVar()
   min_2 = DoubleVar()
   max_2 = DoubleVar()
   mn2 = 0
   mx2 = 0
   dim2_x = BooleanVar()
   dim2_y = BooleanVar()
   dim2_z = BooleanVar()
   #D3 widget variables
   d3_name = StringVar()
   d3_units = StringVar()
   min_3 = DoubleVar()
   max_3 = DoubleVar()
   mn3 = 0
   mx3 = 0
   dim3_x = BooleanVar()
   dim3_y = BooleanVar()
   dim3_z = BooleanVar()
    
   #open the nc file
   ncid = Dataset(fn, mode='r') #open the source file
   #get a list of the dimensions in th efile
   nc_dims = [dim for dim in ncid.dimensions]
   # Dimensions of selected variable
   dd = ncid.variables[selected_var_name].dimensions 
   #create listof dimension names for variabe
   xyz = []
   for n in range(len(dd)):
      for dim in nc_dims:
         if dim in dd[n]:
            xyz.append(dim)
   
   #D1 widgets
   D1Name = Label(f3, textvariable = d1_name, height = 1, width = 10)
   D1Units = Label(f3, textvariable = d1_units, height = 1, width = 25)
   D1X = Checkbutton(f3, height = 1, width = 1, variable = dim1_x, onvalue = True, offvalue = False, command = Dims_callback)
   D1Y = Checkbutton(f3, height = 1, width = 1, variable = dim1_y, onvalue = True, offvalue = False, command = Dims_callback)
   D1Z = Checkbutton(f3, height = 1, width = 1, variable = dim1_z, onvalue = True, offvalue = False, command = Dims_callback)
   D1MIN = Scale(f3, orient=HORIZONTAL, length = 160, from_ = mn1, to = mx1, variable = min_1)
   D1MAX = Scale(f3, orient=HORIZONTAL, length = 160, from_ = mn1, to = mx1, variable = max_1)
   # place D1 widgets on frame 3
   D1Name.grid(row = 2, column = 0)
   D1Units.grid(row = 2, column = 1)
   D1X.grid(row = 2, column = 2)
   D1Y.grid(row = 2, column = 3)
   D1Z.grid(row = 2, column = 4)
   D1MIN.grid(row = 2, column = 5)
   D1MAX.grid(row = 2, column = 6)
   # disable z
   D1Z.configure(state='disabled')
      
   if len(xyz) > 1:
      # D2 widgets
      D2Name = Label(f3, textvariable = d2_name, height = 1, width = 10)
      D2Units = Label(f3, textvariable = d2_units, height = 1, width = 25)
      D2X = Checkbutton(f3, height = 1, width = 1, variable = dim2_x, onvalue = True, offvalue = False, command = Dims_callback)
      D2Y = Checkbutton(f3, height = 1, width = 1, variable = dim2_y, onvalue = True, offvalue = False, command = Dims_callback)
      D2Z = Checkbutton(f3, height = 1, width = 1, variable = dim2_z, onvalue = True, offvalue = False, command = Dims_callback)
      D2MIN = Scale(f3, orient=HORIZONTAL, length = 160, from_ = mn2, to = mx2, variable = min_2)
      D2MAX = Scale(f3, orient=HORIZONTAL, length = 160, from_ = mn2, to = mx2, variable = max_2)
      # place D2 widgets on frame 3
      D2Name.grid(row = 3, column = 0)
      D2Units.grid(row = 3, column = 1)
      D2X.grid(row = 3, column = 2)
      D2Y.grid(row = 3, column = 3)
      D2Z.grid(row = 3, column = 4)
      D2MIN.grid(row = 3, column = 5)
      D2MAX.grid(row = 3, column = 6)
      # disable z 
      D2Z.configure(state='disabled') 
   
      if len(xyz) == 3:
         #D3 widgets
         D3Name = Label(f3, textvariable = d3_name, height = 1, width = 10)
         D3Units = Label(f3, textvariable = d3_units, height = 1, width = 25)
         D3X = Checkbutton(f3, height = 1, width = 1, variable = dim3_x, onvalue = True, offvalue = False, command = Dims_callback)
         D3Y = Checkbutton(f3, height = 1, width = 1, variable = dim3_y, onvalue = True, offvalue = False, command = Dims_callback)
         D3Z = Checkbutton(f3, height = 1, width = 1, variable = dim3_z, onvalue = True, offvalue = False, command = Dims_callback)
         D3MIN = Scale(f3, orient=HORIZONTAL, length = 160, from_ = mn3, to = mx3, variable = min_3)
         D3MAX = Scale(f3, orient=HORIZONTAL, length = 160, from_ = mn3, to = mx3, variable = max_3)
         # place D3 widgets on frame 3
         D3Name.grid(row = 4, column = 0)
         D3Units.grid(row = 4, column = 1)
         D3X.grid(row = 4, column = 2)
         D3Y.grid(row = 4, column = 3)
         D3Z.grid(row = 4, column = 4)
         D3MIN.grid(row = 4, column = 5)
         D3MAX.grid(row = 4, column = 6)
         # enable 1z and 2z
         D1Z.configure(state='normal') 
         D2Z.configure(state='normal') 
         
   #D1 always present
   d1_name.set(xyz[0])
   dim1_x.set(True)
   dim1_y.set(False)
   dim1_z.set(False)
   #units
   try:
      d1_units.set(ncid.variables[xyz[0]].getncattr('units'))
   except:
      d1_units.set('1') 
   #min - limits
   try:      
      mn1 = ncid.variables[xyz[0]].getncattr('valid_min')
   except:
      try:
         mn1 = np.min(ncid.variables[xyz[0]][:]) 
      except:
            mn1 = 1      
   #max - limits 
   try:           
      mx1 = ncid.variables[xyz[0]].getncattr('valid_max')
   except:
      try: 
          mx1 = np.max(ncid.variables[xyz[0]][:])  
      except:
          mx1 = len(ncid.dimensions[xyz[0]])
      
   D1MIN.configure(from_= mn1)
   D1MIN.configure(to = mx1)
   D1MAX.configure(from_= mn1)
   D1MAX.configure(to = mx1)
   D1MIN.set(mn1)
   D1MAX.set(mx1)
   
   if len(xyz) > 1:
      #Dimension 2
      d2_name.set(xyz[1])
      dim1_x.set(True)
      dim1_y.set(False)
      dim1_z.set(False)
      dim2_x.set(False)
      dim2_y.set(True)
      dim2_z.set(False)
      #units
      try:
         d2_units.set(ncid.variables[xyz[1]].getncattr('units'))
      except:
         d2_units.set('1') 
      #min - limits
      try:      
         mn2 = ncid.variables[xyz[1]].getncattr('valid_min')
      except:
         try: 
            mn2 = np.min(ncid.variables[xyz[1]][:])  
         except:
            mn2 = 1
      #max - limits 
      try:           
         mx2 = ncid.variables[xyz[1]].getncattr('valid_max')
      except:
         try: 
            mx2 = np.max(ncid.variables[xyz[1]][:])
         except: 
            mx2 = len(ncid.dimensions[xyz[1]])
      
      D2MIN.configure(from_= mn2)
      D2MIN.configure(to = mx2)
      D2MAX.configure(from_= mn2)
      D2MAX.configure(to = mx2)
      D2MIN.set(mn2)
      D2MAX.set(mx2)
   
      if len(xyz) == 3:
         d3_name.set(xyz[2])
         dim1_x.set(True)
         dim1_y.set(False)
         dim1_z.set(False)
         dim2_x.set(False)
         dim2_y.set(True)
         dim2_z.set(False)
         dim3_x.set(False)
         dim3_y.set(False)
         dim3_z.set(True)
         
         #units
         try:
            d3_units.set(ncid.variables[xyz[2]].getncattr('units'))
         except:
            d3_units.set('1') 
         #min - limits
         try:      
            mn3 = ncid.variables[xyz[2]].getncattr('valid_min')
         except:
            try: 
               mn3 = np.min(ncid.variables[xyz[2]][:]) 
            except:
               mn3 = 1            
         #max - limits 
         try:           
            mx3 = ncid.variables[xyz[2]].getncattr('valid_max')
         except:
            try:
               mx3 = np.max(ncid.variables[xyz[2]][:]) 
            except:
               mx3 = len(ncid.dimensions[xyz[2]])
         
         D3MIN.configure(from_= mn3)
         D3MIN.configure(to = mx3)
         D3MAX.configure(from_= mn3)
         D3MAX.configure(to = mx3)
         D3MIN.set(mn2)
         D3MAX.set(mx2)   
            
   #close the nc file
   ncid.close()         
      
"""
   Selected varaible and supporting data saved to xlsx workbook with multiple sheets
      Global Attributes
      Variable Attributes
      Variable Data
"""
def extract_callback(selected_var_name):
   # get output file name and path and only proceed if valid
   viw.config(cursor="watch")
   # update to kae it active 
   viw.update()
    
   try:
      fn_out =  filedialog.asksaveasfilename(initialdir = "/", title = "Select nc file",filetypes = (("Comma Separated","*.xlsx"),("all files","*.*")))
   
      #create workbook
      workbook = xlsxwriter.Workbook(fn_out, {'nan_inf_to_errors': True})
   
      #create worksheets
      GA = workbook.add_worksheet('Global Attributes')
      VA = workbook.add_worksheet('Variable Attributes')
      VD = workbook.add_worksheet('Dependent Variable Data')
      VV = workbook.add_worksheet('Variable Data')
         
      #open the nc file
      ncid = Dataset(fn, mode='r') #open the source file
      """
         Stop NetCDF package using the valid min and max to mask the data
         also stops shortinef og integers
      """
      ncid.set_auto_maskandscale(False)
      # get the global attributes
      nc_attrs = ncid.ncattrs()
      # get the dimensions
      nc_dims = [dim for dim in ncid.dimensions]
      # Dimensions of selected variable
      dd = ncid.variables[selected_var_name].dimensions 
      #create listof dimension names for variabe
      xyz = []
      for n in range(len(dd)):
         for dim in nc_dims:
            if dim in dd[n]:
               xyz.append(dim)         
        
      # Global Attribute
      # zero column and row pointers
      row = 0
      col = 0
      for nc_attr in nc_attrs:
         GA.write(row, col, nc_attr)
         try:
            GA.write(row, col + 1, ncid.getncattr(nc_attr))
         except:
            pass
         row += 1
        
      # Variable Attributs
      # zero column and row pointers
      row = -1
      col = 0
      #Dimensional variables
      for n in range(len(xyz)):
         row += 1
         #Variable name
         VA.write(row, col, "{}".format(xyz[n]))
              
         row += 1
         #Variable dimensions
         VA.write(row, col+1, "Dimensions")
         try:
            VA.write(row, col+2, "{}".format(ncid.variables[xyz[n]].dimensions))
         except:
            pass
         
         row += 1
         #Variable datatype
         VA.write(row, col+1, "Type")
         try:
            VA.write(row, col+2, "{}".format(ncid.variables[xyz[n]].dtype))
         except:
            pass
         
         row += 1
         #Variable datatype
         VA.write(row, col+1, "Shape")
         try:
            VA.write(row, col+2, "{}".format(ncid.variables[xyz[n]].shape))
         except:
            pass
         
         try:   
            for ncattr in ncid.variables[xyz[n]].ncattrs():
               row +=1
               VA.write(row, col+1, "{}".format(ncattr))
               VA.write(row, col+2, "{}".format(ncid.variables[xyz[n]].getncattr(ncattr)))
         except:
            pass
      
      #Selected variable  
      row += 1
      #Variable name
      VA.write(row, col, "{}".format(selected_var_name))
      
      row += 1
      #Variable dimensions
      VA.write(row, col+1, "Dimensions")
      VA.write(row, col+2, "{}".format(ncid.variables[selected_var_name].dimensions))
      
      row += 1
      #Variable datatype
      VA.write(row, col+1, "Type")
      VA.write(row, col+2, "{}".format(ncid.variables[selected_var_name].dtype))
      
      row += 1
      #Variable datatype
      VA.write(row, col+1, "Shape")
      VA.write(row, col+2, "{}".format(ncid.variables[selected_var_name].shape))
      
      for ncattr in ncid.variables[selected_var_name].ncattrs():
         row +=1
         VA.write(row, col+1, "{}".format(ncattr))
         VA.write(row, col+2, "{}".format(ncid.variables[selected_var_name].getncattr(ncattr)))  
      
      # Data
      # zero column and row pointers
      row = 0
      col = -1
      #Dimensional variable 
      for n in range(len(xyz)):
         col += 1
         row = 0
         # Variable name as column title on row 0
         VD.write(row, col, "{}".format(xyz[n]))
         try:# add data row by row in same coumn
            dd = np.array(ncid.variables[xyz[n]][:])
         except:
            dd = np.arange(len(ncid.dimensions[xyz[n]]))
         for m in range(len(dd)):
            row += 1
            VD.write(row, col, dd[m])
      
      # selected variable name an column title
      VV.write(0, 0, "{}".format(selected_var_name))
      if len(xyz) == 1:
         #1D
         row = 0
         col = 0
         dd = np.array(ncid.variables[selected_var_name][:])
         for m in range(len(dd)):
            row += 1
            VV.write(row, col, dd[m])
      if len(xyz) == 2:
         #2D
         row = 0
         dd = np.array(ncid.variables[selected_var_name][:][:])      
         xx = dd.shape
         for m in range(xx[0]):
            col = -1
            row += 1
            for mn in range(xx[1]):
               col += 1
               VV.write(row, col, dd[m,mn])
      if len(xyz) == 3:
         #3D
         row = 1
         dd = np.array(ncid.variables[selected_var_name][:][:][:])      
         xx = dd.shape
         for ij in range(xx[2]):#blocks
            col = 0
            VV.write(row, col, ij)  
            for m in range(xx[0]):#rows
               col = 0
               row += 1
               for mn in range(xx[1]):#cols
                  col += 1
                  VV.write(row, col, dd[m,mn,ij])
            row += 2
      # close nc file
      ncid.close()
      
      # close workbook   
      workbook.close()
   except:
      # if an error occurs give message in popup box
      message = "Unable to save file:\n{}".format(fn_out)
      messagebox.showerror("Extract a variable", message)   
      
   #return the cursur back to normal"
   viw.config(cursor="")
   viw.update()
   
   # Show message in popup box to say sav is complete
   message = "File:{} saved.".format(fn_out)
   messagebox.showinfo("Extract a variable", message)
       
"""
   This funstion creates a tabbed child window
   Three tabs
        Globa Attributes, Dimensions, Variables
   Varibles list is selectable and bound to b1single clicked
   Attributes displayed of variable selected
   YScroll bar for each tab - only appears if required    
""" 
def view_callback():
   """
      Local function to handle what happens when a variable is selected       
   """
   def LB3_select(event):
      # make the cursur show the swirl while it busy
      # note it only applies to when the cursur is ober the specific widget
      LB3.config(cursor="watch")
      # update to kae it active 
      LB3.update()
      
      # make the name of the variable a global varibale
      global selected_var_name
      ncid = Dataset(fn, mode='r') #open the source file
      """
         Stop NetCDF package using the valid min and max to mask the data
         also stops shortinef og integers
      """
      ncid.set_auto_maskandscale(False)
      # get the name of the variable selected
      w = event.widget
      s = w.curselection()
      p = w.get(s[0])
      selected_var_name = p
      # clean out any text in T4
      T4.delete("1.0", END)
      # Variable name attributes
      message = "Name: {}\n".format(p)      
      T4.insert(END, message)
      #Variable dimensions
      message = "Dimensions:  {}\n".format(ncid.variables[p].dimensions)      
      T4.insert(END, message)
      # Variable datatype
      message = "Type: {}\n".format(ncid.variables[p].dtype) 
      T4.insert(END, message)       
      # print all the variable attributes
      for ncattr in ncid.variables[p].ncattrs():
         message = "{}: {}\n".format(ncattr, ncid.variables[p].getncattr(ncattr))
         T4.insert(END, message)
      
      #fill the data window
      # clean out the text widget beofre starting
      T5.delete("1.0", END)   
      # get the data    
      try:
         dd = ncid.variables[p][:]
      except: 
         dd = ncid.variables[p][:][:]
      finally:
         dd = ncid.variables[p][:][:][:]
      # get the shape of the data
      xx = dd.shape
      #if its 1D
      if len(xx) == 1:
         tot_rows = xx[0]
         tot_cols = 1
      # if its 2D   
      if len(xx) == 2:
         tot_rows = xx[0]
         tot_cols = xx[1]
             
      #column header   
      if len(xx)<3:
         message = "\t"
         for j in range(tot_cols):
            message = message + "{}\t".format(j)
         message = message + "\n"   
         T5.insert(END, message)
      
      if len(xx) == 1:
         for i in range(tot_rows):
            message = "{}\t{}\n".format(i, dd[i])
            T5.insert(END, message)
      if len(xx) == 2:
         for i in range(tot_rows): 
            message = "{}\t".format(i)
            for j in range(tot_cols):
               message = message + "{}\t".format(dd[i][j])     
            message = message + "\n"  
            T5.insert(END, message)      
      if len(xx) == 3:
         T5.insert(END, 'Cannot display 3D data')
    
      ncid.close() #close the source file 
      #return the cursur back to normal"
      LB3.config(cursor="")
      LB3.update()
          
   # create child window and make handle global
   global viw
   viw = Toplevel(root)
   # confgure child window
   viw.geometry('900x400+300+300')
   # stop child window being resized
   viw.resizable(0, 0)
   #disable tool window
   viw.title('AMOF NC Tools: Inspect File')
   viw.iconbitmap('AMOF.ico')
    
   #create tabbed frame
   tabControl = ttk.Notebook(viw) 
   tab1 = ttk.Frame(tabControl) 
   tab2 = ttk.Frame(tabControl) 
   tab3 = ttk.Frame(tabControl) 
   tab4 = ttk.Frame(tabControl)
   tabControl.add(tab1, text ='Global Attributes') 
   tabControl.add(tab2, text ='Dimensions') 
   tabControl.add(tab3, text ='Variables') 
   tabControl.add(tab4, text ='Data')
   tabControl.pack(expand = 1, fill ="both")
    
   #tab 1: Global Attributes
   S1 = Scrollbar(tab1)
   T1 = Text(tab1)
   S1.pack(side = RIGHT, fill = Y)
   T1.pack(expand = 1, side = LEFT, fill = 'both')
   S1.config(command = T1.yview)
   T1.config(yscrollcommand = S1.set)
   T1.configure(exportselection=0)#disbale export of text when selected
    
   #tab2: Dmensions
   T2 = Text(tab2)
   T2.pack(expand = 1, side = LEFT, fill = 'both')
   T2.configure(exportselection=0)#disbale export of text when selected
    
   #tab3: Varaibles
   S2 = Scrollbar(tab3)
   S2.pack(side = RIGHT, fill = Y)
   LB3 = Listbox(tab3, selectmode = SINGLE, width = 55)
   LB3.pack(expand = 1, side = LEFT, fill = Y, padx = 3, pady = 3)
   LB3.bind('<<ListboxSelect>>', LB3_select) 
   S2.config(command = LB3.yview)
   LB3.config(yscrollcommand = S2.set) 
   T4 = Text(tab3, width = 45)
   T4.pack(expand = 1, side = LEFT, fill = Y, padx = 3, pady = 3)
   T4.configure(exportselection=0)#disable export of text when selected  
   b2 = Button(tab3, text = "Plot", height = 2, width = 10, command = lambda: plot_callback(selected_var_name))
   b2.pack(side = LEFT, padx = 3, pady = 3)
   b3 = Button(tab3, text = "Extract", height = 2, width = 10, command = lambda: extract_callback(selected_var_name))
   b3.pack(side = LEFT, padx = 3, pady = 3)
   
   #tab4: data
   T5 = Text(tab4, wrap = "none")
   T5.pack(side = LEFT, fill = 'both')
   S3 = Scrollbar(tab4, orient=VERTICAL)
   S3.pack(side = RIGHT, fill = Y)
   S3.config(command = T5.yview)
   S4 = Scrollbar(tab4, orient=HORIZONTAL)
   S4.pack(side = BOTTOM, fill = X)
   S4.config(command = T5.xview)
   T5.config(yscrollcommand = S3.set)
   T5.config(xscrollcommand = S4.set)
   T5.configure(exportselection=0)#disbale export of text when selected
   
   #parse global attributes
   try:
      ncid = Dataset(fn, mode='r') #open the source file 
      T1.delete("1.0", END)
      nc_attrs = ncid.ncattrs()   
      try:
         for nc_attr in nc_attrs:
            message = "{}: {} \n".format(nc_attr, ncid.getncattr(nc_attr))
            T1.insert(END, message)
      except:
         pass
      ncid.close() #close the source file        
      
      #parse dimensions
      ncid = Dataset(fn, mode='r') #open the source file
      T2.delete("1.0", END)
      nc_dims = [dim for dim in ncid.dimensions]
      try:
         for dim in nc_dims:
            message = "Name: {}  Size: {} \n".format(dim, len(ncid.dimensions[dim]))
            T2.insert(END, message)
      except:
         pass   
      ncid.close() #close the source file         
   
      #parse variables
      ncid = Dataset(fn, mode='r') #open the source file
      nc_vars = [var for var in ncid.variables]     
      try:
         for var in nc_vars:
            LB3.insert(END, var)
      except:
         pass
      ncid.close() #close the source file 
   except:
      # if an error occurs give message in popup box
      message = "No file selcted"
      messagebox.showerror("Opening NC file", message)

"""
   Help - About
"""
def help_about():
   message = "AMOF_ncSuit: a python baced GUI to assist access to netCDF files."
   messagebox.showinfo("About", message)

"""
   Help - version
"""
def help_version():
   message = "September 2020: 1.0"
   messagebox.showinfo("Version", message)

"""
   Change working directory to where the source file is
"""   
try:
    os.chdir(os.path.dirname(__file__))
except:
    pass

"""   
   create root window
"""
root = Tk()
root.title('AMOF NC Tools')
root.geometry('500x200+100+100')
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.resizable(0, 0) #Don't allow resizing in the x or y direction
root.iconbitmap('AMOF.ico')

# file label
l1 = Label(root, text="File:", height = 2, width = 10)
l1.grid(column=0, row=0, padx = 3, pady = 3, sticky='ne')
# text container for file name
TT1 = Text(root, height=2, width = 50)
TT1.grid(column=1, row=0, padx = 3, pady = 3, sticky='nw')
TT1.configure(exportselection=0)#disbale export of text when selected
TT1.insert(END, "*.nc")
# summary label
l3 = Label(root, text="Summary:", height = 2, width = 10)
l3.grid(column=0, row=1, padx = 3, pady = 3, sticky='ne')
# text container for summary
TT2 = Text(root, height=10, width = 50)
TT2.grid(column=1, row=1, padx = 3, pady = 3, sticky='nw')
TT2.configure(exportselection=0)#disbale export of text when selected

# Menubar
menubar = Menu(root)
# File menu
filemenu = Menu(menubar, tearoff = 0)
filemenu.add_command(label = "Open", command = get_file)
filemenu.add_separator()
filemenu.add_command(label = "Close", command = close_file)
filemenu.add_separator()
filemenu.add_command(label = "Exit", command = root.quit)
menubar.add_cascade(label = "File", menu = filemenu)
# View Menu
viewmenu = Menu(menubar, tearoff = 0)
viewmenu.add_command(label = "Inspect File", command = view_callback)
menubar.add_cascade(label = "View", menu = viewmenu)
# Help Menu
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label = "Help")
helpmenu.add_separator()
helpmenu.add_command(label = "About", command = help_about)
helpmenu.add_command(label = "Version", command = help_version)
menubar.add_cascade(label = "Help", menu = helpmenu)

warnings.filterwarnings("ignore") #stop warning being printed
root.config(menu = menubar)
root.mainloop()