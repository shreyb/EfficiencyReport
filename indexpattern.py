#!/usr/bin/python

import datetime
import re

def dateparse(date):
    """Function to make sure that our date is either a list, a datetime.date object or a date in the form of yyyy/mm/dd or yyyy-mm-dd"""
    while True:
        if isinstance(date, datetime.date):
            return [date.year, date.month, date.day]
        elif isinstance(date, list):
            return date
        else:
            try:
                date = datetime.date(*[int(elt) for elt in re.split('[/: -]', date)][:3])
                continue        # Pass back to beginning of loop so datetime.date clause returns the date string
            except:
                raise TypeError("The date must be a datetime.date object, a list in the form of [yyyy,mm,dd], or a date in the form of yyyy/mm/dd or yyyy-mm-dd")


def indexpattern_generate(start, end):
    """Function to return the proper index pattern for queries to elasticsearch on gracc.opensciencegrid.org.  This improves performance by not just using a general index pattern unless absolutely necessary.
    This will especially help with reports, for example.

    This function assumes that the date being passed in has been split into a list with [yyyy,mm,dd] format.  This gets tested and cleaned up in the called dateparse function.
    """
    startdate = dateparse(start)
    enddate = dateparse(end)

    basepattern = 'gracc.osg.raw-'

    if startdate[0] == enddate[0]:                        # Check if year is the same
        basepattern += '{}.'.format(str(startdate[0]))
        if startdate[1] == enddate[1]:                    # Check if month is the same
            if len(str(startdate[1])) == 1:               # Add leading zero if necessary
                add = '0{}'.format(str(startdate[1]))
            else:
                add = str(startdate[1])
            basepattern += '{}'.format(add)
        else:
            basepattern += '*'
    else:
        basepattern += '*'

    return basepattern


if __name__ == "__main__":
    # Meant for testing
    date_end = ['2016', '06', '12']
    date_start1 = ['2016', '06', '10']
    date_start2 = ['2016', '05', '10']
    date_start3 = ['2015', '06', '10']

    date_dateend = datetime.date(2016, 06, 12)
    date_datestart1 = datetime.date(2016, 06, 10)
    date_datestart2 = datetime.date(2016, 5, 10)
    date_datestart3 = datetime.date(2015, 05, 10)

    datestringslash = '2016/06/10'
    datestringdash = '2016-06-10'

    fulldate = '2016/06/10 12:34'

    datebreak = '20160205'

    # gracc.osg.raw-YYYY.MM

    assert indexpattern_generate(date_start1, date_end) == 'gracc.osg.raw-2016.06', "Assertion Error, {}-{} test failed".format(date_start1, date_end)
    assert indexpattern_generate(date_start2, date_end) == 'gracc.osg.raw-2016.*', "Assertion Error, {}-{} test failed".format(date_start2, date_end)
    assert indexpattern_generate(date_start3, date_end) == 'gracc.osg.raw-*', "Assertion Error, {}-{} test failed".format(date_start3, date_end)
    print "Passed date array tests"

    assert indexpattern_generate(date_datestart1, date_dateend) == 'gracc.osg.raw-2016.06', "Assertion Error, {}-{} test failed".format(date_datestart1, date_dateend)
    assert indexpattern_generate(date_datestart2, date_dateend) == 'gracc.osg.raw-2016.*', "Assertion Error, {}-{} test failed".format(date_datestart2, date_dateend)
    assert indexpattern_generate(date_datestart3, date_dateend) == 'gracc.osg.raw-*', "Assertion Error, {}-{} test failed".format(date_datestart3, date_dateend)
    print "Passed datetime.date tests"

    assert indexpattern_generate(datestringslash, date_dateend) == 'gracc.osg.raw-2016.06', "Assertion Error, {}-{} test failed".format(datestringslash, date_dateend)
    assert indexpattern_generate(datestringdash, date_dateend) == 'gracc.osg.raw-2016.06', "Assertion Error, {}-{} test failed".format(datestringslash, date_dateend)
    print "Passed date string tests (/ and -)"

    print "This next test should fail with a TypeError."
    try:
        indexpattern_generate(datebreak, date_dateend)
    except TypeError as e:
        print "A TypeError was raised.  The error was the following:"
        print e
