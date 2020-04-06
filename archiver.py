#!$(which python)

"""
Simple-python-archiver

A simple script for handling regular localised backups, intended for use with crontab or manual usage.

Author: James A. Douthwaite
"""

import os
import sys
import tarfile
from datetime import datetime
from collections import namedtuple

# ======== Configuration =========
inputFileList = "archive-files.txt"					# The file containing the list of file locations
outputFileLabel = "backup.tgz" 						# The string identifing these archives
outputLocation = "/media/backups"					# Where archives are stored
dateFormat = "%Y-%m-%d @ %H-%M"						# The date format 
allowance = 1.1										# Growth expectation ~~ frequency
fixedArchiveCount = True							# Enable fixed archive number
fixedArchiveNumber = 10								# Fixed number of archives

# =========== Methods ============
def CreateArchive(outputFilePath,archiveFilePaths):
	flag = False
	try:
	    with tarfile.open(outputFilePath, "w:gz") as tar:
	    	for archiveFile in archiveFilePaths:
	    		tar.add(archiveFile, arcname=archiveFile)
	    flag = True
	except Exception as err:
		print("[BACKUP] --> Failed to write archive.")
		print("OS error: {0}".format(err))

		if os.path.exists(outputFilePath):
			os.remove(outputFilePath)				# If a file is created, remove it

	return flag

def GetArchiveStatistics(path,filePattern):
	files = []
	largest = []
	maxArchiveSize = 0
	for fn in os.listdir(path):
		if not fn.endswith(filePattern):
			continue
		fnPath = os.path.join(path,fn)
		files.append(fnPath)
		# Get the maximum size file
		fnSize = float(GetFileSize(fnPath))
		if fnSize > maxArchiveSize:
			maxArchiveSize = fnSize
			largest = fnPath
	# Get the oldest and newest
	files = sorted(files, key=os.path.getctime)
	oldest = files[0]
	newest = files[-1]
	archiveNumber = int(len(files))
	return newest, oldest, largest, archiveNumber

def GetConfigList(fileName):
	fHandle = open(fileName, 'r')
	fileList = fHandle.readlines()
	for i in range(0,len(fileList)):
		fileList[i] = fileList[i].rstrip() 			# remove end of lines
	return fileList

def GetDiskUsage(path):
	"""Return disk usage statistics about the given path.
	Returned valus is a named tuple with attributes 'total', 'used' and
	'free', which are the amount of total, used and free space, in bytes.
    """
	st = os.statvfs(path)
	free = st.f_bavail * st.f_frsize
	total = st.f_blocks * st.f_frsize
	used = (st.f_blocks - st.f_bfree) * st.f_frsize
	return free, total, used

def GetFileSize(path):
	size = os.path.getsize(path)
	return size

# ================== Main =====================
currentTime = datetime.now()
outputFilePath = os.path.join(outputLocation,
	"[" + currentTime.strftime(dateFormat) + "] " + outputFileLabel)

print("[BACKUP] Executing backup routine..")
print("[BACKUP] Date: " + currentTime.strftime(dateFormat))
print("[BACKUP] Location: " + outputLocation)
print("[BACKUP] ")

# ====== Check fixed number constraint ========
newest, oldest, largest, archiveNumber = GetArchiveStatistics(outputLocation,outputFileLabel)		# Get current archive data
if (fixedArchiveCount):																				# Check if number of archives is within boundary
	print("[BACKUP] Confirming archive count...")
	while archiveNumber > int(fixedArchiveNumber):
		os.remove(oldest)																			# Delete oldest archive
		newest, oldest, largest, archiveNumber = GetArchiveStatistics(outputLocation,outputFileLabel)
	print("[BACKUP] Archive number valid.")

#For debug
#print("Newest: %s, Oldest: %s, Largest: %s", #archives: %s" % (newest, oldest, largest, str(archiveNumber)))

# ========== Confirm space on disk ============
print("[BACKUP] ")
print("[BACKUP] Confirming available drive space..")
free, total, used = GetDiskUsage(outputLocation)													# Get usage
print("[BACKUP] Space at archive location:");
print("[BACKUP] Total: %dMB used: %dMB free: %dMB (%d%% used)" %(
	float(total)/1000000,
	float(used)/1000000,
	float(free)/1000000,
	(float(used)/float(total))*100))																# Display initial drive stats
diff = float(GetFileSize(largest))*allowance - float(free)											# The space differencial
# Recursively remove files										
while diff > 0:
	print("[BACKUP] More space required (%dMB).. deleting oldest archive '%s'" % (diff/1000000,oldest))
	os.remove(oldest)
	# Re-evaluate
	newest, oldest, largest, archiveNumber = GetArchiveStatistics(outputLocation,outputFileLabel)	
	print(largest)				# Redefine the oldest archive data
	free, total, used = GetDiskUsage(outputLocation)															# Get new usage
	diff = float(GetFileSize(largest))*allowance - float(free) 									  	# Reaffirm space differencial

print("[BACKUP] Space check passed.")

# =============== Backing up ====================
print("[BACKUP] ")
print("[BACKUP] Continuing with backup procedure...")
print("[BACKUP] ")
print("[BACKUP] Target archive: %s" %(outputFilePath))
print("[BACKUP] Reading file set:")

# Look for list of local files
try:
	fileList = GetConfigList(os.path.join(os.path.abspath(os.getcwd()),inputFileList))
except:
	print("[BACKUP] Reading input file list failed.")
	sys.exit()

for file in fileList:
	print("[BACKUP] Queuing file '%s'" %(file))									# Read out for clarity

print("[BACKUP] ")
print("[BACKUP] Compressing files to archive '%s'" %(outputLocation))
print("[BACKUP] ")

flag = CreateArchive(outputFilePath,fileList)									# Create backup at output-path

if (flag):
	print("[BACKUP] Success.")
else:
	print("[BACKUP] Failed.")

print("[BACKUP] ")
print("[BACKUP] ...routine complete.\n")
sys.exit()