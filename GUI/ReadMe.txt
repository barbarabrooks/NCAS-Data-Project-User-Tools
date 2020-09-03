Dependencies
	os
	tkinter 
	netCDF4
	numpy  
	xlsxwriter
	warnings
	matplotlib
	time

OS tested
	Windows 10
	Centos 7

Python Version
	Windows10: 3.8
	Centos7: 3.7
	Anaconda3 package manager used

Use
	python AMOF_ncSuit_v1.0.py
	python3 AMOF_ncSuit_v1.0.py

Notes
	For Windows10 file AMOF.ico must be in same folder as AMOR_ncSuit_v1.0.py source code

	For Centos7 use of favicons is not supported. AMOF.ico not supplied.

	This has not been test on any Mac OS but in principle the Centos7 package should work.

Overview
	AMOF_ncSuit is a GUI (graphical user interface) designed to aid inspection and visualisation of netCDF files produced by NCAS AMOF instrumentation. In principle any netCDF file can be opened and inspected using this interface but behaviour cannot be guaranteed. This interface allows the user to:
		* Use an open file dialogue box to select the target file
		* Inspect the global attributes, dimensions and variables defined in the file
		* Select a particular variable and inspect this variables attributes and the data associated with it. Note data inspection is limited to m x n matrices.
		* Plot a graph (and save to .png if required) of the selected variable.
		* Extract the selected variable and save to and .xlsx file.

	For full details on how to use the GUI see the associated user manual.
