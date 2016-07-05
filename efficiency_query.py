#!/usr/bin/python

import json
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q,A, Search
import certifi
import logging

logging.basicConfig(filename='example.log',level=logging.ERROR)
logging.getLogger('elasticsearch.trace').addHandler(logging.StreamHandler())

client=Elasticsearch(['https://gracc.opensciencegrid.org/e'],
                     use_ssl = True,
                     verify_certs = True,
                     ca_certs = certifi.where(),
                     client_cert = 'gracc_cert/gracc-reports-dev.crt',
                     client_key = 'gracc_cert/gracc-reports-dev.key',
                     timeout = 60) 


starttimeq ='2016-07-04T00:00'
endtimeq='2016-07-05T23:59'
vo = 'uboone'
wildcardVOq = '*'+vo+'*'
wildcardProbeNameq = 'condor:fifebatch?.fnal.gov'

s = Search(using=client,index='gracc.osg.raw-2016*')\
	.query("wildcard",VOName=wildcardVOq)\
	.query("wildcard",ProbeName=wildcardProbeNameq)\
	.filter("range",EndTime={"gte":starttimeq,"lt":endtimeq})\
	.filter(Q({"range":{"WallDuration":{"gt":0}}}))\
    .filter(Q({"term":{"Host_description":"GPGrid"}}))\
    .filter(Q({"term":{"ResourceType":"Payload"}}))[0:0]
   


Bucket = s.aggs.bucket('group_VOname','terms',field='ReportableVOName')\
        .bucket('group_HostDescription','terms',field='Host_description')\
        .bucket('group_commonName','terms',field='CommonName')

Metric = Bucket.metric('Process_times_WallDur','sum',script="(doc['WallDuration'].value*doc['Processors'].value)")\
		.metric('WallHours','sum',script="(doc['WallDuration'].value*doc['Processors'].value)/3600")\
		.metric('CPUDuration','sum',field='CpuDuration')
#Pipeline = Metric.pipeline('Test','bucket_script',buckets_path=['CPUDuration','WallHours'],script='CPUDuration/WallHours')  #Right now, failing because Processors isn't numeric.  Follow up with Kevin.  Up until here, it works

response = s.execute()
t = s.to_dict()

##Query
print json.dumps(t,sort_keys=True,indent=4)

#Response from query
print json.dumps(response.to_dict(),sort_keys=True,indent=4)

resultset = response.aggregations

for per_vo in resultset.group_VOname.buckets:
    for per_hostdesc in per_vo.group_HostDescription.buckets:
        #print per_hostdesc
        for per_CN in per_hostdesc.group_commonName.buckets:
            if per_CN.WallHours.value > 1000:  #Value from config file
                print '{}\t{}\t{}\t{}\t{}\t{}'.format(vo,
                                                      per_hostdesc.key,
                                                      per_CN.key,
                                                      per_CN.WallHours.value,
                                                      per_CN.CPUDuration.value/3600.,
                                                      (per_CN.CPUDuration.value/3600) / per_CN.WallHours.value
                                                      )
"""
SQL:

SELECT 
	*
/* 	UPPER(VO.VOName) -- DONE
	,R.HostDescription -- DONE 
	,R.CommonName
	,R.ProbeName */
-- 	,sum(R.Cores*R.WallDuration)/3600 as WallHours
-- 	,sum(R.CpuUserDuration + R.CpuSystemDuration)/sum(R.Cores*R.WallDuration) -- Note:  CPUDuration is CPUUserDuration+CPUSystemDuration
FROM
	JobUsageRecord R
/* 	MasterSummaryData R */ 
-- 	JOIN Probe P on R.ProbeName = P.probename
-- 	JOIN VONameCorrection VC ON (VC.corrid=R.VOcorrid)
-- 	JOIN VO on (VC.void = VO.void)
WHERE 
	1=1
	AND R.EndTime >=  "2016-06-01 07:30" -- DONE
	AND R.EndTime <  "2016-06-02 07:30"  -- DONE
	AND R.ResourceType='BatchPilot' -- DONE
	AND ReportableVOName regexp 'dune' -- DONE with dune as test
-- 	AND R.ProbeName like '%fifebatch%.fnal.gov' -- done with condor:fifebatch?.fnal.gov as test
	AND R.WallDuration > 0  -- DONE
/* GROUP BY  
	UPPER(VO.VOName)  -- done
	, R.CommonName -- done
	; */
-- HAVING sum(R.Cores*R.WallDuration)/3600 >= :min_hours 
; 

"""



