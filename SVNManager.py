# Subversion Manager
# Coded by minseob
# Date : 2017/07/13
import sys
from PySide import QtGui
from PySide import QtCore
from PySide.QtGui import *
from SVNManagerConfig import *
from SVNCmd import *
from FileBrowserTree import *
from PendingList import *
from UpdateList import *
from HistoryList import *
from ShelveList import *
from MergeTool import *
from LinkTool import *
import TortoiseSVNCmd
from ConfigDialog import *

class SVNManagerWindow(QMainWindow):
	version = '0.1.170831'

	def __init__(self):
		super(SVNManagerWindow, self).__init__()
		self.config = SVNManagerConfig()
		self.config.load('SVNManager.Config.xml')
		self.svn = SVNCmd(self.config)
		self.initUI()
		
		if self.config.rootpath is None or len(self.config.rootpath) == 0:
			self.showConfigDialog()
	
	def initUI(self):
		self.setWindowTitle('SVNManager ver.' + self.version)
		self.statusBar().showMessage('Ready...')
		self.initMenuBar()
		self.initMainWidget()
	
	def initMenuBar(self):
		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		configAction = QAction('&Config', self)
		configAction.triggered.connect(self.showConfigDialog)
		fileMenu.addAction(configAction)
		exitAction = QAction('&Exit', self)
		exitAction.triggered.connect(sys.exit)
		fileMenu.addAction(exitAction)

		actionMenu = menubar.addMenu('&Action')
		refreshAction = QAction('&Refresh', self)
		refreshAction.setShortcut(QKeySequence('F5'))
		refreshAction.triggered.connect(self.refreshList)
		actionMenu.addAction(refreshAction)
		updateAllAction = QAction('&Update all', self)
		updateAllAction.setShortcut(QKeySequence('Shift+F5'))
		updateAllAction.triggered.connect(self.updateAll)
		actionMenu.addAction(updateAllAction)
		cleanupAction = QAction('Clean &Up', self)
		cleanupAction.triggered.connect(self.cleanup)
		actionMenu.addAction(cleanupAction)
		actionMenu.addSeparator();
		commitAction = QAction('&Commit', self)
		commitAction.setShortcut(QKeySequence('Ctrl+S'))
		commitAction.triggered.connect(self.commitFiles)
		actionMenu.addAction(commitAction)
		diffAction = QAction('&Diff', self)
		diffAction.setShortcut(QKeySequence('Ctrl+D'))
		diffAction.triggered.connect(self.diffFile)
		actionMenu.addAction(diffAction)
		
		helpMenu = menubar.addMenu('&Help')
		aboutAction = QAction('&About', self)
		aboutAction.triggered.connect(self.showAboutDialog)
		helpMenu.addAction(aboutAction)

	def initMainWidget(self):
		mainWidget = QSplitter()
		mainWidget.setOrientation(Qt.Horizontal)
		# mainLayout = QHBoxLayout()
		# mainWidget.setLayout(mainLayout)
		
		self.mainFileBrowser = FileBrowserTree(self.config.rootpath, self.svn, self.config)
		self.mainFileBrowser.setWindowFlags(QtCore.Qt.SubWindow)
		sizeGrip = QSizeGrip(self.mainFileBrowser)
		mainWidget.addWidget(self.mainFileBrowser)
		mainWidget.setStretchFactor(0, 3)
		
		mainTabWidget = QTabWidget()
		mainWidget.addWidget(mainTabWidget)
		mainWidget.setStretchFactor(1, 7)
		
		mainTabWidget.addTab(self.initPendingWidget(), 'Pending')
		mainTabWidget.addTab(self.initUpdateWidget(), 'Update')
		mainTabWidget.addTab(self.initHistoryWidget(), 'History')
		mainTabWidget.addTab(self.initShelveWidget(), 'Shelve')
		mainTabWidget.addTab(self.initMergeWidget(), 'Merge')
		mainTabWidget.addTab(self.initLinkWidget(), 'Link')
		
		self.setCentralWidget(mainWidget)
				
	def initPendingWidget(self):
		self.pendingList = PendingList(self.svn, 'SVNManager.Pending.xml')
		return self.pendingList
		
	def initUpdateWidget(self):
		self.updateList = UpdateList()
		return self.updateList
		
	def initHistoryWidget(self):
		historyWidget = HistoryList(self.svn)
		return historyWidget
		
	def initShelveWidget(self):
		shelveWidget = ShelveList(self.svn)
		return shelveWidget
		
	def initMergeWidget(self):
		diffWidget = MergeTool(self.svn)
		return diffWidget
		
	def initLinkWidget(self):
		linkWidget = LinkTool()
		return linkWidget
		
	def showConfigDialog(self):
		configDialog = ConfigDialog(self, self.config)
		configDialog.setModal(True)
		configDialog.show()
		if configDialog.result() == 0:
			self.mainFileBrowser.setRootPath(self.config.rootpath)
			self.svn.initSVNList()
	def showAboutDialog(self):
		QMessageBox.about(self, 'SVNManager', 'SVNManager version.'+self.version+'\nCreated by minseob')
	
	def refreshList(self):
		self.pendingList.resetPendingList()
		
	def updateAll(self):
		TortoiseSVNCmd.run('update', [['path', self.config.rootpath]])
			
	def cleanup(self):
		TortoiseSVNCmd.run('cleanup', [['path', self.config.rootpath]])
			
	def commitFiles(self):
		self.pendingList.commitFile()
			
	def diffFile(self):
		self.pendingList.diffSelectedFiles()
		
def main():
	app = QtGui.QApplication(sys.argv)
	w = SVNManagerWindow()
	w.resize(800, 600)
	w.show()
	sys.exit(app.exec_())	
	
if __name__ == '__main__':
	main()