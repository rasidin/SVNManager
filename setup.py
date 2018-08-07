from distutils.core import setup
import py2exe

option = {
	'compressed': 1,
	"optimize" : 2,
	"bundle_files" : 3
}
setup(
	options = {'py2exe': option},
	windows=['SVNManager.py'],
	zipfile=None,
	)