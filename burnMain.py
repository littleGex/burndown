import os
import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox, QFileDialog
import pandas as pd
import datetime
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class burnDown(QMainWindow):
    def __init__(self):
        super(burnDown, self).__init__()
        uic.loadUi('burndown.ui', self)
        self.setupUi()
        self.setMenu()
    
    def setupUi(self):
        #======================================================================
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        self.plotlayout.addWidget(self.toolbar)
        self.plotlayout.addWidget(self.canvas)
        
        #set up initial responses
        self.today = datetime.date.today()
        ty = str(self.today).split('-')[0]
        tm = str(self.today).split('-')[1]
        td = str(self.today).split('-')[2]
        
        self.todayYear.setText(ty)
        self.todayYear.setToolTip(self.todayYear.text())
        self.todayMonth.setText(tm)
        self.todayMonth.setText(self.todayMonth.text())
        self.todayDay.setText(td)
        self.todayDay.setToolTip(self.todayDay.text())
        
        self.startYear.setToolTip('Input timebox starting Year')
        self.startYear.setFocus()
        self.startYear.selectAll()
        self.startMonth.setToolTip('Input timebox starting Month')
        self.startDay.setToolTip('Input timebox starting Day')
        
        self.endYear.setToolTip('Input timebox ending Year')
        self.endMonth.setToolTip('Input timebox ending Month')
        self.endDay.setToolTip('Input timebox ending Day')
        
        self.estimate.setToolTip('Input estimate of effort')
        self.toDo.setToolTip('Input remaining to do effort')
        
        self.plot.setText('Plot burndown chart')
        self.plot.setToolTip("Plot")
        self.plot.setStyleSheet("border: 1px solid grey; border-radius: 3px;")
        self.plot.setMinimumSize(200, 20)
        self.plot.released.connect(self.run)
        
        self.legend.setText('Legend')
        self.grid.setText('Grid lines')

        #======================================================================
    def setMenu(self):
        #set up windows menubar
        mainMenu = self.menuBar()
        mainMenu.setNativeMenuBar(False) #needed for mac
        
        fileMenu = mainMenu.addMenu('File')
        dataMenu = mainMenu.addMenu('Data')
        
        new_session = QAction("New session", self)
        new_session.setShortcut("Ctrl+O")
        new_session.setStatusTip("Click to start new session")
        fileMenu.addAction(new_session)
        new_session.triggered.connect(self.newSession)
        
        plotting = QAction("Plot chart", self)
        plotting.setShortcut("Ctrl+B")
        plotting.setStatusTip("Click to Plot chart")
        fileMenu.addAction(plotting)
        plotting.triggered.connect(self.run)
        
        quit = QAction("Quit", self)
        quit.setShortcut("Ctrl+Q")
        quit.setStatusTip("Click to Exit")
        fileMenu.addAction(quit)
        quit.triggered.connect(self.close) 

        save_csv = QAction("Save dataframe", self)
        save_csv.setShortcut("Ctrl+C")
        save_csv.setStatusTip("Click to save dataframe")
        dataMenu.addAction(save_csv)
        save_csv.triggered.connect(self.saveCSV) 

        print = QAction("Print", self)
        print.setShortcut("Ctrl+P")
        print.setStatusTip("Click to print Plot")
        dataMenu.addAction(print)
        print.triggered.connect(self.Print)
        
        self.show()
            
        #======================================================================
    def close (self):
        choice = QMessageBox.question(self, 'Close',
                                            "Do you want to quit the application?",
                                            QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            print("Session closed")
            sys.exit()
        else:
            pass
        
        #======================================================================    
    def newSession (self):
        choice = QMessageBox.question(self, 'New Session',
                                            "Do you want to start a new session?",
                                            QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.startYear.setText('YYYY')
            self.startMonth.setText('MM')
            self.startDay.setText('DD')
            self.endYear.setText('YYYY')
            self.endMonth.setText('MM')
            self.endDay.setText('DD')
            self.estimate.clear()
            self.toDo.clear()
            self.tableWidget.setRowCount(0) #clear tablewidget
        else:
            pass
        
        #======================================================================    
    def saveCSV (self):
        #Save dataframe csv file to allow reload/reuse
        filename,_ = QFileDialog.getSaveFileName(self, "Save dataframe", "", "CSV files (*.csv)")
        self.df.to_csv(filename)
        
        #======================================================================    
    def Print (self):
        filename,_ = QFileDialog.getSaveFileName(self, "Save plots as PDF file", "", "Portable Document File (*.pdf)")
        if filename == "":
            return
        self.canvas.print_figure(filename)
        
        #======================================================================
    def run(self):
        def numOfDays(date1, date2): 
            return (date2-date1).days 
    
        # date1 = (int(self.startYear.text()), ',', int(self.startMonth.text()), ',', int(self.startDay.text()))
        date1 = datetime.datetime.strptime(self.startYear.text() + '-' + self.startMonth.text() + '-' + self.startDay.text(), "%Y-%m-%d").date()
        # date2 = (int(self.endYear.text()), ',', int(self.endMonth.text()), ',', int(self.endDay.text()))
        date2 = datetime.datetime.strptime(self.endYear.text() + '-' + self.endMonth.text() + '-' + self.endDay.text(), "%Y-%m-%d").date()
        days = numOfDays(date1, date2)
        print(days)
        
        est = int(self.estimate.text())
        toDo = int(self.toDo.text())
        
        if self.today > date2:
            QtWidgets.QMessageBox.information(self, 'Timebox', 'Todays date exceeds timebox')
            return
            print ('Todays date exceeds timebox')
        else:
            delta = numOfDays(date1, datetime.date.today())
            print (delta)
        
        increment = round(float((est-toDo)/delta),2)
        
        self.df = pd.DataFrame(columns=('Days','Estimate'))
        for i in range(days,0,-1):
            self.df.loc[i] = [i, int(est/days*i)]
        
        self.df.reset_index(drop=True, inplace=True)
        
        self.df['To_do'] = self.df.apply(lambda row: (est-(increment*row.name)) if (row['Days'] >= (days-delta)) else toDo,axis=1)
        
        self.write_df_to_qtable(self.df, self.tableWidget)
        
        #Plot data
        ax = self.figure.add_subplot(111)
        ax.clear()
        
        self.df.plot(y='Estimate', label='Estimate', legend=False, ax=ax)
        self.df.plot(y='To_do', label='To do', legend=False, ax=ax)
        ax.axvline(x=delta, color='red', linestyle='--', label='Today')

        # for tick in ax.get_xticklabels():
        #     tick.set_rotation(90)

        #Add or remove legend using checkbox
        if self.legend.isChecked():
            leg= ax.legend(prop={'size':8}, loc='center left', bbox_to_anchor=(1,0.5))

            if leg:
                leg.set_draggable(True)

        ax.set_title('Sprint burndown')
        ax.set_xlabel('Days')
        ax.set_xticks(self.df.index.tolist())
        ax.set_ylabel('Effort')

        #Add major and Minor gridlines
        # '-', '--', '-.', ':', 'solid', 'dashed', 'dashdot', 'dotted'

        if self.grid.isChecked():
            # Customize the major grid 
            ax.grid(which='major', linestyle=':', linewidth='0.5', color='grey')

            # Customize the minor grid
            ax.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')

        self.figure.tight_layout()
        plt.isinteractive()
        
        self.canvas.draw()
        
    # Takes a df and writes it to a qtable provided. df headers become qtable headers
    @staticmethod
    def write_df_to_qtable(df,table):
        headers = list(df)
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1])
        table.setHorizontalHeaderLabels(headers)        

        # getting data from df is computationally costly so convert it to array first
        df_array = df.values
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                table.setItem(row, col, QtWidgets.QTableWidgetItem(str(df_array[row,col])))
        
#======================================================================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = burnDown()
    window.show()
    sys.exit(app.exec_())