#!/usr/bin/python

import json
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q,A, Search
import certifi
import logging


#client = Elasticsearch(host='localhost',port=9200,timeout=60)

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
endtimeq='2016-07-05T00:00'
wildcardVOq = 'dune'
wildcardProbeNameq = 'condor:fifebatch?.fnal.gov'

s = Search(using=client,index='gracc.osg.raw-2016*')\
	.query("regexp",ReportableVOName=wildcardVOq)\
	.query("wildcard",ProbeName=wildcardProbeNameq)\
	.filter("range",EndTime={"gte":starttimeq,"lt":endtimeq})\
	.filter(Q({"range":{"WallDuration":{"gt":0}}}))\
    .filter(Q({"term":{"ResourceType":"Payload"}}))[0:0]
    

#a=A('terms',field='ReportableVOName')
	
Bucket = s.aggs.bucket('group_VOname','terms',field='ReportableVOName').bucket('group_commonName','terms',field='CommonName')

#Bucket.metric('Test_metric','sum',field='WallDuration')

#Bucket.metric('Process_times_WallDur','scripted_metric',map_script="doc['WallDuration'].value*doc['Processors'].value")

Metric = Bucket.metric('Process_times_WallDur','sum',script="(doc['WallDuration'].value*doc['Processors'].value)")\
		.metric('WallHours','sum',script="(doc['WallDuration'].value*doc['Processors'].value)/3600")\
		.metric('CPUDuration','sum',field='CpuDuration')
#Pipeline = Metric.pipeline('Test','bucket_script',buckets_path=['CPUDuration','WallHours'],script='CPUDuration/WallHours')  #Right now, failing because Processors isn't numeric.  Follow up with Kevin.  Up until here, it works

#Pipeline = Metric.pipeline('Test','bucket_script',buckets_path="Process_times_WallDur",script="doc['CpuDuration']/(Process_times_WallDur*3600)")



#Bucket.metric('Process_times_WallDur','scripted_metric',init_script="_agg['\"stuff\"] = [];",map_script="_agg.stuff.add(doc['WallDuration'].value * doc['Processors']);",\
#		combine_script="number = 0; for (t in _agg.transactions) {number+=t}; return number;", \
#		reduce_script = "number = 0 ; for (a in _aggs) {number += a}; return number;")
		# *doc['WallDuration']")

response = s.execute()
t = s.to_dict()

##Query
#print json.dumps(t,sort_keys=True,indent=4)

#for line in response:
#	print response.to_dict().keys()

#try:
#	print response.to_dict()['WallDuration'], response.to_dict()['Processors']
#except KeyError:
#	print "Oh well"
#	pass

#print json.dumps(response.to_dict(),sort_keys=True,indent=4)

resultset = json.dumps(response.aggregations.to_dict(),sort_keys=True,indent=4)
print resultset


#for item in response:
#	print item.to_dict()
	#['CommonName']

#for i in response.aggregations:	
#	#.group_VOName.bucket:
#	print i.key,i.doc_count


#a = A('terms',field='CommonName')
#print response.aggs.bucket('group_commonName',a)

#a = aggs.bucket("group_CommonName",dd"terms",field='CommonName')

#      "aggs":{
#        "group_CommonName":{
#          "terms":{"field":"CommonName"},
#
#          "aggs":{
#            "Sum_wall_seconds":{
#              "sum":{"field":"WallDuration.seconds"}
#            },
#            "Sum_Cpu_Duration":{
#              "sum":{"field":"CpuDuration.seconds"}
#                }
#              }
#            }
#          }
#        }
#      }
#    }
#  }
#



#print 'Total %d hits found' % response.hits.total
#for h in response:
#	print h

#for line in s.scan():
#	print line['RecordId'][0],line['EndTime'][0]
#	print line
#Returns 24114 lines as opposed to GRATIA 24115 without aggregations.  Can investigate if needed.

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



#{
#  "query":{
#    "bool":{
#      "must":[
#        {"regexp":{"ReportableVOName":"dune"}},
#        {"wildcard":{"ProbeName":"condor:fifebatch?.fnal.gov"}}
#      ],
#      "filter":[
#        {"range":{
#          "EndTime":{
#            "from":"2016-05-09T12:00",
#            "to":"2016-05-10T12:00"
#          }
#        }},
#        {"term":{"Resource.ResourceType":"BatchPilot"}},
#        {"range":{
#          "WallDuration.seconds":{"gt":0}
#        }}
#      ]
#    }
#  },
#  "aggs":{
#    "group_VOName":{
#      "terms":{"field":"ReportableVOName"},
#      
#      "aggs":{
#        "group_CommonName":{
#          "terms":{"field":"CommonName"},
#
#          "aggs":{
#            "Sum_wall_seconds":{
#              "sum":{"field":"WallDuration.seconds"}
#            },
#            "Sum_Cpu_Duration":{
#              "sum":{"field":"CpuDuration.seconds"}
#                }
#              }
#            }
#          }
#        }
#      }
#    }
#  }
#
#
#}
