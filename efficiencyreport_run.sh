#!/bin/sh

VOS="nova seaquest minerva minos gm2 mu2e uboone darkside dune cdms mars cdf" 
YESTERDAY=`date --date yesterday +"%F %T"`
TODAY=`date +"%F %T"`



cd /home/sbhat/EfficiencyReport

for vo in ${VOS}
do
	echo $vo
	./EfficiencyReporterPerVO -F GPGrid -c efficiency.config -E $vo -s "$YESTERDAY" -e "$TODAY" -d -v
	echo "Sent report for $vo"
done

 

