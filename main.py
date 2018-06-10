import serial
from tkinter import *
import _thread
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
import matplotlib.animation as animation
from matplotlib import style
style.use("ggplot")

gyroData = []
accelData = []
pressureData = []
altitudeData = []
orientationData = []
gpsData = []
root = Tk()

class SyntaxParser():
    prevTime = 0
    prevSyntax = None
    START_LINE = '@{'
    END_LINE = '}@'
    TIMING = ';'
    GYRO_SYNTAX = ["GX:", "GY:", "GZ:", "TS:"]
    ACCEL_SYNTAX = ["AX:", "AY:", "AZ:", "TS:"]
    ORIENTATION_SYNTAX = ["OX:", "OY:", "OZ:", "TS:"]
    PRESSURE_SYNTAX = ["PS:", "TS:"]
    ALTITUDE_SYNTAX = ["PA:", "TS:"]

    def parseLine(self, line):
        print(line)
        toAppend = 0.0
        syntax = self.getSyntax(line)
        data = []
        startIndex = line.index(self.START_LINE)
        endIndex = line.index(self.END_LINE)
        if self.goodLine(line):
            for i in range(0, len(syntax)):
                if(i < len(syntax)-1):
                    toAppend = float(line[line.index(syntax[i])+3:line.index(syntax[i+1])-1])
                else:
                    toAppend = float(line[line.index(syntax[i])+3:endIndex])
                    if toAppend <= self.prevTime and syntax == self.prevSyntax:
                        return None
                    self.prevTime = toAppend
                data.append(toAppend)
                self.prevSyntax = syntax
            return data
        else: return None

    def getSyntax(self, line):
        startIndex = line.index(self.START_LINE)
        testSyntax = line[startIndex+2:startIndex+5]
        if(testSyntax == self.GYRO_SYNTAX[0]):
            return self.GYRO_SYNTAX
        elif(testSyntax == self.ACCEL_SYNTAX[0]):
            return self.ACCEL_SYNTAX
        elif(testSyntax == self.ORIENTATION_SYNTAX[0]):
            return self.ORIENTATION_SYNTAX
        elif(testSyntax == self.PRESSURE_SYNTAX[0]):
            return self.PRESSURE_SYNTAX
        elif(testSyntax == self.ALTITUDE_SYNTAX[0]):
            return self.ALTITUDE_SYNTAX

    def goodLine(self, line):
        startIndex = line.index(self.START_LINE)
        endIndex = line.index(self.END_LINE)
        syntax = self.getSyntax(line)
        timingCount = self.getTimingCount(line)
        if startIndex is not None and endIndex is not None and syntax is not None:
            if timingCount is len(syntax)-1:
                return True
        return False

    def getTimingCount(self, line):
        count = 0;
        for i in line:
            if i is self.TIMING:
                count += 1
        return count

class AltitudeMonitor():
    def __init__(self, port):
        self.ser = serial.Serial(port, 115200)

    def readData(self):
        return str(self.ser.readline())

    def isAvailable(self):
        return self.ser.is_open

    def kill(self):
        self.ser.close()

class GraphGUI():
    def __init__(self, master):
        master.columnconfigure(0,weight=1)
        master.rowconfigure(1,weight=1)
        self.master = master
        self.master.title("Rocket Data Analyzer")
        self.master.geometry('800x600')
        self.master.attributes("-zoomed", False)
        self.createGraph()
        self.plotGraph()
        self.master.bind("<Escape>", self.end_fullscreen)

    def end_fullscreen(self, event=None):
        self.state = False
        sys.exit()

    def createGraph(self):
        self.frame = Frame(self.master)
        self.frame.grid(column=0,row=1,columnspan=4, rowspan=3, sticky=N+W+E+S)
        self.f = Figure( figsize=(8, 7), dpi=80 )
        self.ax0 = self.f.add_axes( (0.05, .05, .90, .90), frameon=False)
        self.ax0.set_xlabel( 'Time (ms)' )
        self.ax0.set_ylabel( 'Thrust (N)' )
        self.ax0.grid(color='r',linestyle='-', linewidth=2)
        #self.ax0.plot(np.max(np.random.rand(100,10)*10,axis=1),"r-")
        self.canvas = FigureCanvasTkAgg(self.f, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        # self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.frame)
        # self.toolbar.grid(column = 0, row = 2, columnspan=2)
        self.toolbar.update()

    def plotGraph(self):
        xData = []
        yData = []
        for i in altitudeData:
            xData.append(i[1])
            yData.append(i[0])
        self.ax0.plot(xData,yData)
        self.ax0.get_lines()[0].set_color("blue")
        self.canvas.draw()

def runArduino():
    print("start thread")
    altMonitor = AltitudeMonitor("/dev/ttyACM0")
    parser = SyntaxParser()
    f = altMonitor.readData()
    while altMonitor.isAvailable():
        if parser.START_LINE in f and parser.END_LINE in f:
            sampleData = parser.parseLine(f)
            if(sampleData != None):
                altitudeData.append(sampleData)
                graph.plotGraph()
            f = altMonitor.readData()
        else:
            altMonitor.kill()

def main():
    _thread.start_new_thread(runArduino, ())
    root.mainloop()

graph = GraphGUI(root)
main()
