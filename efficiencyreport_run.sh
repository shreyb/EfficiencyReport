#!/bin/sh

VOS="NOvA Seaquest Minerva Minos gm2 Mu2e UBooNe Darkside DUNE CDMS Mars CDF" 
YESTERDAY=`date --date yesterday +"%F %T"`
TODAY=`date +"%F %T"`



cd /home/sbhat/EfficiencyReport

for vo in ${VOS}
do
	echo $vo
	./EfficiencyReporterPerVO -F GPGrid -c efficiency.config -E $vo -s "$YESTERDAY" -e "$TODAY" -d
	echo "Sent report for $vo"
done

 

