##############################################################################
# codecount.py
# Quick and dirty line of code counter for C/C++/C# souce files.
#
# Modification History:
# 08/10/2014 - Tom Kerr
# Initial creation.
##############################################################################

import os
import re
import sys


##############################################################################
# Find the max nesting level in a C/C++/C# statement.
##############################################################################
def max_nest_level(sourceline, nest, maxnest):
    for c in sourceline:
        if (c == '{'):
            nest += 1
            if (nest > maxnest):
                maxnest = nest
        elif (c == '}'):
            nest -= 1
            if (nest < 0):
                nest = 0
    return (nest, maxnest)
    
    
##############################################################################
# Parse a C/C++/C# source file.
##############################################################################
def parse_source_file(file):

    # Define some regular expressions.
    blank_re = re.compile("^\s*$")
    comment1_re = re.compile("^\s*?/\*.*?\*/") # Single line C comment with no code
    comment2_re = re.compile("^\s*?//.*?$")    # Single line C++ comment with no code
    multi_begin_re = re.compile("^.*?/\*")     # C begin comment
    multi_end_re = re.compile("^.*?\*/")       # C end comment
    quoted_re = re.compile('"(.*?)"')          # Any quoted string
    source1_re = re.compile("^(\s*?\S+?\s*?)(\s*?/\*.*?\*/)") # nbnc with C single line comment
    source2_re = re.compile("^(\s*?\S+?\s*?)(//.*?)$")        # nbnc with C++ single line comment
    
    lines = 0
    blanks = 0
    comments = 0
    nbnc = 0
    maxnest = 0
    
    multiline = False
    nest = 0
    
    # Open the file for reading.  
    # Note that no exception processing is implemented yet.
    f = open(file, 'r')
    
    for line in f:
        lines += 1
        
        # Remove quoted strings to avoid comment confusion.
        m = quoted_re.search(line)
        if m:
            #sys.stdout.write("Q")
            line = line.replace(m.group(1), "")
            
        # Blank line.
        if blank_re.search(line):
            #sys.stdout.write("A")
            blanks += 1
            continue
        
        # Finish parsing a C multi-line comment.
        if multiline:
            #sys.stdout.write("B")
            comments += 1
            if multi_end_re.search(line):
                multiline = 0
                
        else:
        
            # Single line C comment with no code.
            m = comment1_re.search(line)
            if m:
                #sys.stdout.write("C")
                comments += 1
                continue
            
            # Single line C++ comment with no code.
            m = comment2_re.search(line)
            if m:
                #sys.stdout.write("D")
                comments += 1
                continue
            
            # nbnc with C single line comment.
            m = source1_re.search(line)
            if m:
                #sys.stdout.write("E")
                nbnc += 1
                comments += 1
                (nest, maxnest) = max_nest_level(m.group(1), nest, maxnest)
                continue
            
            # nbnc with C++ single line comment.
            m = source2_re.search(line)
            if m:
                #sys.stdout.write("F")
                nbnc += 1
                comments += 1
                (nest, maxnest) = max_nest_level(m.group(1), nest, maxnest)
                continue
            
            # Look for start of multi-line C comment.
            if multi_begin_re.search(line):
                #sys.stdout.write("G")
                multiline = 1
                comments += 1
                continue
                
            # Everything else should be a stand alone non-blank-non-comment.
            #sys.stdout.write("H")
            nbnc += 1
            (nest, maxnest) = max_nest_level(line, nest, maxnest)
        
    f.close()
    
    return (lines, blanks, comments, nbnc, maxnest) 


##############################################################################
# Script execution starts here.
##############################################################################            

# This is the expected file name format for C/C++/C# source files
sourcefile_re = re.compile(".+\.(c$|cpp$|cs$|h$)")

file_count = 0;
(totalLines, totalBlanks, totalComments, totalNbnc, totalMaxnest) = (0, 0, 0, 0, 0)

# Print a header line in CSV format.
print("file,lines,blanks,comments,non-blank-non-comment,maxnest")

# Traverse the directory hierarchy looking for source files.
for root, dirs, files in os.walk(os.getcwd()):
    for file in files:
        if sourcefile_re.match(file):
        
            # Found a source file.
            file_count += 1
            sourcefile = os.path.join(root, file)
            (lines, blanks, comments, nbnc, maxnest) = parse_source_file(sourcefile)
            totalLines += lines
            totalBlanks += blanks
            totalComments += comments
            totalNbnc += nbnc
            if (maxnest > totalMaxnest):
                totalMaxnest = maxnest
            
            # Print the result in CSV format.
            print(sourcefile + "," + str(lines) + "," + str(blanks) + "," + 
                str(comments) + "," + str(nbnc) + "," + str(maxnest))

# Print totals.
print("totals," + str(totalLines) + "," + str(totalBlanks) + "," + str(totalComments) +
    "," + str(totalNbnc) + "," + str(totalMaxnest))
    
print("files," + str(file_count))

# End of file