#!/bin/sh

<<<<<<< HEAD
VOS="NOvA SeaQuest MINERvA MINOS gm2 Mu2e UBooNe DarkSide DUNE CDMS MARS CDF" 
=======
VOS="NOvA Seaquest Minerva Minos gm2 Mu2e UBooNe Darkside DUNE CDMS Mars CDF" 
>>>>>>> d6f4da5b8bb87c8e397a7471591594a06647a1c2
YESTERDAY=`date --date yesterday +"%F %T"`
TODAY=`date +"%F %T"`



cd /home/sbhat/EfficiencyReport

for vo in ${VOS}
do
	echo $vo
	./EfficiencyReporterPerVO -F GPGrid -c efficiency.config -E $vo -s "$YESTERDAY" -e "$TODAY" -d
	echo "Sent report for $vo"
done

 

