# SVNCmd
# Command of svn revisions
# date : 2017/07/19
import svn.local
import svn.remote
import svn.exception
from threading import *
from SVNManagerConfig import *
from datetime import *
import warnings
warnings.filterwarnings('ignore', category=UnicodeWarning)

SVNCmdThreadMutex = Lock()
class SVNCmdThread(Thread):
	def __init__(self, client, cmd, arg=None, callback=None):
		super(SVNCmdThread, self).__init__()
		self.svnclient = client
		self.svncmd = cmd
		self.svnarg = arg
		self.resultCB = callback
	def run(self):
		result = None

		# SVNCmdThreadMutex.acquire()
		if self.svncmd == 'status':
			result = list(self.svnclient.status())
		elif self.svncmd == 'update':
			self.svnclient.update()
		elif self.svncmd == 'history':
			historyList = self.svnclient.log_default(limit=10)
			result = []
			try:
				for historyItem in historyList:
					result.append([historyItem.revision, historyItem.author, historyItem.msg])
			except svn.exception.SvnException:
				pass						
		if self.resultCB is not None:
			self.resultCB(result)
		# SVNCmdThreadMutex.release()

class SVNCmd():
	mutexForCmdPool = Lock()
	historyCmdPool = []
	def __init__(self, config):
		self.config = config
		self.initSVNList()
		self.historyList = None
		self.statusUpdateTime = 0
		self.modifyList = None
		self.historyUpdateTime = datetime.now()
		
	def initSVNList(self):
		if self.config.rootpath is None or len(self.config.rootpath) == 0:
			return
		self.svnLocalClient = svn.local.LocalClient(self.config.rootpath, username=self.config.user, password=self.config.password)
		self.statusUpdateTime = datetime.now()
		self.modifyList = None
		sctStatus = SVNCmdThread(client=self.svnLocalClient, cmd='status', callback=self.finishUpdateStatusList)
		sctStatus.start()
		
	def getSVNHistory(self, path):
		existThread = False
		for historyCmdPoolItem in self.historyCmdPool:
			if historyCmdPoolItem[0] == path:
				existThread = True
				break
	
		self.mutexForCmdPool.acquire()
		if len(self.historyCmdPool) > 1:
			del historyCmdPoolItem[1:]
	
		svnlc = svn.local.LocalClient(path, username=self.config.user, password=self.config.password)
		sctHistory = SVNCmdThread(client=svnlc, cmd='history', callback=self.finishGetSVNHistory)
		
		self.historyCmdPool.append([path, sctHistory])
		if len(self.historyCmdPool) == 1:
			self.historyCmdPool[0][1].start()
		self.mutexForCmdPool.release()
		
	def getSVNHistoryImmediately(self, path, limitCount=10):
		svnlc = svn.local.LocalClient(path, username=self.config.user, password=self.config.password)
		historyList = svnlc.log_default(limit=limitCount)
		result = []
		try:
			for historyItem in historyList:
				result.append([historyItem.revision, historyItem.author, historyItem.msg])
		except svn.exception.SvnException:
			pass									
		return result
		
	def finishUpdateStatusList(self, list):
		self.statusList = list
		self.modifyList = []
		for stitem in self.statusList:
			if stitem.type_raw_name == 'modified' or stitem.type_raw_name == 'added':
				self.modifyList.append(stitem)
		self.statusUpdateTime = datetime.now()
		print('Updated SVN status at ' + self.statusUpdateTime.strftime('%H:%M:%S'))

	def finishGetSVNHistory(self, historyList):
		self.historyList = historyList
		self.historyUpdateTime = datetime.now()
		print('Get SVN history at ' + self.historyUpdateTime.strftime('%H:%M:%S'))
		self.mutexForCmdPool.acquire()
		del self.historyCmdPool[0]
		self.mutexForCmdPool.release()
		if len(self.historyCmdPool) > 0:
			self.historyCmdPool[0][1].start()
		
	def update(self, path):
		localClient = svn.local.LocalClient(path, username=self.config.user, password=self.config.password)
		sctUpdate = SVNCmdThread(client=localClient, cmd='update', callback=self.finishUpdate)
		sctUpdate.start()
		
	def finishUpdate(self, result):
		print('SVN update finished')