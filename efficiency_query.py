#!/usr/bin/python

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q,A, Search

client = Elasticsearch(host='localhost',port=9200,timeout=60)


starttimeq = '2016-06-01T07:30'
endtimeq= '2016-06-02T07:30'
wildcardVOq = 'dune'
wildcardProbeNameq = 'condor:fifebatch?.fnal.gov'

s = Search(using=client,index='gracc.osg.raw-2016*')\
	.query("regexp",ReportableVOName=wildcardVOq)\
	.query("wildcard",ProbeName=wildcardProbeNameq)\
	.filter("range",EndTime={"gte":starttimeq,"lt":endtimeq})\
	.filter(Q({"range":{"WallDuration":{"gt":0}}}))\
	.filter(Q({"term":{"ResourceType":"Payload"}}))


#a=A('terms',field='ReportableVOName')
	
s.aggs.bucket('group_VOname','terms',field='ReportableVOName')
s.aggs['group_VOname'].bucket('group_commonName','terms',field='CommonName')


response = s.execute()
t = s.to_dict()

print t
print response

for i in response.aggregations.group_VOname.buckets:	
	#.group_VOName.bucket:
	print i.key,i.doc_count


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
