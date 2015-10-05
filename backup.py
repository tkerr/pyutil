##############################################################################
# backup.py
# File backup and synchronization script.
#
# Usage:
# See print_usage() below.
#
# Modification History:
# 09/29/2015 - Tom Kerr
# Added -x option to exclude files from backup.
#
# 09/15/2015 - Tom Kerr
# Remove destination directories during sync that don't exist in source tree.
#
# 09/10/2015 - Tom Kerr
# Created.
##############################################################################

import getopt
import os.path
import shutil
import sys

##############################################################################
# Print usage syntax.
##############################################################################
def print_usage():
    print("Usage:", sys.argv[0], "[-dfhsvx] <src-dir> <dst-dir>")
    print("  Copy files from <src-dir> to <dst-dir>")
    print("  <src-dir> and <dst-dir> are directories")
    print("  -d = Dry run: print what would happen without actually copying")
    print("  -f = Force copy even if destination file is newer")
    print("  -h = Halt on copy error (default = skip and keep copying)")
    print("  -s = Sync: delete files in <dst-dir> that are not in <src-dir>")
    print("  -v = Verbose printing")
    print("  -x <file> Exclude files listed in <file>")
    sys.exit(2)

    
##############################################################################
# Print copy, deleted and error counts.
##############################################################################
def print_counts(copy_count, deleted_count, excluded_count, error_count, dry_run):
    if dry_run:
        print("Dry run results, no actions actually taken")
    print("Files copied:   " + str(copy_count))
    print("Files deleted:  " + str(deleted_count))
    print("Files excluded: " + str(excluded_count))
    print("Errors:         " + str(error_count))
    
    
##############################################################################
# Script execution starts here.
##############################################################################     
if __name__ == "__main__":
    
    # Local initialization.
    copy_count     = 0
    deleted_count  = 0
    excluded_count = 0
    error_count    = 0
    dry_run        = False
    error_halt     = False
    exclude        = False
    excludeFile    = None
    excludeList    = []
    force_copy     = False
    sync           = False
    verbose        = False
        
    # Get command line options and arguments.
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "dfhsvx:")
    except getopt.GetoptError as err:
        print str(err)
        print_usage()

    for (o, a) in opts:
        if (o == "-d"):
            dry_run = True
        if (o == "-f"):
            force_copy = True
        if (o == "-h"):
            error_halt = True
        if (o == "-s"):
            sync = True
        if (o == "-v"):
            verbose = True
	if (o == "-x"):
	    exclude = True
	    excludeFile = a
        
    # Check argument count.
    if (len(args) < 2):
        print_usage()
        
    # Get the source and destination paths.
    src_root = args[0]
    if not os.path.exists(src_root):
        print("Source directory '" + str(src_root) + "' does not exist")
        sys.exit(1)
    if not os.path.isdir(src_root):
        print(str(src_root) + " is not a directory")
        sys.exit(1)
    src_root_abs = os.path.abspath(src_root)
        
    dst_root = args[1]
    if not os.path.exists(dst_root):
        print("Destination directory '" + str(dst_root) + "' does not exist")
        sys.exit(1)
    if not os.path.isdir(dst_root):
        print(str(dst_root) + " is not a directory")
        sys.exit(1)
    dst_root_abs = os.path.abspath(dst_root)
    
    # Build the exclude file list.
    if (exclude):
        if not os.path.exists(excludeFile):
	    print("Exclude file '" + str(excludeFile) + "' does not exist")
            sys.exit(1)
	try:
	    f = open(excludeFile, 'r')
	    for line in f:
		fn = str(line).split("#")[0].strip()  # Remove comments and trim whitespace
		if (len(fn)) > 0:
	            excludeList.append(fn)
            f.close()
	except (IOError, OSError, os.error) as err:
	    print("Error reading " + str(excludeFile) + ": " + str(err))
	    sys.exit(1)

    # Iterate over all source files.  
    # Copy source to destination if criteria met.
    for (dirpath, dirnames, filenames) in os.walk(src_root_abs):
        for file in filenames:
            sfn_abs = os.path.join(dirpath, file)        # source file absolute path
            fn_rel = os.path.relpath(sfn_abs, src_root)  # source file relative path
            src_mtime = os.path.getmtime(sfn_abs)        # source file modification time
            
	    # See if this file is in the exclusion list.
	    if (exclude):
	        found = False
	        for f in excludeList:
		    if (sfn_abs == f):
		        found = True
		        excluded_count = excluded_count + 1
			if (verbose):
			    print("Excluding " + sfn_abs)
	                break
		if (found):
 		    continue
		
            # Check for this file in the destination path.
            dst_mtime = 0
            dfn_abs = os.path.join(dst_root_abs, fn_rel) # destination file absolute path
            if os.path.exists(dfn_abs):
                dst_mtime = os.path.getmtime(dfn_abs)    # destination file modification time
                
            # Copy source to destination.    
            if (force_copy or (src_mtime > dst_mtime)):
                if (dry_run or verbose):
                    print(str(sfn_abs) + " -> " + str(dfn_abs))
                if dry_run:
                    copy_count = copy_count + 1  # Dry run: fake copy count
                else:
                    try:
                        # Create directories if they don't exist.
                        dst_path = os.path.dirname(dfn_abs)
                        if not os.path.exists(dst_path):
                            os.makedirs(dst_path)
                        
                        # Perform the copy.
                        shutil.copy2(sfn_abs, dfn_abs)
                        os.utime(dfn_abs, None)          # update destination atime + mtime
                        copy_count = copy_count + 1
                        
                    except (shutil.Error, IOError, OSError, os.error) as err:
                        print("Error copying " + str(sfn_abs) + ": " + str(err))
                        error_count = error_count + 1
                        if error_halt:
                            print_counts(copy_count, deleted_count, excluded_count, error_count, dry_run)
                            sys.exit(3)
    
    # Sync option.    
    # Iterate over all destination files.  
    # Delete files and directories that don't exist in the source tree.
    if sync:
        # Perform a top-down walk to remove files.
        for (dirpath, dirnames, filenames) in os.walk(dst_root_abs, True):
            for file in filenames:
                dfn_abs = os.path.join(dirpath, file)        # destination file absolute path
                fn_rel = os.path.relpath(dfn_abs, dst_root)  # destination file relative path
                sfn_abs = os.path.join(src_root_abs, fn_rel) # source file absolute path
                if not os.path.exists(sfn_abs):
                    if (dry_run or verbose):
                        print("Deleting " + str(dfn_abs))
                    if dry_run:
                        deleted_count = deleted_count + 1  # Dry run: fake deleted count
                    else:
                        try:
                            os.remove(dfn_abs)
                            deleted_count = deleted_count + 1
                            
                        except (shutil.Error, IOError, OSError, os.error) as err:
                            print("Error deleting " + str(dfn_abs) + ": " + str(err))
                            error_count = error_count + 1
                            if error_halt:
                                print_counts(copy_count, deleted_count, excluded_count, error_count, dry_run)
                                sys.exit(3)
   
        # Perform a bottom-up walk to remove directories.        
        for (dirpath, dirnames, filenames) in os.walk(dst_root_abs, False):
            for dir in dirnames:
                ddn_abs = os.path.join(dirpath, dir)         # destination directory absolute path
                dn_rel = os.path.relpath(ddn_abs, dst_root)  # destination directory relative path
                sdn_abs = os.path.join(src_root_abs, dn_rel) # source directory absolute path
                if not os.path.exists(sdn_abs):
                    if (dry_run or verbose):
                        print("Deleting " + str(ddn_abs))
                    if dry_run:
                        deleted_count = deleted_count + 1  # Dry run: fake deleted count
                    else:
                        try:
                            os.rmdir(ddn_abs)
                            deleted_count = deleted_count + 1
                            
                        except (shutil.Error, IOError, OSError, os.error) as err:
                            print("Error deleting " + str(ddn_abs) + ": " + str(err))
                            error_count = error_count + 1
                            if error_halt:
                                print_counts(copy_count, deleted_count, excluded_count, error_count, dry_run)
                                sys.exit(3)
                
    print_counts(copy_count, deleted_count, excluded_count, error_count, dry_run)
    
# End of file. 