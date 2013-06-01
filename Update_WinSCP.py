# Released under the GNU General Public License version 3 by J2897.

def get_page(page):
	import urllib2
	source = urllib2.urlopen(page)
	return source.read()

title = 'WinSCP Updater'
target = 'Downloading WinSCP'
url = 'http://winscp.net/eng/download.php'

try:
	page = get_page(url)
except:
	page = None

def msg_box(message, box_type):
	import win32api
	user_input = win32api.MessageBox(0, message, title, box_type)
	return user_input

def stop():
	import sys
	sys.exit()

if page == None:
	msg_box('Could not download the page. You may not be connected to the internet.', 0)
	stop()

def find_site_ver(page):
	T1 = page.find(target)
	if T1 == -1:
		return None, None
	T2 = page.find('>WinSCP ', T1)
	T3 = page.find('<', T2)
	T4 = page.find('winscp', T3)
	T5 = page.find('.exe', T4)
	return page[T2+8:T3], page[T4:T5+4]	# 5.1.5, winscp515setup.exe

try:
	site_version, FN = find_site_ver(page)
except:
	site_version = None

if site_version == None:
	msg_box('The search target has not been found on the page. The formatting, or the text on the page, may have been changed.', 0)
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
    file_version = None

if file_version == None:
	msg_box('Cannot find the file version of the local WinSCP.exe file.', 0)
	stop()

# Check if the site_version numbers are in the file_version numbers...
if clean(file_version).find(clean(site_version)) != -1:
	# Yes:	Quit.
	stop()

# Check if WinSCP is running...
def find_proc(exe):
	import subprocess
	cmd = 'WMIC PROCESS get Caption'
	proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	for line in proc.stdout:
		if line.find(exe) != -1:
			return True

while find_proc('WinSCP.exe'):
	user_input = msg_box('There is a new version of WinSCP available. Please close WinSCP and press OK to continue.', 1)
	if user_input == 1:
		pass
	elif user_input == 2:
		stop()

# Now download and install the new file...
user_input = msg_box('If you have a WinSCP.ini file, back it up now and then press OK when you are ready to proceed with the update.', 1)
if user_input == 2:
	stop()

import urllib
url = 'http://downloads.sourceforge.net/project/winscp/WinSCP/' + site_version + '/' + FN
DL = tmp + '\\' + FN

try:
	urllib.urlretrieve(url, DL)
except:
	msg_box('Failed to download [' + FN + '] to [' + tmp + '].', 0)
	stop()

def sub_proc(exe, args):
	import subprocess
	filepath = exe + args
	p = subprocess.Popen(filepath, shell=True, stdout=subprocess.PIPE)
	stdout, stderr = p.communicate()
	return p.returncode # is 0 if success

args = ' /SILENT /NORESTART'

try:
	RC = sub_proc(DL, args)
except:
	RC = None

if RC == None:
	msg_box('Failed to execute [' + FN + '].', 0)
	stop()
elif RC == 0:
	msg_box('Successfully updated from version [' + file_version + '] to version [' + site_version + '].', 0)
	stop()
else:
	msg_box('Successfully executed [' + FN + ']. But the installation appears to have failed.', 0)
