# LinkTool
# brief : Make directory link
# date : 2017/12/19
import os
import shutil
import subprocess
from PySide.QtGui import *
from PySide.QtCore import *
from threading import *
from PathLineEdit import *

class LinkThread(Thread):
	def __init__(self, pbWidget, sourcePath, targetPath):
		super(LinkThread, self).__init__()
		self.sourcePath = sourcePath
		self.targetPath = targetPath
		self.pb = pbWidget
		
		if os.path.exists(self.targetPath):
			shutil.rmtree(self.targetPath)
		os.makedirs(self.targetPath)
		
	def run(self):
		print 'Start Link Process...'
		sourceFileList = list(os.walk(self.sourcePath))
		copySourceFileList = []
		for fileList in sourceFileList:
			for fileName in fileList[2]:
				copySourceFileList.append(os.path.join(fileList[0], fileName))
				targetDirName = fileList[0].replace(self.sourcePath, self.targetPath)
				if os.path.exists(targetDirName) is False:
					os.makedirs(targetDirName)
		self.pb.setMaximum(len(copySourceFileList))
		self.pb.setMinimum(0)
		self.pb.setValue(0)
		
		for filePath in copySourceFileList:
			sourceFilePath = filePath
			targetFilePath = filePath.replace(self.sourcePath, self.targetPath)
			print 'copy %s to %s ...'%(sourceFilePath, targetFilePath)
			shutil.copyfile(sourceFilePath, targetFilePath)
			self.pb.setUpdatesEnabled(False)
			self.pb.setValue(self.pb.value() + 1)
			self.pb.setUpdatesEnabled(True)
			
		shutil.rmtree(self.sourcePath)
		subprocess.Popen(['mklink', '/D', self.sourcePath, self.targetPath], shell=True)

class LinkList(QTableWidget):
	ColumnNames = ['Source', 'Target']
	def __init__(self):
		super(LinkList, self).__init__()	
		self.initPopupMenu()
		self.setColumnCount(len(self.ColumnNames))
		self.setHorizontalHeaderLabels(self.ColumnNames)
		
	def initPopupMenu(self):
		self.popupMenu = QMenu()
		popupUnlink = self.popupMenu.addAction('Unlink')
		popupUnlink.triggered.connect(self.unlink)
		
	def mouseReleaseEvent(self, event):
		super(LinkList, self).mouseReleaseEvent(event)
		if event.button() == Qt.RightButton:
			self.popupMenu.popup(event.globalPos())
	
	def keyReleaseEvent(self, event):
		if event.key() == Qt.Key_Delete:
			self.unlink()
	
	def addLinkedPath(self, srcPath, tarPath):
		self.insertRow(self.rowCount())
		self.setItem(self.rowCount()-1, 0, QTableWidgetItem(srcPath))
		self.setItem(self.rowCount()-1, 1, QTableWidgetItem(srcPath))
	
	def unlink(self):
		if len(self.selectedItems()) == 0:
			return
		if (QMessageBox.question(None, 'Unlink', 'Do you really want to unlink this??') == QMessageBox.Ok):
			for selectedItem in self.selectedItems():
				self.removeRow(self.row(selectedItem))

class LinkTool(QWidget):
	def __init__(self):
		super(LinkTool, self).__init__()
		self.initUI()

		self.currentThread = None
		self.startTimer(30)
		
	def initUI(self):
		mainLayout = QVBoxLayout()
		
		# CommandPanel
		commandPanelGroup = QGroupBox()
		commandPanelGroup.setTitle('Command')
		commandPanelLayout = QVBoxLayout()
		sourcePathLayout = QHBoxLayout()
		sourcePathLayout.addWidget(QLabel('Source', self))
		self.LESourcePath = PathLineEdit()
		sourcePathLayout.addWidget(self.LESourcePath)
		PBBrowserSource = QPushButton()
		PBBrowserSource.clicked.connect(self.browseSourcePath)
		sourcePathLayout.addWidget(PBBrowserSource)
		commandPanelLayout.addLayout(sourcePathLayout)
		targetPathLayout = QHBoxLayout()
		targetPathLayout.addWidget(QLabel('Target', self))
		self.LETargetPath = PathLineEdit()
		targetPathLayout.addWidget(self.LETargetPath)
		PBBrowserTarget = QPushButton()
		PBBrowserTarget.clicked.connect(self.browseTargetPath)
		targetPathLayout.addWidget(PBBrowserTarget)
		commandPanelLayout.addLayout(targetPathLayout)

		self.PBLinkCommand = QPushButton('Link')
		self.PBLinkCommand.clicked.connect(self.runLink)
		commandPanelLayout.addWidget(self.PBLinkCommand)
		self.PBLinkProg = QProgressBar()
		commandPanelLayout.addWidget(self.PBLinkProg)
		self.PBLinkProg.hide()

		commandPanelGroup.setLayout(commandPanelLayout)
		mainLayout.addWidget(commandPanelGroup)

		self.linkList = LinkList()
		mainLayout.addWidget(self.linkList)
		
		self.setLayout(mainLayout)

	def timerEvent(self, event):
		if self.isVisible() is False:
			return

		if self.currentThread is not None and self.currentThread.is_alive() is False:
			self.linkList.addLinkedPath(self.currentThread.sourcePath, self.currentThread.targetPath)
			self.currentThread = None
	
		if self.currentThread is None:
			if self.PBLinkCommand.isVisible() == False:
				self.PBLinkCommand.setVisible(True)
			if self.PBLinkProg.isVisible():
				self.PBLinkProg.setVisible(False)
		else:
			if self.PBLinkCommand.isVisible():
				self.PBLinkCommand.setVisible(False)
			if self.PBLinkProg.isVisible() == False:
				self.PBLinkProg.setVisible(True)

	def browseSourcePath(self):
		filepath = QFileDialog.getExistingDirectory(self, "Set source path")
		if filepath is not None and len(filepath) > 0:
			self.LESourcePath.setText(filepath)
		
	def browseTargetPath(self):
		filepath = QFileDialog.getExistingDirectory(self, "Set target path")
		if filepath is not None and len(filepath) > 0:
			self.LETargetPath.setText(filepath)	
	
	def runLink(self):
		sourcePath = self.LESourcePath.text()
		targetPath = self.LETargetPath.text()
		self.currentThread = LinkThread(self.PBLinkProg, sourcePath, targetPath)
		self.currentThread.start()
		