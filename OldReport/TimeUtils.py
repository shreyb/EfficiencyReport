"""Unitlity module that deals with time of the report"""

import time 
import datetime

############## From AccountingReport.py##############
class TimeUtils:  
    """Utility class to deal with setting time period for the report"""

    @staticmethod        
    def setDeltaStartTime(startTime,endTime):
	"""Sets the start and end date for previous time interval to calculate delta 
        Args:
                startTime(str)
                endTime(int)
        """

        b=startTime.split("/")
        e=endTime.split("/")
        st=time.mktime(datetime.date(int(b[0]),int(b[1]),int(b[2])).timetuple())
        et=time.mktime(datetime.date(int(e[0]),int(e[1]),int(e[2])).timetuple())
        delta=et-st
        old=datetime.date.fromtimestamp(st-delta)
        oldTime="%s/%s/%s" % (old.year,old.month,old.day)
        return oldTime

    @staticmethod     
    def DateToString(dateStr,gmt=False):
        """Converts date to string format
        Args:
        	dateStr(str)
                gmt(boolean)
        """

        if gmt:
            return dateStr.strftime("%Y-%m-%d 07:00:00");
        else:
            return dateStr.strftime("%Y-%m-%d");

    @staticmethod     
    def AddMonth(fromd, month):
        """Returns date as N month from a specified date
        Args:
                fromd(Date)
                month(int)
        """

        newyear = fromd.year
        newmonth = fromd.month + month
        while newmonth < 1:
            newmonth += 12
            newyear -= 1
        while newmonth > 12:    
            newmonth -= 12
            newyear += 1
        return datetime.date(newyear,newmonth,fromd.day)

    @staticmethod     
    def SetMonthlyDate(tm,flag=0):
        """Set the start and end date to be the begin and end of the month given in 'start'
	Args:
		tm(str)
		flaf(int)
	"""

        when = datetime.date(*time.strptime(tm, "%Y/%m/%d")[0:3])
        if not flag:
            begin = datetime.date( when.year, when.month, 1 )
            end = TimeUtils.AddMonth(begin, 1 )
        else:
            end = datetime.date( when.year, when.month, 1 )
            begin=TimeUtils.AddMonth(end,-1)
            print begin,end
        return begin,end

    @staticmethod     
    def SetWeeklyDate(finish):
        """Set the start and end date to the week preceding 'end'
        Args:
                finish(str)
	""" 

        end = datetime.date(*time.strptime(finish, "%Y/%m/%d")[0:3])
        begin = end - datetime.timedelta(days=7)
        return begin,end

    @staticmethod     
    def SetDailyDate(finish):
        """Set the start and end date to the week preceding 'end' 
	Args:
		finish(str)
	""" 

        end = datetime.date(*time.strptime(finish, "%Y/%m/%d")[0:3])
        begin = end - datetime.timedelta(days=1)
        return begin,end

    @staticmethod     
    def SetDate(start,finish):
        """Set the start and begin by string
	Args:
		start(str)
		finish(str)
	"""
 
        if len(start) > 0:
            begin = datetime.date(*time.strptime(start, "%Y/%m/%d")[0:3])
        if len(finish) > 0:
            end = datetime.date(*time.strptime(finish, "%Y/%m/%d")[0:3])
        return begin,end
