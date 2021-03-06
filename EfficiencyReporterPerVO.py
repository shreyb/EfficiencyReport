#!/usr/bin/env python

import sys
import os
import traceback
import re
import json
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q, Search

import TextUtils
import Configuration
import NiceNum
from Reporter import Reporter
from indexpattern import indexpattern_generate


class User:
    def __init__(self, info):
        """Take CSV as described below and assigns to it the attributes vo, facility, email, user, hours, eff
        # CSV format DARKSIDE, Fermigrid, /CN = fifegrid/CN = batch/CN = Shawn S. Westerdale/CN = UID:shawest,
        # 13411.2019444, 0.969314375191
        # New CSV format 'uboone', 'GPGrid', '/CN=fifegrid/CN=batch/CN=Elena Gramellini/CN=UID:elenag', '1337.86666667', '0.857747616437'
        """
        tmp = info.split(',')
        self.vo = tmp[0].lower()
        self.facility = tmp[1]
        self.email, self.user = self.parseCN(tmp[2])
        self.hours = int(float(tmp[3]))
        self.eff = round(float(tmp[4]), 2)

    def parseCN(self, cn):
        """Parse the CN to grab the email address and user"""
        m = re.match(".+CN=UID:(\w+)", cn)      # CILogon certs
        if m:
            email = '{}@fnal.gov'.format(m.group(1))
        else:
            email = ""
            m = re.match('/CN=(\w+)/.+', cn)    # Non-CILogon Certs (note - this matches what we did before, but we might need to change it in the future
        user = m.group(1)
        return email, user

    def dump(self):
        print "{:>10}, {:>20}, {:>20}, {}, {}".format(self.vo, self.facility, self.user, int(self.hours), round(self.eff, 2))


class Efficiency(Reporter):
    def __init__(self, config, start, end, vo, verbose, hour_limit, eff_limit, is_test):
        Reporter.__init__(self, config, start, end, verbose = False)
        self.hour_limit = hour_limit
        self.vo = vo
        self.eff_limit = eff_limit
        self.is_test = is_test
        self.verbose = verbose

    def query(self, client):
        """Method to query Elasticsearch cluster for EfficiencyReport information"""
        # Gather parameters, format them for the query
        start_date = re.split('[-/ :]', self.start_time)
        starttimeq = datetime(*[int(elt) for elt in start_date]).isoformat()
        end_date = re.split('[-/ :]', self.end_time)
        endtimeq = (datetime(*[int(elt) for elt in end_date])).isoformat()
        wildcardVOq = '*' + self.vo.lower() + '*'
        wildcardProbeNameq = 'condor:fifebatch?.fnal.gov'

        # Elasticsearch query and aggregations
        s = Search(using = client, index = indexpattern_generate(start_date, end_date))\
                   .query("wildcard", VOName=wildcardVOq)\
                   .query("wildcard", ProbeName=wildcardProbeNameq)\
                   .filter("range", EndTime={"gte" : starttimeq, "lt" : endtimeq})\
                   .filter(Q({"range" : {"WallDuration": {"gt": 0}}}))\
                   .filter(Q({"term": {"Host_description" : "GPGrid"}}))\
                   .filter(Q({"term" : {"ResourceType" : "Payload"}}))[0:0]       # Size 0 to return only aggregations

        Bucket = s.aggs.bucket('group_VOname', 'terms', field='ReportableVOName')\
                .bucket('group_HostDescription', 'terms', field='Host_description')\
                .bucket('group_commonName', 'terms', field='CommonName')

        Metric = Bucket.metric('Process_times_WallDur', 'sum', script="(doc['WallDuration'].value*doc['Processors'].value)")\
                .metric('WallHours', 'sum', script="(doc['WallDuration'].value*doc['Processors'].value)/3600")\
                .metric('CPUDuration', 'sum', field='CpuDuration')

        return s

    def query_to_csv(self):
        """Returns a csv file with aggregated data from query to Elasticsearch"""
        outfile = 'efficiency.csv'

        # Initialize the elasticsearch client
        client = Elasticsearch(['https://fifemon-es.fnal.gov'],
                             use_ssl = True,
                             verify_certs = True,
                             ca_certs = '/etc/grid-security/certificates/cilogon-osg.pem',
                             client_cert = 'gracc_cert/gracc-reports-dev.crt',
                             client_key = 'gracc_cert/gracc-reports-dev.key',
                             timeout = 60)

        s = self.query(client)

        if self.verbose:
            t = s.to_dict()
            print json.dumps(t, sort_keys=True, indent=4)

        response = s.execute()
        resultset = response.aggregations

        if not response.success():
            raise Exception('Error accessing ElasticSearch')

        if self.verbose:
            print json.dumps(response.to_dict(), sort_keys=True, indent=4)

        # Header for file
        header = '{}\t{}\t{}\t{}\t{}\n'.format('VO',
                                             'Host Description',
                                             'Common Name',
                                             'Wall Hours',
                                             'Efficiency')

        # Write everything to the outfile
        with open(outfile, 'w') as f:
            f.write(header)
            for per_vo in resultset.group_VOname.buckets:
                for per_hostdesc in per_vo.group_HostDescription.buckets:
                    for per_CN in per_hostdesc.group_commonName.buckets:
                        outstring = '{},{},{},{},{}\n'.format(self.vo,
                                                                  per_hostdesc.key,
                                                                  per_CN.key,
                                                                  per_CN.WallHours.value,
                                                                  (per_CN.CPUDuration.value / 3600) / per_CN.WallHours.value)
                        f.write(outstring)

        return outfile

    def reportVO(self, users, facility):
        """Method to generate report for VO from users dictionary"""
        if self.vo == "FIFE":
            records = [rec for rec in users.values()]
        else:
            records = users[self.vo.lower()]
        info = [rec for rec in records if ((rec.hours > self.hour_limit and rec.eff < self.eff_limit) and (facility == "all" or rec.facility == facility))]
        return sorted(info, key=lambda user: user.eff)

    def send_report(self, report):
        """Generate HTML from report and send the email"""
        if len(report) == 0:
            print "Report empty"
            return

        table = ""
        for u in report:
            table += '<tr><td align="left">{}</td><td align="left">{}</td>'.format(u.vo.upper(), u.facility) + \
                     '<td align="left">{}</td><td align="right">{}</td><td align="right">{}</td></tr>'.format(
                                                                        u.user, NiceNum.niceNum(u.hours), u.eff)

        text = "".join(open("template_efficiency.html").readlines())
        text = text.replace("$START", self.start_time)
        text = text.replace("$END", self.end_time)
        text = text.replace("$TABLE", table)
        text = text.replace("$VO", self.vo.upper())

        if self.verbose:
            fn = "{}-efficiency.{}".format(self.vo.lower(), self.start_time.replace("/", "-"))
            with open(fn, 'w') as f:
                f.write(text)

        if self.is_test:
            emails = re.split('[; ,]', self.config.get("email", "test_to"))
        else:
            emails = re.split('[; ,]', self.config.get(self.vo.lower(), "email")) + re.split('[; ,]', self.config.get("email", "test_to"))
        TextUtils.sendEmail(
                            ([], emails),
                            "{} Jobs with Low Efficiency ({})  on the  OSG Sites ({} - {})".format(
                                                                                                    self.vo,
                                                                                                    self.eff_limit,
                                                                                                    self.start_time,
                                                                                                    self.end_time),
                            {"html": text},
                            ("Gratia Operation", "sbhat@fnal.gov"),
                            "smtp.fnal.gov")

        if self.verbose:
            os.remove(fn)
            print "Report sent"


if __name__ == "__main__":
    opts, args = Reporter.parse_opts()
    try:
        # Set up the configuration
        config = Configuration.Configuration()
        config.configure(opts.config)
        # Grab VO
        vo = opts.vo
        # Grab the limits
        eff = config.config.get(opts.vo.lower(), "efficiency")
        min_hours = config.config.get(opts.vo.lower(), "min_hours")

        # Create an Efficiency object, create a report for the VO, and send it
        e = Efficiency(config, opts.start, opts.end, vo, opts.verbose, int(min_hours), float(eff), opts.is_test)
        # Run our elasticsearch query, get results as CSV
        resultfile = e.query_to_csv()

        # For each line returned, create a User object, and add the User and their vo to the users dict
        with open(resultfile, 'r') as file:
            f = file.readlines()
        users = {}
        for line in f[1:]:
            u = User(line)
            if u.vo not in users:
                users[u.vo] = []
            users[u.vo].append(u)

        # Generate the VO report, send it
        if vo == "FIFE" or vo.lower() in users:
            r = e.reportVO(users, opts.facility)
            e.send_report(r)
    except:
        print >> sys.stderr, traceback.format_exc()
        sys.exit(1)
    sys.exit(0)
