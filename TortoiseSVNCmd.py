# TortoiseSVNCmd
# date : 2017/08/21

import subprocess

def run(cmd, args=[]):
	fullcmd = 'tortoiseproc '
	fullcmd = fullcmd + '/command:' + cmd
	for arg in args:
		fullcmd = fullcmd + ' /' + arg[0] + ':' + arg[1]
	
	print 'run:' + fullcmd
	subprocess.call(fullcmd)