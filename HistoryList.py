# HistoryList
# date : 2017/07/19

from PySide.QtGui import *
from PySide.QtCore import *

class HistoryList(QTreeWidget):
	def __init__(self, svncmd):
		super(HistoryList, self).__init__()
		self.setColumnCount(3)
		self.svn = svncmd
		self.updateTime = None
		self.startTimer(1000)

	def timerEvent(self, event):
		if self.svn.historyUpdateTime != self.updateTime:
			self.initTree(self.svn.historyList)
			
	def initTree(self, historyList):
		self.clear()
		
		if historyList is None:
			return
			
		self.updateTime = self.svn.historyUpdateTime

		for historyText in historyList:
			historyTreeItem = QTreeWidgetItem(self)
			historyTreeItem.setText(0, '%d'%(historyText[0]))
			historyTreeItem.setText(1, historyText[1])
			historyTreeItem.setText(2, historyText[2])
			self.addTopLevelItem(historyTreeItem)
		