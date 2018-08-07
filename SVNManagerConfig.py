#SVNManager Configuration
#Date : 2017/07/14
import sys
import os
import xml.etree.ElementTree as ET
import base64
from Crypto import Random
from Crypto.Cipher import AES

class SVNManagerConfig():
	cryptokey = 'SVNManagerMinseob201708300000000' # 32
	def _pad(self, s):
		return s + (len(self.cryptokey) - len(s) % len(self.cryptokey)) * chr(len(self.cryptokey) - len(s) % len(self.cryptokey))

	def _unpad(self, s):
		return s[:-ord(s[len(s)-1:])]

	def encrypt(self, raw):
		raw = self._pad(raw)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.cryptokey, AES.MODE_CBC, iv)
		return base64.b64encode(iv + cipher.encrypt(raw))

	def decrypt(self, enc):
		enc = base64.b64decode(enc)
		iv = enc[:AES.block_size]
		cipher = AES.new(self.cryptokey, AES.MODE_CBC, iv)
		return self._unpad(cipher.decrypt(enc[AES.block_size:]))
	
	def load(self, filepath):
		if os.path.exists(filepath) is False:
			self.rootpath = ''
			self.repository = ''
			self.editorpath = ''
			self.user = ''
			self.password = ''
			return
		xmlData = ET.parse(filepath)
		root = xmlData.getroot()
		svnRootPathNode = root.find('rootpath')
		if svnRootPathNode is not None:
			self.rootpath = svnRootPathNode.text
		else:
			self.rootpath = ''
		svnRepositoryNode = root.find('repository')
		if svnRepositoryNode is not None:
			self.repository = svnRepositoryNode.text
		else:
			self.repository = ''
		svnEditorPathNode = root.find('editorpath')
		if svnEditorPathNode is not None:
			self.editorpath = svnEditorPathNode.text
		else:
			self.editorpath = ''
		svnUserNode = root.find('user')
		if svnUserNode is not None:
			self.user = self.decrypt(svnUserNode.text)
		else:
			self.user = ''
		svnPasswordNode = root.find('password')
		if svnPasswordNode is not None:
			self.password = self.decrypt(svnPasswordNode.text)
		else:
			self.password = ''
		
	def save(self, filepath):
		xmlData = None
		if os.path.exists(filepath) is False:
			rootElement = ET.Element('config')
			xmlData = ET.ElementTree(rootElement)
		else:
			xmlData = ET.parse(filepath)
		root = xmlData.getroot()
		svnRootPathNode = root.find('rootpath')
		if svnRootPathNode is None:
			svnRootPathNode = ET.SubElement(root, 'rootpath')
		svnRootPathNode.text = self.rootpath
		svnRepositoryNode = root.find('repository')
		if svnRepositoryNode is None:		
			svnRepositoryNode = ET.SubElement(root, 'repository')
		svnRepositoryNode.text = self.repository
		svnEditorPathNode = root.find('editorpath')
		if svnEditorPathNode is None:
			svnEditorPathNode = ET.SubElement(root, 'editorpath')
		svnEditorPathNode.text = self.editorpath
		svnUserNode = root.find('user')
		if svnUserNode is None:
			svnUserNode = ET.SubElement(root, 'user')
		svnUserNode.text = self.encrypt(self.user)
		svnPasswordNode = root.find('password')
		if svnPasswordNode is None:
			svnPasswordNode = ET.SubElement(root, 'password')
		svnPasswordNode.text = self.encrypt(self.password)
		xmlData.write(filepath)