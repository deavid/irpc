#!/bin/sh
for ui in *.ui; do
    py=`echo $ui | sed 's/ui/py/'`
    echo "$ui >> $py"
    pyuic4 $ui > $py
done
