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
                date = datetime.date(*[int(elt) for elt in re.split('[/-]',date)])
                continue        # Pass back to beginning of loop so datetime.date clause returns the date string
            except:
                raise TypeError("The date must be a datetime.date object, a list in the form of [yyyy,mm,dd], or a date in the form of yyyy/mm/dd or yyyy-mm-dd")


def indexpattern_generate(start,end):
    """Function to return the proper index pattern for queries to elasticsearch on gracc.opensciencegrid.org.  This improves performance by not just using a general index pattern unless absolutely necessary.
    This will especially help with reports, for example.i

    This function assumes that the date being passed in has been split into a list with [yyyy,mm,dd] format.  This gets tested and cleaned up in the called dateparse function.
    """ 
    startdate = dateparse(start)
    enddate = dateparse(end)
        
    basepattern='gracc.osg.query-'
    
    if startdate[0]==enddate[0]:                        #Check if year is the same
        basepattern+='{}.'.format(str(startdate[0]))
        if startdate[1]==enddate[1]:                    #Check if month is the same
            if len(str(startdate[1]))==1:               #Add leading zero if necessary
                add = '0{}'.format(str(startdate[1]))
            else:
                add = str(startdate[1])
            basepattern+='{}'.format(add)
        else:
            basepattern+='*'
    else:
        basepattern+='*'

    return basepattern


if __name__=="__main__":
    #Meant for testing
    date_end = ['2016','06','12']
    date_start1 = ['2016','06','10']
    date_start2 = ['2016','05','10']
    date_start3 = ['2015','06','10']
   
    date_dateend = datetime.date(2016,06,12)
    date_datestart1 = datetime.date(2016,06,10)
    date_datestart2 = datetime.date(2016,5,10)
    date_datestart3 = datetime.date(2015,05,10)

    datestringslash = '2016/06/10'
    datestringdash = '2016-06-10'

    datebreak = '20160205'
    
# gracc.osg.query-YYYY.MM

    print indexpattern_generate(date_start1,date_end), 'Should be gracc.osg.query-2016.06'
    print indexpattern_generate(date_start2,date_end), 'Should be gracc.osg.query-2016.*'
    print indexpattern_generate(date_start3,date_end), 'Should be gracc.osg.query-*'

    print indexpattern_generate(date_datestart1,date_dateend), 'Should be gracc.osg.query-2016.06'
    print indexpattern_generate(date_datestart2,date_dateend), 'Should be gracc.osg.query-2016.*'
    print indexpattern_generate(date_datestart3,date_dateend), 'Should be gracc.osg.query-*'

    print indexpattern_generate(datestringslash,date_dateend), 'Should be gracc.osg.query-2016.06'
    print indexpattern_generate(datestringdash,date_dateend), 'Should be gracc.osg.query-2016.06'
    
    print "This next test should fail with a TypeError."
    print indexpattern_generate(datebreak,date_dateend)


