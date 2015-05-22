#Copyright(c) 2015, David Mans, Konrad Sobon
# @arch_laboratory, http://archi-lab.net, http://neoarchaic.net

import clr
import sys
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

import System
from System import Array
from System.Collections.Generic import *

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os.path
import os

appDataPath = os.getenv('APPDATA')
bbPath = appDataPath + r"\Dynamo\0.8\packages\Bumblebee\extra"
if bbPath not in sys.path:
	sys.path.Add(bbPath)

import bumblebee as bb

clr.AddReferenceByName('Microsoft.Office.Interop.Excel, Version=11.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c')
from Microsoft.Office.Interop import Excel

System.Threading.Thread.CurrentThread.CurrentCulture = System.Globalization.CultureInfo("en-US")
from System.Runtime.InteropServices import Marshal

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN

filePath = IN[0]
runMe = IN[1]
byColumn = IN[2]
data = IN[3]

def LiveStream():
	try:
		xlApp = Marshal.GetActiveObject("Excel.Application")
		xlApp.Visible = True
		xlApp.DisplayAlerts = False
		return xlApp
	except:
		return None

def SetUp(xlApp):
	xlApp.Visible = False
	xlApp.DisplayAlerts = False
	xlApp.ScreenUpdating = False
	return xlApp

def WriteData(ws, data, byColumn, origin):

	def FillData(x, y, x1, y1, ws, data, origin):
		if origin != None:
			x = x + origin[1]
			y = y + origin[0]
		else:
			x = x + 1
			y = y + 1
		if y1 != None:
			ws.Cells[x, y] = data[x1][y1]
		else:
			ws.Cells[x, y] = data[x1]
		return ws

	if any(isinstance(item, list) for item in data):
		for i, valueX in enumerate(data):
			for j, valueY in enumerate(valueX):
				if byColumn:
					FillData(j,i,i,j, ws, data, origin)
				else:
					FillData(i,j,i,j, ws, data, origin)
	else:
		for i, valueX in enumerate(data):
			if byColumn:
				FillData(i,0,i,None, ws, data, origin)
			else:
				FillData(0,i,i,None, ws, data, origin)
	return ws

def ExitExcel(filePath, xlApp, wb, ws):

	def CleanUp(_list):
		if isinstance(_list, list):
			for i in _list:
				Marshal.ReleaseComObject(i)
		else:
			Marshal.ReleaseComObject(_list)
		return None
	
	wb.SaveAs(str(filePath))
	xlApp.ActiveWorkbook.Close(False)
	xlApp.ScreenUpdating = True
	CleanUp([ws,wb,xlApp])
	return None

if runMe:
	message = None
	if LiveStream() == None:
		if os.path.isfile(str(filePath)):
			if not isinstance(data, list):
				xlApp = SetUp(Excel.ApplicationClass())
				xlApp.Workbooks.open(str(filePath))
				wb = xlApp.ActiveWorkbook
				ws = xlApp.Sheets(data.SheetName())
				ws.Cells.ClearContents()
				ws.Cells.Clear()
				WriteData(ws, data.Data(), byColumn, data.Origin())
				ExitExcel(filePath, xlApp, wb, ws)
			else:
				xlApp = SetUp(Excel.ApplicationClass())
				xlApp.Workbooks.open(str(filePath))
				wb = xlApp.ActiveWorkbook
				sheetNameSet = set([x.SheetName() for x in data])
				for i in range(0,len(sheetNameSet),1):
					wb.Worksheets[i+1].Cells.ClearContents()
					wb.Worksheets[i+1].Cells.Clear()
				for i in data:
					ws = xlApp.Sheets(i.SheetName())
					WriteData(ws, i.Data(), byColumn, i.Origin())
				ExitExcel(filePath, xlApp, wb, ws)
		else:
			if not isinstance(data, list):
				xlApp = SetUp(Excel.ApplicationClass())
				wb = xlApp.Workbooks.Add()
				ws = wb.Worksheets[1]
				ws.Name = data.SheetName()
				WriteData(ws, data.Data(), byColumn, data.Origin())
				ExitExcel(filePath, xlApp, wb, ws)
			else:
				sheetNameSet = set([x.SheetName() for x in data])
				sheetNameList = list(sheetNameSet)
				xlApp = SetUp(Excel.ApplicationClass())
				wb = xlApp.Workbooks.Add()
				wb.Sheets.Add(After = wb.Sheets(wb.Sheets.Count), Count = len(sheetNameSet)-1)
				for i in range(0,len(sheetNameSet),1):
					wb.Worksheets[i+1].Name = sheetNameList[i]
				for i in data:
					ws = xlApp.Sheets(i.SheetName())
					WriteData(ws , i.Data(), byColumn, i.Origin())
				ExitExcel(filePath, xlApp, wb, ws)					
	else:
		message = "Close currently running Excel \nsession."
else:
	message = "Run Me is set to False. Please set \nto True if you wish to write data \nto Excel."

#Assign your output to the OUT variable
if message == None:
	OUT = "Success!"
else:
	OUT = '\n'.join('{:^35}'.format(s) for s in message.split('\n'))