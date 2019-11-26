# -*- coding: utf8 -*-
import os
import time
from datetime import datetime

from lib.utils.logger import Logger
from utils.const import const
from lib.utils.utils_funs import send_mail , send_mail_with_auth

class RTMRepoJob(object):
    def __init__(self,rtm,job_attr):
        self.logger = Logger.get_logger()
        self.rtm_api = rtm
        self.status = 1
        self.job_templates =  []
        self.hosts = []
        self.emails = None
        self.report_file = []
        self.name = None
        self.gene_time = None
        self._parser_attri(job_attr)
        pass

    
    def _generate_template_report(self,folder):
        file_name = folder.decode("utf-8") + self.name + u"_"
        suffix = u"_" + datetime.now().strftime('%Y_%m_%d_%H_%M').decode("utf-8") + u'.xlsx'
        #.rptdesign&__format=xlsx&HostIDS=All&HostGroup=t&__parameterpage=false
        host =  u",".join(str(x) for x in self.hosts)+u"&HostGroup=t&__parameterpage=false&__format=xlsx"

        for report in self.job_templates:
            tem_file = file_name + report[1].replace(" ","_") + suffix
            cmd = u'curl -o "' + tem_file + u'" "'+ const.BIRT+report[0]+ u".rptdesign&HostIDS=" + host + u'"'
            self.logger.debug("generate report :\n %s"%(cmd))
            os.system(cmd.encode("utf-8"))
            cmd = u'chmod -R 777 ' + folder.decode("utf-8")
            os.system(cmd.encode("utf-8"))
            self.report_file.append(tem_file)

    def _create_report(self,folder):
        if self.status == '1' or self.jobid is None :
            self.report_file = None
            return
        self._generate_template_report(folder)
        pass

    def _parser_attri(self,job_attr):
        if 'status' not in job_attr.keys():
            return
        if 'jobid' not in job_attr.keys():
            return
        self.jobid = self.status
        self.status = job_attr['status']
        if 'gene_time' in job_attr.keys():
            self.gene_time = int(job_attr['gene_time'])
        if self.gene_time is None:
            self.gene_time = 0

        self.name = job_attr['name']
        if 'jobtemplate' in job_attr.keys():
            if len(job_attr['jobtemplate']) > 0:
                for temp in  job_attr['jobtemplate']:
                    self.job_templates.append([temp["host"],temp['name']])
                self.logger.debug("template key is %s"%(self.job_templates))
        if 'job_mail' in job_attr.keys():
            tem_mail = []
            if len(job_attr['job_mail']) > 0:
                emails = job_attr['job_mail']
                for email in emails:
                    tem_mail.append(email['email'])
                self.emails = tem_mail

        if 'job_hosts' in job_attr.keys():
            if len(job_attr['job_hosts']) > 0:
                for host in job_attr['job_hosts']:
                    self.hosts.append(host["hostid"])
            else:
                self.hosts = ['All']

        pass


    def _send_mail(self,file_name):
        smtp = self.rtm_api.mediatype.get(filter = {"status":"0","type":0})
        if self.emails is None: 
            return
        target_mail = []
        for mail in self.emails:
            target_mail.append(str(mail))
        if smtp is not None and len(smtp) > 0:
            smtp_info =  smtp[0]
            send_mail_with_auth(u" Reporting " + self.name,target_mail,file_name,smtp_info)
        else:
            send_mail(u" Reporting " + self.name,target_mail,file_name)

        self.logger.info("Send reporting item %s to the owner"%(self.name))

    def _get_reporting_time(self,gen_time):
        time_slot = "{0:b}".format(gen_time)
        i = 0
        time_slots=[]
        ft = len(time_slot)
        for a in time_slot:
            if a == "1":
                time_slots.append(ft - i)
            i = i + 1
        return time_slots

    def gene_report(self,folder):
        try:
            week_of_day = time.localtime().tm_wday + 1
            report_gen_time = self._get_reporting_time(self.gene_time)
            if self.gene_time != 0 and (week_of_day not in  report_gen_time):
                return
            self._create_report(folder)
            if self.report_file is None:
                return
            self._send_mail(self.report_file)
        except Exception as e:
            self.logger.exception("Generate report job encouter issue.\nDetail: %s\n",e.args)
