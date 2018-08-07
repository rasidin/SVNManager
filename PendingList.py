# PendingList
# date : 2017/07/18
from PySide.QtGui import *
from PySide.QtCore import *
from SVNCmd import *
from datetime import *
from uuid import *
import xml.etree.ElementTree as ET
import os
import TortoiseSVNCmd
import shutil

class PendingListDataItem():
	def __init__(self):
		self.name = ""
		self.id = '%x'%uuid1()
		self.files = []
		self.shelves = []
		self.opened = False
		self.commited = False

class PendingListData():
	def __init__(self, filepath):
		self.filepath = filepath
		self.id = '%x'%uuid1()
		self.load()
	def load(self):
		if os.path.exists(self.filepath) is False:
			return
		xmlData = ET.parse(self.filepath)
		rootElement = xmlData.getroot()
		
		self.list = []
		
		for pendingItem in rootElement.findall('pending'):
			listItem = PendingListDataItem()
			nameElement = pendingItem.find('name')
			if nameElement is not None:
				listItem.name = nameElement.text
			IDElement = pendingItem.find('id')
			openedElement = pendingItem.find('opened')
			if openedElement is not None:
				if openedElement.text == 'True':
					listItem.opened = True
				else:
					listItem.opened = False
			commitedElement = pendingItem.find('commited')
			if commitedElement is not None:
				if commitedElement.text == 'True':
					listItem.commited = True
				else:
					listItem.commited = False
			if IDElement is not None:
				listItem.id = IDElement.text
			filesElement = pendingItem.findall('files')
			if filesElement is not None:
				for fileElement in filesElement[0]:
					listItem.files.append(fileElement.text)
			shelvesElement = pendingItem.findall('shelves')
			if shelvesElement is not None and len(shelvesElement):
				for shelveElement in shelvesElement[0]:
					listItem.shelves.append(shelveElement.text)
			self.list.append(listItem)
		
	def save(self, treeWidget):
		if treeWidget.topLevelItemCount() < 2:
			return
	
		if os.path.exists(self.filepath):
			shutil.copyfile(self.filepath, self.filepath + '.backup')
	
		rootElement = ET.Element('pendinglist')
		xmlData = ET.ElementTree(rootElement)
		
		for itemIndex in range(treeWidget.topLevelItemCount()):
			topTreeItem = treeWidget.topLevelItem(itemIndex)
			if topTreeItem.text(treeWidget.TitleIndex) == 'default':
				continue
			subElement = ET.SubElement(rootElement, 'pending')
			subElementName = ET.SubElement(subElement, 'name')
			subElementName.text = topTreeItem.text(treeWidget.TitleIndex)
			subElementID = ET.SubElement(subElement, 'id')
			subElementID.text = topTreeItem.text(treeWidget.IDIndex)
			subElementOpened = ET.SubElement(subElement, 'opened')
			if topTreeItem.isExpanded():
				subElementOpened.text = 'True'
			else:
				subElementOpened.text = 'False'
			subElementCommited = ET.SubElement(subElement, 'commited')
			if topTreeItem.data(0, 0) == True:
				subElementCommited.text = 'True'
			else:
				subElementCommited.text = 'False'
			
			shelveFiles = []
			subElementFiles = ET.SubElement(subElement, 'files')
			for fileItemIndex in range(topTreeItem.childCount()):
				fileItem = topTreeItem.child(fileItemIndex)
				if fileItem.text(treeWidget.TitleIndex) == 'Shelves':
					for shelveChildIndex in range(fileItem.childCount()):
						shelveChildItem = fileItem.child(shelveChildIndex)
						shelveFiles.append(shelveChildItem.text(treeWidget.TitleIndex))
					continue
				subElementFile = ET.SubElement(subElementFiles, 'file')
				subElementFile.text = fileItem.text(treeWidget.TitleIndex)
		
			if len(shelveFiles) > 0:
				subElementShelves = ET.SubElement(subElement, 'shelves')
				for shelveFile in shelveFiles:
					subElementShelve = ET.SubElement(subElementShelves, 'shelve')
					subElementShelve.text = shelveFile
		
		xmlData.write(self.filepath)
	def addPendingList(self, name):
		newElement = ET.SubElement(self.rootElement, 'PendingItem')
		newItem = PendingListItem(name, newElement)
		self.list.append(newItem)
		return newItem

class PendingListEditDialog(QDialog):
	def __init__(self, parent = None):
		super(PendingListEditDialog, self).__init__(parent)
		
class PendingList(QTreeWidget):
	ColumnNames = ['ID', 'Title']
	IDIndex = 0
	TitleIndex = 1
	def __init__(self, svncmd, filepath):
		super(PendingList, self).__init__()
		self.fileSystemModel = QFileSystemModel()
		self.fileSystemModel.setRootPath(svncmd.config.rootpath)
		
		self.initPopupMenu()
		self.setColumnCount(len(self.ColumnNames))
		self.setHeaderLabels(self.ColumnNames)
		self.data = PendingListData(filepath)
		self.setSelectionMode(QAbstractItemView.ContiguousSelection)
		self.setDragEnabled(True)
		self.setAcceptDrops(True)
		self.svn = svncmd
		self.updateTime = None
		
		initializingItem = QTreeWidgetItem(self)
		initializingItem.setText(self.TitleIndex, 'Initializing...')
		self.addTopLevelItem(initializingItem)
		
		self.startTimer(1000)

	def __del__(self):
		self.data.save(self)
		
	def initPopupMenu(self):
		self.popupMenu = QMenu()
		popupNewList = self.popupMenu.addAction('Create new list')
		popupNewList.triggered.connect(self.createNewList)
		popupDeleteList = self.popupMenu.addAction('Delete from list')
		popupDeleteList.triggered.connect(self.deleteFromList)
		popupCopyFullPath = self.popupMenu.addAction('Copy full path')
		popupCopyFullPath.triggered.connect(self.copyFullPath)
		self.popupMenu.addSeparator()
		popupHistory = self.popupMenu.addAction('History')
		popupHistory.triggered.connect(self.historyFile)
		popupRevert = self.popupMenu.addAction('Revert')
		popupRevert.triggered.connect(self.revertFile)
		popupCommit = self.popupMenu.addAction('Commit')
		popupCommit.triggered.connect(self.commitFile)
		self.popupMenu.addSeparator()
		popupUnshelve = self.popupMenu.addAction('Unshelve')
		popupUnshelve.triggered.connect(self.unshelveFile)
		
	def timerEvent(self, event):
		if self.svn.statusUpdateTime != self.updateTime:
			self.initTree(self.svn.modifyList)
		
	def makeFileItem(self, parent, path, dragEnabled=False):
		outItem = QTreeWidgetItem(parent)
		outItem.setText(self.TitleIndex, path)
		outItem.setToolTip(0, path)
		outItem.setToolTip(1, path)
		fileIndex = self.fileSystemModel.index(path)
		if fileIndex.isValid():
			outItem.setIcon(0, self.fileSystemModel.fileIcon(fileIndex))
		flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
		if dragEnabled:
			flags = flags | Qt.ItemIsDragEnabled
		outItem.setFlags(flags)
		
	def initTree(self, modifyList):
		self.clear()
		if modifyList is None:
			updatingItem = QTreeWidgetItem(self)
			updatingItem.setText(self.TitleIndex, 'Updating...')
			self.addTopLevelItem(updatingItem)
			return
		
		self.updateTime = self.svn.statusUpdateTime
		
		treeItemDefault = QTreeWidgetItem(self)
		treeItemDefault.setText(self.IDIndex, 'None')
		treeItemDefault.setText(self.TitleIndex, 'default')
		treeItemDefault.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
		self.addTopLevelItem(treeItemDefault)
		
		modFilesName = []
		for moditem in modifyList:
			modTreeItem = self.makeFileItem(treeItemDefault, moditem.name, dragEnabled=True)
			modFilesName.append(moditem.name)
			
		for pendingItem in self.data.list:
			pendingTreeItem = QTreeWidgetItem(self)
			pendingTreeItem.setText(self.IDIndex, pendingItem.id)
			pendingTreeItem.setText(self.TitleIndex, pendingItem.name)
			pendingTreeItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled)
			for pendingFileItem in pendingItem.files:
				if pendingFileItem not in modFilesName:
					continue
				pendingFileTreeItem = self.makeFileItem(pendingTreeItem, pendingFileItem, dragEnabled=True)
				for defItemIndex in range(treeItemDefault.childCount()):
					defItem = treeItemDefault.child(defItemIndex)
					if defItem.text(self.TitleIndex) == pendingFileItem:
						treeItemDefault.removeChild(defItem)
						break
			if pendingTreeItem.childCount() == 0 and pendingItem.commited:
				self.takeTopLevelItem(self.topLevelItemCount()-1)
				continue
			pendingTreeItem.sortChildren(self.TitleIndex, Qt.AscendingOrder)
			shelveTreeItem = QTreeWidgetItem(pendingTreeItem)
			shelveTreeItem.setText(self.TitleIndex, 'Shelves')
			shelveTreeItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled)
			for pendingShelveItem in pendingItem.shelves:
				pendingShelveTreeItem = self.makeFileItem(shelveTreeItem, pendingShelveItem)
				
			pendingTreeItem.setExpanded(pendingItem.opened)

	def resetPendingList(self):
		self.data.save(self)
		self.data.load()
		self.svn.initSVNList()
				
	def mouseReleaseEvent(self, event):
		super(PendingList, self).mouseReleaseEvent(event)
		if event.button() == Qt.RightButton:
			self.popupMenu.popup(event.globalPos())
	
	def keyReleaseEvent(self, event):
		if event.key() == Qt.Key_Delete:
			self.deleteFromList()
	
	def addShelveFile(self, item, shelveItem):
		srcpath = item.text(self.TitleIndex)
		if os.path.isdir(srcpath):
			return
		for childIndex in range(shelveItem.childCount()):
			childItem = shelveItem.child(childIndex)
			if childItem.text(self.TitleIndex) == item.text(self.TitleIndex):
				return
		relpath = os.path.relpath(srcpath, self.svn.config.rootpath)
		tarpath = os.path.join('shelves', item.parent().text(self.IDIndex), relpath)
		if os.path.exists(os.path.dirname(tarpath)) is False:
			os.makedirs(os.path.dirname(tarpath))
		if os.path.exists(tarpath):
			os.remove(tarpath)
		shutil.copyfile(srcpath, tarpath)
		dragItemNew = self.makeFileItem(shelveItem, srcpath)
	
	def	removeShelveFile(self, item):
		relpath = os.path.relpath(item.text(self.TitleIndex), self.svn.config.rootpath)
		tarpath = os.path.join('shelves', item.parent().parent().text(self.IDIndex), relpath)
		if os.path.exists(tarpath):
			os.remove(tarpath)
		item.parent().removeChild(item)		
	
	def removeShelveFolder(self, item):
		removeFolders = []
		while item.childCount() > 0:
			shelveItem = item.child(0)
			self.removeShelveFile(shelveItem)
			relpath = os.path.relpath(shelveItem.text(self.TitleIndex), self.svn.config.rootpath)
			tarpath = os.path.join('shelves', item.parent().text(self.IDIndex), relpath)
			removeFolder = os.path.dirname(tarpath)
			alreadyExists = False
			for remFol in removeFolders:
				if remFol == removeFolder:
					alreadyExists = True
					break
			if alreadyExists == False:
				removeFolders.append(removeFolder)
		for removeFolder in removeFolders:
			os.removedirs(removeFolder)
	
	def unshelveItem(self, item):
		tarpath = item.text(self.TitleIndex)
		relpath = os.path.relpath(tarpath, self.svn.config.rootpath)
		srcpath = os.path.join('shelves', item.parent().parent().text(self.IDIndex), relpath)
		if os.path.exists(os.path.dirname(tarpath)) is False:
			os.makedirs(os.path.dirname(tarpath))
		if os.path.exists(tarpath):
			os.remove(tarpath)
		shutil.copyfile(srcpath, tarpath)
	
	def dropEvent(self, event):
		dragItems = self.selectedItems()
		fromRows = []
		for dragItem in dragItems:
			fromRows.append(self.indexFromItem(dragItem).row())
		droppedIndex = self.indexAt(event.pos())
		if droppedIndex.isValid() is False:
			event.setDropAction(Qt.IgnoreAction)
			return
		destItem = self.itemFromIndex(droppedIndex)
		destTopItemIndex = self.indexOfTopLevelItem(destItem)
		if destTopItemIndex >= 0:
			for dragItem in dragItems:
				if destItem.indexOfChild(dragItem) < 0:
					dragItem.parent().removeChild(dragItem)
					destItem.insertChild(destItem.childCount()-1, dragItem)
		elif destItem.text(self.TitleIndex) == 'Shelves':
			for dragItem in dragItems:
				self.addShelveFile(dragItem, destItem)

	def diffSelectedFiles(self):
		selectedItems = self.selectedItems()
		for item in selectedItems:	
			topLevelItemIndex = self.indexOfTopLevelItem(item)
			if topLevelItemIndex < 0: # child item
				TortoiseSVNCmd.run('diff', args=[['path', item.text(self.TitleIndex)]])
				
	def mouseDoubleClickEvent(self, event):
		self.diffSelectedFiles()
		super(PendingList, self).mouseDoubleClickEvent(event)		
	
	def createNewList(self):
		treeItemNew = QTreeWidgetItem(self)
		treeItemNew.setText(self.TitleIndex, 'new list')
		treeItemNew.setText(self.IDIndex, '%x'%uuid1())
		treeItemNew.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled)
		treeItemShelveNew = QTreeWidgetItem(treeItemNew)
		treeItemShelveNew.setText(self.TitleIndex, 'Shelves')
		treeItemShelveNew.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled)

	def deleteFromList(self):
		for selectedItem in self.selectedItems():
			topLevelItemIndex = self.indexOfTopLevelItem(selectedItem)
			if topLevelItemIndex >= 0: # top level
				topItem = self.topLevelItem(topLevelItemIndex)
				for childItemIndex in range(topItem.childCount()):
					childItem = topItem.child(childItemIndex)
					if childItem.text(self.TitleIndex) == 'Shelves':
						self.removeShelveFolder(childItem)
					
				self.takeTopLevelItem(topLevelItemIndex)
			else: # child
				if selectedItem.parent().text(self.TitleIndex) == 'Shelves':
					self.removeShelveFile(selectedItem)
				elif selectedItem.text(self.TitleIndex) == 'Shelves':
					while selectedItem.childCount() > 0:
						childItem = selectedItem.child(0)
						self.removeShelveFile(childItem)
				else:
					selectedItem.parent().removeChild(selectedItem)
					self.topLevelItem(0).addChild(selectedItem)

	def copyFullPath(self):
		clipboard = QApplication.clipboard()
		clipboard.setText(self.selectedItems()[0].text(self.TitleIndex))
					
	def historyFile(self):
		for selectedItem in self.selectedItems():
			TortoiseSVNCmd.run('log', [['path', selectedItem.text(self.TitleIndex)]])
	def revertFile(self):
		revertFileList = []
		for selectedItem in self.selectedItems():
			topLevelItemIndex = self.indexOfTopLevelItem(selectedItem)
			if topLevelItemIndex < 0: # child
				revertFileList.append(selectedItem.text(self.TitleIndex))
			else: # parent
				for childIndex in range(selectedItem.childCount()):
					childItem = selectedItem.child(childIndex)
					if childItem.text(self.TitleIndex) != 'Shelves':
						revertFileList.append(childItem.text(self.TitleIndex))
					
		if len(revertFileList) > 0:
			TortoiseSVNCmd.run('revert', args=[['path', '*'.join(revertFileList)]])
			self.resetPendingList()
	def commitFile(self):
		commitMessage = ""
		commitFileList = []
		for selectedItem in self.selectedItems():
			topLevelItemIndex = self.indexOfTopLevelItem(selectedItem)
			if topLevelItemIndex < 0: # child
				commitFileList.append(selectedItem.text(self.TitleIndex))
			else: # parent
				commitMessage = selectedItem.text(self.TitleIndex)
				selectedItem.setData(0, 0, True)
				for childIndex in range(selectedItem.childCount()):
					childItem = selectedItem.child(childIndex)
					if childItem.text(self.TitleIndex) != 'Shelves':
						commitFileList.append(childItem.text(self.TitleIndex))
					
		if len(commitFileList) > 0:
			TortoiseSVNCmd.run('commit', args=[['logmsg', '"'+commitMessage+'"'],['path', '*'.join(commitFileList)]])
			self.resetPendingList()
	
	def unshelveFile(self):
		for selectedItem in self.selectedItems():
			if selectedItem.text(self.TitleIndex) == 'Shelves':
				for childindex in range(selectedItem.childCount()):
					childItem = selectedItem.child(childindex)
					self.unshelveItem(childItem)
			elif selectedItem.parent().text(self.TitleIndex) == 'Shelves':
				self.unshelveItem(selectedItem)
		self.svn.initSVNList()