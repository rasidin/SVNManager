# PathLineEdit
# brief : Qt util
# date : 2017/12/19
from PySide.QtGui import *

class PathLineEdit(QLineEdit):
	def __init__(self):
		super(PathLineEdit, self).__init__()
		self.setAcceptDrops(True)
		
	def dragEnterEvent(self, event):
		mime = event.mimeData()
		if mime.hasUrls():
			event.accept()
		else:
			event.ignore()
		
	def dropEvent(self, event):
		mime = event.mimeData()
		urllist = mime.urls()
		if len(urllist)>0:
			path = urllist[0].path()
			if path[0] == '/':
				path = path[1:]
			path = path.replace('/', "\\")
			self.setText(path)
