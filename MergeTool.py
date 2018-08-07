# MergeTool
# date : 2017/08/30
import os
from PySide.QtGui import *
from threading import *
from PathLineEdit import *
import subprocess

class DiffThread(Thread):
	excludeNames = ['.svn']
	def __init__(self, pbWidget, svn, sourcepath, targetpath, filter, author):
		super(DiffThread, self).__init__()
		self.svn = svn
		self.source = sourcepath
		self.target = targetpath
		if filter is not None and len(filter) > 0:
			self.filters = filter.split(';')
			for filterIndex in range(len(self.filters)):
				if self.filters[filterIndex] == '*.*':
					self.filters.pop(filterIndex)
					break
				self.filters[filterIndex] = self.filters[filterIndex].replace('*', '')
		else:
			self.filters = None
		self.pb = pbWidget
		if author is not None and len(author) > 0:
			self.author = author.split(';')
		else:
			self.author = None

		self.result = None
		
		self.stopEvent = Event()
		
	def run(self):
		print 'Start diffThread'
		folderwalkerSource = os.walk(self.source)
		folderwalkerTarget = os.walk(self.target)
		self.sourceFolderList = list(folderwalkerSource)
		self.targetFolderList = list(folderwalkerTarget)
		self.pb.setUpdatesEnabled(False)
		self.pb.setMaximum(len(self.sourceFolderList))
		self.pb.setMinimum(0)
		self.pb.setValue(0)
		self.pb.setUpdatesEnabled(True)
		
		targetFolderItem = self.targetFolderList.pop(0)
		self.result = self.diffFolder(self.sourceFolderList[0], targetFolderItem)
			
	def stop(self):
		self.stopEvent.set()
		
	def diffFolder(self, folderItem, folderItemTarget):
		diffResult = []
		for folderName in folderItem[1]:
			if folderName in self.excludeNames:
				self.pb.setUpdatesEnabled(False)
				self.pb.setValue(self.pb.value()+1)
				self.pb.setUpdatesEnabled(True)
				continue
			folderFullPath = os.path.join(folderItem[0], folderName)
			folderRelPath = folderFullPath.replace(self.source + "\\", '')
			print 'Diff ' + folderRelPath
			
			targetFolderItem = None
			for targetFolderIndex in range(len(self.targetFolderList)):
				targetFolderRelPath = self.targetFolderList[targetFolderIndex][0].replace(self.target + "\\", '')
				if targetFolderRelPath == folderRelPath:
					targetFolderItem = self.targetFolderList.pop(targetFolderIndex)
					break
			if targetFolderItem is None:
				if self.author is None:
					newTreeItem = QTreeWidgetItem()
					newTreeItem.setText(0, 'Deleted')
					newTreeItem.setText(1, folderRelPath)
					diffResult.append(newTreeItem)
			else:
				sourceFolderItem = None
				for sourceFolderIndex in range(len(self.sourceFolderList)):
					if self.sourceFolderList[sourceFolderIndex][0] == folderFullPath:
						sourceFolderItem = self.sourceFolderList.pop(sourceFolderIndex)
						break
				if sourceFolderItem is not None:
					diffFolderResult = self.diffFolder(sourceFolderItem, targetFolderItem)
					if diffFolderResult is not None:
						diffResult.append(diffFolderResult)
		
		diffFileList = self.diffFiles(folderItem[0], folderItem[2], folderItemTarget[0], folderItemTarget[2])
		for diffFileItem in diffFileList:
			diffResult.append(diffFileItem)
		
		self.pb.setUpdatesEnabled(False)
		self.pb.setValue(self.pb.value()+1)
		self.pb.setUpdatesEnabled(True)
		if len(diffResult) > 0:
			newTreeItem = QTreeWidgetItem()
			newTreeItem.setText(1, os.path.basename(folderItem[0]))
			checkDiffFlag = 0
			diffWord = 'None'
			for diffItem in diffResult:
				if diffItem.text(0) == 'Diff':
					if checkDiffFlag & ~(1<<0):
						diffWord = 'Complex'
					else:
						diffWord = 'Diff'
					checkDiffFlag = checkDiffFlag & (1<<0)
				if diffItem.text(0) == 'Deleted':
					if checkDiffFlag & ~(1<<1):
						diffWord = 'Complex'
					else:
						diffWord = 'Deleted'
					checkDiffFlag = checkDiffFlag & (1<<1)
				if diffItem.text(0) == 'Added':
					if checkDiffFlag & ~(1<<2):
						diffWord = 'Complex'
					else:
						diffWord = 'Deleted'
					checkDiffFlag = checkDiffFlag & (1<<2)
				newTreeItem.addChild(diffItem)
			diffItem.setText(0, diffWord)
			return newTreeItem
		return None
	
	def checkAuthor(self, path):
		if self.author is not None and len(self.author) > 0:
			fileHistory = self.svn.getSVNHistoryImmediately(path, limitCount=1)
			if len(fileHistory) > 0:
				if fileHistory[0][1] not in self.author:
					return False
			else:
				return True
		else:
			return True
	
	def diffFiles(self, sourcePath, sourceFiles, targetPath, targetFiles):
		result = []
		
		for sourceFile in sourceFiles:
			if self.filters is not None and len(self.filters) > 0:
				splitedFileName = os.path.splitext(sourceFile)
				if splitedFileName[1] not in self.filters:
					continue
			
			sourceFileFullPath = os.path.join(sourcePath, sourceFile)
			exists = False
			for targetFile in targetFiles:
				if targetFile == sourceFile:
					targetFileFullPath = os.path.join(targetPath, targetFile)
					sourceFileSize = os.path.getsize(sourceFileFullPath)
					targetFileSize = os.path.getsize(targetFileFullPath)
					if sourceFileSize != targetFileSize:
						if self.checkAuthor(sourceFileFullPath) == False:
							continue
						newTreeItem = QTreeWidgetItem()
						newTreeItem.setText(0, 'Diff')
						newTreeItem.setText(1, sourceFile)
						newTreeItem.setToolTip(1, sourceFileFullPath)
						result.append(newTreeItem)
					exists = True
					break
			if exists == False:
				if self.checkAuthor(sourceFileFullPath) == False:
					continue
				newTreeItem = QTreeWidgetItem()
				newTreeItem.setText(0, 'Deleted')
				newTreeItem.setText(1, sourceFile)
				result.append(newTreeItem)
		
		if self.author is None:
			for targetFile in targetFiles:
				exists = False
				for sourceFile in sourceFiles:
					if targetFile == sourceFile:
						exists = True
						break
				if exists == False:
					newTreeItem = QTreeWidgetItem()
					newTreeItem.setText(0, 'Added')
					newTreeItem.setText(1, targetFile)
					result.append(newTreeItem)				
					
		return result
		
class MergeTool(QWidget):
	def __init__(self, svn):
		super(MergeTool, self).__init__()
		self.initUI()
		self.currentThread = None
		self.svn = svn
		
		self.startTimer(30)

	def __del__(self):
		if self.currentThread is not None and self.currentThread.is_alive():
			self.currentThread.stop()
			self.currentThread.join()
		
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
		filterLayout = QHBoxLayout()
		filterLayout.addWidget(QLabel('Filter', self))
		self.LEFilter = QLineEdit()
		self.LEFilter.setText('*.*')
		filterLayout.addWidget(self.LEFilter)
		commandPanelLayout.addLayout(filterLayout)
		authorLayout = QHBoxLayout()
		authorLayout.addWidget(QLabel('Author', self))
		self.LEAuthor = QLineEdit()
		authorLayout.addWidget(self.LEAuthor)
		commandPanelLayout.addLayout(authorLayout)
		self.PBDiffCommand = QPushButton('Diff')
		self.PBDiffCommand.clicked.connect(self.runDiff)
		commandPanelLayout.addWidget(self.PBDiffCommand)
		self.PBDiffProg = QProgressBar()
		commandPanelLayout.addWidget(self.PBDiffProg)
		self.PBDiffProg.hide()
		commandPanelGroup.setLayout(commandPanelLayout)
		mainLayout.addWidget(commandPanelGroup)
		
		# DiffTreePanel
		self.diffTreeWidget = QTreeWidget()
		mainLayout.addWidget(self.diffTreeWidget)
		self.initDiffTreeWidget(self.diffTreeWidget)
		self.diffTreeWidget.itemDoubleClicked.connect(self.doubleClickedItem)
		
		self.setLayout(mainLayout)
		
	def initDiffTreeWidget(self, treeWidget):
		treeWidget.clear()
		diffTreeColumnNames = ['Type', 'Name']
		treeWidget.setColumnCount(len(diffTreeColumnNames))
		treeWidget.setHeaderLabels(diffTreeColumnNames)

	def setupDiffTree(self, result):
		self.initDiffTreeWidget(self.diffTreeWidget)
		self.diffTreeWidget.addTopLevelItem(result)
		
	def doubleClickedItem(self, item, column):
		for selectedItem in self.diffTreeWidget.selectedItems():
			selectedPath = selectedItem.toolTip(1)
			if selectedPath is None or len(selectedPath) == 0:
				continue
			relPath = selectedPath.replace(self.LESourcePath.text()+"\\", '')
			targetPath = os.path.join(self.LETargetPath.text(), relPath)
			print 'Diff ' + selectedPath + ' ' + targetPath
			subprocess.call(['TortoiseMerge', '/base:'+selectedPath, '/mine:'+targetPath])
		
	def timerEvent(self, event):
		if self.isVisible() is False:
			return
	
		if self.currentThread is not None and self.currentThread.is_alive() is False:
			self.setupDiffTree(self.currentThread.result)
			self.currentThread = None
	
		if self.currentThread is None:
			if self.PBDiffCommand.isVisible() == False:
				self.PBDiffCommand.setVisible(True)
			if self.PBDiffProg.isVisible():
				self.PBDiffProg.setVisible(False)
		else:
			if self.PBDiffCommand.isVisible():
				self.PBDiffCommand.setVisible(False)
			if self.PBDiffProg.isVisible() == False:
				self.PBDiffProg.setVisible(True)
		
	def browseSourcePath(self):
		filepath = QFileDialog.getExistingDirectory(self, "Set source path")
		if filepath is not None and len(filepath) > 0:
			self.LESourcePath.setText(filepath)
		
	def browseTargetPath(self):
		filepath = QFileDialog.getExistingDirectory(self, "Set target path")
		if filepath is not None and len(filepath) > 0:
			self.LETargetPath.setText(filepath)	
		
	def runDiff(self):
		if len(self.LESourcePath.text()) == 0 or len(self.LETargetPath.text()) == 0:
			return
		self.currentThread = DiffThread(self.PBDiffProg, self.svn, self.LESourcePath.text(), self.LETargetPath.text(), self.LEFilter.text(), self.LEAuthor.text())
		self.currentThread.start()