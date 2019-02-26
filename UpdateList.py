# UpdateList
# date : 2018/08/13
from PySide.QtGui import *
from PySide.QtCore import *

class UpdateList(QWidget):
	def __init__(self):
		super(UpdateList, self).__init__()
		self.initUI()
		
	def initUI(self):
		mainLayout = QVBoxLayout()
		toolbarGroup = QGroupBox()
		toolbarLayout = QHBoxLayout()
		btnAddGroup = QPushButton('Add')
		toolbarGroup.setLayout(toolbarLayout)
		
		self.setLayout(mainLayout)