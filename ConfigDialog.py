# SVNManager config
# date : 2017/08/24

from PySide.QtGui import *

class ConfigDialog(QDialog):
	def __init__(self, parent, config):
		super(ConfigDialog, self).__init__(parent)
		self.resize(400, 0)
		self.config = config
		self.initUI()
	def initUI(self):
		mainLayout = QVBoxLayout()
		
		RootLayout = QHBoxLayout()
		RootLayout.addWidget(QLabel('RootPath', self))
		self.LERootPath = QLineEdit(self)
		self.LERootPath.setText(self.config.rootpath)
		RootLayout.addWidget(self.LERootPath)
		mainLayout.addLayout(RootLayout)
		
		RepoLayout = QHBoxLayout()
		RepoLayout.addWidget(QLabel('Repository', self))
		self.LERepo = QLineEdit(self)
		self.LERepo.setText(self.config.repository)
		RepoLayout.addWidget(self.LERepo)
		mainLayout.addLayout(RepoLayout)
		
		ShelveLayout = QHBoxLayout()
		ShelveLayout.addWidget(QLabel('ShelvePath', self))
		self.LEShelve = QLineEdit(self)
		self.LEShelve.setText(self.config.shelvepath)
		ShelveLayout.addWidget(self.LEShelve)
		mainLayout.addLayout(ShelveLayout)
		
		EditorLayout = QHBoxLayout()
		EditorLayout.addWidget(QLabel('Editor', self))
		self.LEEditorPath = QLineEdit(self)
		self.LEEditorPath.setText(self.config.editorpath)
		EditorLayout.addWidget(self.LEEditorPath)
		PBEditorPath = QPushButton('...', self)
		EditorLayout.addWidget(PBEditorPath)
		PBEditorPath.clicked.connect(self.browseEditorPath)
		mainLayout.addLayout(EditorLayout)
		
		IDLayout = QHBoxLayout()
		IDLayout.addWidget(QLabel('ID', self))
		self.LEID = QLineEdit(self)
		self.LEID.setText(self.config.user)
		IDLayout.addWidget(self.LEID)
		mainLayout.addLayout(IDLayout)
		
		PWLayout = QHBoxLayout()
		PWLayout.addWidget(QLabel('Password', self))
		self.LEPW = QLineEdit(self)
		self.LEPW.setEchoMode(QLineEdit.Password)
		self.LEPW.setText(self.config.password)
		PWLayout.addWidget(self.LEPW)
		mainLayout.addLayout(PWLayout)
		
		dialogButton = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		dialogButton.accepted.connect(self.accept)
		dialogButton.rejected.connect(self.reject)
		mainLayout.addWidget(dialogButton)
		
		self.setLayout(mainLayout)

	def browseEditorPath(self):
		filepath = QFileDialog.getOpenFileName(self, "Set EditorPath", '', 'Execution File (*.exe)')
		if filepath is not None and len(filepath[0]) > 0:
			self.LEEditorPath.setText(filepath[0])
		
	def accept(self):
		self.config.rootpath = self.LERootPath.text()
		self.config.repository = self.LERepo.text()
		self.config.shelvepath = self.LEShelve.text()
		self.config.editorpath = self.LEEditorPath.text()
		self.config.user = self.LEID.text()
		self.config.password = self.LEPW.text()
		self.config.save('SVNManager.Config.xml')
		super(ConfigDialog, self).accept()
		