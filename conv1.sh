#!/bin/bash
#
# Usage: conv1.sh filename
#
#
# Script to convert file using awk script
#

USAGE="${0##/} inputfile"
#check parameters
if (($#<1)); then
   echo "ERROR: invalid parameters"
   echo "USAGE: $USAGE"
   exit -1
fi

IF=$1
#append .new to input filename for output filename 
OF=${IF}.new

#check that input file exists and is not empty
if [[ ! -s $IF ]] ; then
   echo "ERROR: inputfile '$IF' empty or does not exist" 
   exit -1
fi

# if file has only line then treat differently - seems to work okay

#run awk script to perform following actions
# prefix 1st line with [
# append , to end of each line, except last line
# append ] to end of last line
echo "Running conversion to generate file '$OF'"
awk 'BEGIN { l=1 }
{ if (l) { printf("[%s",$0); l=0 } else printf(",\n%s",$0) }
END { printf("]\n") }' $IF > $OF

#check filesizes to ensure it looks good
#get line and char counts of inputfile and outputfile
#line counts should be the same
#char count should increase by line count + 1

#following ksh command wont work
#wc $IF |read -r nli nwi nci dummy

#use set instead
set $(wc < $IF)
nli=$1; nci=$3
set $(wc < $OF)
nlo=$1; nco=$3

typeset -i LRET=0

#check that line counts match
echo "Checking line counts match"
if ((nli!=nlo)) ;then
   echo "ERROR: linecount mismatch"
   LRET=-1
fi

#check outfile char count increased by infile line count + 1
echo "Checking char counts match"
if ((nco!=((nci + nli + 1)))) ;then
   echo "ERROR: charcount mismatch"
   LRET=-1
fi

#((LRET!=0)) && wc $IF && wc $OF
wc $IF ; wc $OF
((LRET==0)) && echo "OK"

exit $LRET
