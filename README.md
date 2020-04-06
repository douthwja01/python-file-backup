# simple-python-archiver
A quick and simple linux-python back up tool. This tool is intended to facilate regular backups of a list of files though the use of crontab. The script maintains a set of time-stamped archives with a regular structure. The user can either allow script to maintain a fixed number of archives, or simply fill the available space before the oldest archives are overwritten. 

# Features
- The list of files to be included are specified as absolute paths in "archive-files.txt"
- Each archive is placed in the "output" directory, timestamped with a defined regular label.
- The script can either maintain a fixed number of archives, or maintain as many as drive space allows.
- Does not need super-user (depending on the files being included).

I hope you find this useful!
