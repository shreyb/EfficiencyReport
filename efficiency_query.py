#!/usr/bin/python

from Elasticsearch import Elasticsearch
from Elasticsearch_dsl import Q, Search

client = Elasticsearch()

s = Search(using=client,index='gracc-osg-2016*').query("match_all")

response = s.execute()


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
