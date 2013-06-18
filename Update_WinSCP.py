# Released under the GNU General Public License version 3 by J2897.

def get_page(page):
	import urllib2
	source = urllib2.urlopen(page)
	return source.read()

title = 'WinSCP Updater'
target = 'Downloading WinSCP'
url = 'http://winscp.net/eng/download.php'

print 'Running:		' + title
print 'Target:			' + target
print 'URL:			' + url

try:
	page = get_page(url)
except:
	page = None
else:
	print 'Got page...'

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
	msg_box('Could not search the page.', 0)
	stop()
else:
	print 'Found:			' + site_version

if site_version == None:
	msg_box('The search target has not been found on the page. The formatting, or the text on the page, may have been changed.', 0)
	stop()

import os
tmp = os.getenv('TEMP')
PF = os.getenv('PROGRAMFILES')
WinSCP_exe = PF + '\\WinSCP\\WinSCP.exe'
DL = tmp + '\\' + FN
command = [DL, '/SILENT', '/NORESTART']

def DL_file():
	import urllib
	url = 'http://downloads.sourceforge.net/project/winscp/WinSCP/' + site_version + '/' + FN
	urllib.urlretrieve(url, DL)

def sub_proc(command):
	import subprocess
	p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	stdout, stderr = p.communicate()
	return p.returncode # is 0 if success

def download_install():
	try:
		DL_file()
	except:
		msg_box('Failed to download ' + FN + ' to ' + tmp + '.', 0)
		stop()
	else:
		print 'Downloaded:		' + FN

	try:
		RC = sub_proc(command)
	except:
		RC = None

	if RC == None:
		msg_box('Failed to execute ' + FN + '.', 0)
		stop()
	elif RC == 0:
		msg_box('Successfully updated to version ' + site_version + '.', 0)
		stop()
	else:
		msg_box('Successfully spawned new process for ' + FN + '. But the installation appears to have failed.', 0)
		stop()

# Check if the WinSCP.exe file exists...
if not os.path.isfile(WinSCP_exe):
	# No:	Download and install WinSCP, and quit.
	print 'WinSCP.exe file doesn\'t exist.'
	print 'Installing WinSCP for the first time...'
	download_install()
	print 'Ending...'
	delay(5)
	stop()

import win32api
try:
    info = win32api.GetFileVersionInfo(WinSCP_exe, "\\")
    ms = info['FileVersionMS']
    ls = info['FileVersionLS']
    file_version = "%d.%d.%d.%d" % (win32api.HIWORD(ms), win32api.LOWORD (ms),
									win32api.HIWORD (ls), win32api.LOWORD (ls))
except:
	msg_box('Cannot find the file version of the local WinSCP.exe file.', 0)
	stop()
else:
	print 'Got local file version information...'

# Check if the site_version numbers are in the file_version numbers...
def clean(text):
	import re
	return re.sub('[^0-9]', '', text)

clean_site_version = clean(site_version)
clean_file_version = clean(file_version)[:len(clean_site_version)]

print 'Local version:		' + clean_file_version
print 'Site version:		' + clean_site_version

def delay(sec):
	import time
	time.sleep(sec)

if clean_file_version.find(clean_site_version) != -1:
	# Yes:	Quit.
	print 'Match!'
	print 'Ending...'
	delay(5)
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
	print 'WinSCP is running. Close WinSCP now!'
	user_input = msg_box('There is a new version of WinSCP available. Please close WinSCP and press OK to continue.', 1)
	if user_input == 1:
		pass
	elif user_input == 2:
		stop()

# Now download and install the new file...
user_input = msg_box('If you use a custom WinSCP.ini file, back it up now and then press OK when you are ready to proceed with the update.', 1)
if user_input == 2:
	stop()

download_install()
print 'Ending...'
delay(5)
