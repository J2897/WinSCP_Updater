# Released under the GNU General Public License version 3 by J2897.

def get_page(page):
	import urllib2
	source = urllib2.urlopen(page)
	return source.read()

def find_site_ver(page):
	T1 = page.find(target)
	if T1 == -1:
		return None, None
	T2 = page.find('>WinSCP ', T1)
	T3 = page.find('<', T2)
	T4 = page.find('winscp', T3)
	T5 = page.find('.exe', T4)
	return page[T2+8:T3], page[T4:T5+4]	# 5.1.5, winscp515setup.exe

def stop():
	import sys
	sys.exit()

target = 'Downloading WinSCP'
url = 'http://winscp.net/eng/download.php'
page = get_page(url)

site_version, FN = find_site_ver(page)
if site_version == None:
	stop()

import os
tmp = os.getenv('TEMP')
PF = os.getenv('PROGRAMFILES')

def clean(text):
	import re
	return re.sub('[^0-9]', '', text)

import win32api

try:
    info = win32api.GetFileVersionInfo(PF + '\\WinSCP\\WinSCP.exe', "\\")
    ms = info['FileVersionMS']
    ls = info['FileVersionLS']
    file_version = "%d.%d.%d.%d" % (win32api.HIWORD(ms), win32api.LOWORD (ms),
									win32api.HIWORD (ls), win32api.LOWORD (ls))
except:
    file_version = '0.0.0.0' # some appropriate default here.

# Check if the site_version numbers are in the file_version numbers...
if clean(file_version).find(clean(site_version)) != -1:
	# Yes:	Quit.
	stop()

# Now download and install the new file...

import urllib
url = 'http://downloads.sourceforge.net/project/winscp/WinSCP/' + site_version + '/' + FN
DL = tmp + '\\' + FN
urllib.urlretrieve(url, DL)

args = ' /SILENT /NORESTART'

def sub_proc(exe, args):
	import subprocess
	filepath = exe + args
	p = subprocess.Popen(filepath, shell=True, stdout = subprocess.PIPE)
	stdout, stderr = p.communicate()
	return p.returncode # is 0 if success

sub_proc(DL, args)
