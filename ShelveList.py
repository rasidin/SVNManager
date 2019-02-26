# ShelveList
# date : 2018/08/29
from PySide.QtGui import *
from PySide.QtCore import *

class ShelveListTree(QTreeWidget):
	def __init__(self):
		super(ShelveListTree, self).__init__()
		
	def initTree(self):
		self.clear()	

class ShelveList(QWidget):
	def __init__(self, svncmd):
		super(ShelveList, self).__init__()
		
		self.svn = svncmd
		self.shelveListTree = ShelveListTree()
		
		mainLayout = QVBoxLayout()
		userLayout = QHBoxLayout()
		userLayout.addWidget(QLabel('User', self))
		self.CBUser = QComboBox(self)
		userLayout.addWidget(self.CBUser)
		mainLayout.addLayout(userLayout)
		
		mainLayout.addWidget(self.shelveListTree)
		self.setLayout(mainLayout)
		
		self.initUserList()
		
	def initUserList(self):
		fileSystemModelUser = QFileSystemModel()
		fileSystemmodelUser.setRootPath(self.svn.config.shelvepath)
		