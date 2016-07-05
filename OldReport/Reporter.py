from MySQLUtils  import MySQLUtils
import TextUtils

class Reporter:
    def __init__(self,config,start,end=None,verbose=False):
        """Constructor for OSGReporter 
        Args:
                config(Configuration) - configuration file
                start(str) - start date (YYYY/MM/DD) of the report
                end(str,optional) - end date (YYYY/MM/DD) of the report, defaults to 1 month from start date 
                verbose(boolean,optional) - print debug messages to stdout
        """

        self.header=[]
        self.config=config.config
        self.start_time=start
        self.verbose=verbose
        self.end_time=end

    def format_report(self):
	pass

    def send_report(self,report_type="test"):
        """Send reports as ascii, csv, html attachements """
        text={}
        content=self.format_report()
	print "header",self.header
        emailReport=TextUtils.TextUtils(self.header)
        text["text"]=emailReport.printAsTextTable("text",content)
        text["csv"]=emailReport.printAsTextTable("csv",content)
        text["html"]="<html><body><h2>%s</h2><table border=1>%s</table></body></html>" % (self.title,emailReport.printAsTextTable("html",content),)
        emails=self.config.get("email","%s_to" % (report_type,)).split(",")
        names=self.config.get("email","%s_realname" % (report_type,)).split(",")
        TextUtils.sendEmail((names,emails),self.title,text, ("Gratia Operation",self.config.get("email","from")),self.config.get("email","smtphost"))

