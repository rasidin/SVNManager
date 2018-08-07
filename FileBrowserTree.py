#FileBrowserTree
#Date : 2017/07/14
import os
import time
from mutex import *
from PySide.QtGui import *
from PySide.QtCore import *
from SVNCmd import *
import TortoiseSVNCmd
import subprocess

class FileBrowserTree(QTreeView):
	def __init__(self, rootpath, svncmd, config):
		super(FileBrowserTree, self).__init__()
		self.svn = svncmd
		self.config = config
# FileSystemModel version {
		treeModel = QFileSystemModel()
		treeModel.setRootPath(rootpath)
		self.setModel(treeModel)
		self.setRootIndex(treeModel.index(rootpath))
		self.currentItem = None
# }
# TreeWidget version {
		# self.itemExpanded.connect(self.expandedItem)
		# self.itemClicked.connect(self.clickedItem)
		# self.initTree(rootpath)
# }
		self.initPopupMenu()
		self.initShortcut()
		
	def initTree(self, rootpath):
		rootItem = QTreeWidgetItem(self)
		rootItem.setText(0, os.path.basename(rootpath))
		rootItem.setToolTip(0, rootpath)
		self.addTopLevelItem(rootItem)

		self.updateChild(rootItem, rootpath)
		self.expandedItem(rootItem)
	def setRootPath(self, rootpath):
		self.model().setRootPath(rootpath)
		self.update()
	def initPopupMenu(self):
		self.popupMenu = QMenu()
		popupUpdate = self.popupMenu.addAction('Update')
		popupUpdate.triggered.connect(self.updateFolder)
		popupHistory = self.popupMenu.addAction('History')
		popupHistory.triggered.connect(self.historyItem)
		popupCleanUp = self.popupMenu.addAction('CleanUp')
		popupCleanUp.triggered.connect(self.cleanUp)
		self.popupMenu.addSeparator()
		popupAdd = self.popupMenu.addAction('Add')
		popupAdd.triggered.connect(self.addFile)
		self.popupMenu.addSeparator()
		popupOpenExplorer = self.popupMenu.addAction('Open with explorer')
		popupOpenExplorer.triggered.connect(self.openWithExplorer)
		popupOpenEditor = self.popupMenu.addAction('Open using editor')
		popupOpenEditor.triggered.connect(self.openUsingEditor)
	def initShortcut(self):
		copyShortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_V), self)
		copyShortcut.activated.connect(self.moveToClipboard)
		self.setShortcutEnabled(copyShortcut.id())
	def moveToClipboard(self):
		clipboard = QApplication.clipboard()
		mimeData = clipboard.mimeData()
		filepath = ''
		if mimeData.hasUrls():
			fileurls = mimeData.urls()
			filepath = fileurls[0].path()
		elif mimeData.hasText():
			filepath = mimeData.text()
		if len(filepath) > 0:
			if filepath[0] == '/':
				filepath = filepath[1:]
			relpath = os.path.relpath(filepath, self.config.rootpath)
			dirwords = relpath.split('\\')
			exppath = self.config.rootpath
			for dirword in dirwords:
				exppath = os.path.join(exppath, dirword)
				expTarIndex = self.model().index(exppath)
				if expTarIndex.isValid():
					self.setExpanded(expTarIndex, True)
				
			fileIndex = self.model().index(filepath)
			if fileIndex.isValid():
				self.scrollTo(fileIndex)
				self.selectionModel().select(fileIndex, QItemSelectionModel.SelectCurrent)
				print 'move to ' + filepath
		
	def selectedItems(self):
		selectionIndexes = self.selectionModel().selectedIndexes()
		output = []
		if len(selectionIndexes) > 0:
			itemData = self.model().filePath(selectionIndexes[0])
			output.append(itemData)
		return output
	def expandedItem(self, item):
		for childindex in range(item.childCount()):
			childitem = item.child(childindex)
			if os.path.isdir(childitem.toolTip(0)) is True:
				self.updateChild(childitem, childitem.toolTip(0))
	def clickedItem(self, item, column):
# TreeWidget version {
		# self.updateHistory(item.toolTip(0))
# }
# FileSystemModel version {
			self.updateHistory(item)
# }
	def updateChild(self, parentItem, dirpath):
		for childIndex in range(parentItem.childCount()):
			parentItem.removeChild(parentItem.child(0))
		files = os.listdir(dirpath)
		for file in files:
			# Ignore current dir
			if file[0] == '.':
				continue
			fileItem = QTreeWidgetItem(parentItem)
			fileItem.setText(0, file)
			fullpath = os.path.join(dirpath, file)
			fileItem.setToolTip(0, fullpath)
	def updateHistory(self, path):
		self.svn.getSVNHistory(path)
	def updateFolder(self):
		for selectedItem in self.selectedItems():
# TreeWidget version {
			# print('update ' + selectedItem.toolTip(0))
			# self.svn.update(selectedItem.toolTip(0))
# }
# FileSystemModel version {
			print 'update ' + selectedItem
			TortoiseSVNCmd.run('update', [['path', selectedItem]])
# }
	def historyItem(self):
		for selectedItem in self.selectedItems():
			TortoiseSVNCmd.run('log', [['path', selectedItem]])
	def addFile(self):
# FileSystemModel version {
		for selectedItem in self.selectedItems():
			TortoiseSVNCmd.run('add', [['path', selectedItem]])
# }
	def cleanUp(self):
		for selectedItem in self.selectedItems():
			TortoiseSVNCmd.run('cleanup', [['path', selectedItem]])
	def openWithExplorer(self):
		for selectedItem in self.selectedItems():
			cmd = 'explorer %s'%selectedItem.replace('/', '\\')
			print 'Open : ' + cmd
			subprocess.call(cmd)
	
	def openUsingEditor(self):
		if self.config.editorpath is None or len(self.config.editorpath) == 0:
			return
		for selectedItem in self.selectedItems():
			cmd = self.config.editorpath + ' %s'%selectedItem.replace('/', '\\')
			print 'Open : ' + cmd
			subprocess.call(cmd)		
	
	# events
	def mouseReleaseEvent(self, event):
		super(FileBrowserTree, self).mouseReleaseEvent(event)
		if event.button() == Qt.RightButton:
			self.popupMenu.popup(event.globalPos())
		elif event.button() == Qt.LeftButton:
			currentSelectedItems = self.selectedItems()
			if currentSelectedItems is not None and len(currentSelectedItems) > 0 and self.currentItem != currentSelectedItems[0]:
				self.currentItem = currentSelectedItems[0]
				self.clickedItem(self.currentItem, 0)