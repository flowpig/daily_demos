# -*- coding: utf8 -*-
import time
import os

from rtm_reporting_job import  RTMRepoJob
from lib.utils.logger import Logger

class RTMReporting(object):
    def __init__(self,rtm_api,hw_report = False,tem_dir = '/var/www/html/service_robot/reports/'):
        self.is_hw_report = hw_report
        self.logger = Logger.get_logger()
        self.rtm_api = rtm_api
        self.tem_folder = tem_dir
        self.report_interval = 24 * 3600
        self.keep_report_days = 14
        self.job_list = []
        self._init_tem_folder()
        self._create_jobs()

        pass

    def _init_tem_folder(self):
        if not os.path.isdir(self.tem_folder):
            os.makedirs(self.tem_folder)

        now = time.time()
        for f_name in os.listdir(self.tem_folder):
            f = os.path.join(self.tem_folder,f_name)
            if os.stat(f).st_mtime < now - self.keep_report_days * self.report_interval:
                os.remove(f)


    def _create_jobs(self):
        jobs = self.rtm_api.reportjob.get(selectTemplates = 'extend',\
                                   selectJobHosts = ['hostid'],selectJobMails=['email'])
        for job_attr in jobs:
            self.logger.debug('Create the job %s'%(str(job_attr)))
            job  = RTMRepoJob(self.rtm_api,job_attr)
            self.job_list.append(job)


    def gene_report(self):
        for job in self.job_list:
            job.gene_report(self.tem_folder)

