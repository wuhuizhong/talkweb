#!/usr/bin/python
#-*-coding:utf-8-*-
#https://elasticsearch-py.readthedocs.io/en/master/

from elasticsearch import Elasticsearch
from elasticsearch.client import ClusterClient
import time
import re

#配置参数
es_hosts = ['192.168.0.7:9200']
es_user = 'elastic'
es_passwd = 'changeme'
es_index = ['fluentd-']
logs_file = '/data/crontabs/root_es.log'
RESERVER_DAY=30 #日志保留天数（包括当天,至少为1）
DAY_SECOND = 24 * 60 * 60

class ES:
    def __init__(self,hosts=es_hosts,http_auth=(es_user,es_passwd)):
        self.hosts=hosts
        self.es=Elasticsearch(hosts=hosts,http_auth=http_auth)
        self.cluster = ClusterClient(self.es)

    def log(self,message):
        with open(logs_file,'a') as f: f.write(message+'\n')
        print(message)

    def delEsLogs(self,reserver_day=RESERVER_DAY):
        '''清理es日志---reserver_day:日志保留天数（包括当天）'''
        if reserver_day < 1 :raise Exception(u'参数reserver_day值异常，不能小于1.')
        cluster_state = self.cluster.state()
        indices = cluster_state['metadata']['indices']
        zero_time = time.mktime(time.strptime(time.strftime('%Y-%m-%d 00:00:00',time.localtime(time.time())), '%Y-%m-%d %H:%M:%S'))
        #对比时间为毫秒
        compare_time = (zero_time  - DAY_SECOND*(reserver_day-1))*1000
        log_str = u'[es主机:%s---执行时间:%s]-删除 %s 之前的日期的日志'%(str(self.hosts),time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(compare_time/1000)))
        self.log('--------------------------start-------------------------------------')
        self.log(log_str)
        for key,indice in indices.items():
            creation_date = int(indice['settings']['index']['creation_date'])
            if  creation_date < compare_time and self.isMatch(key):
                self.log(u'准备删除日志名称:%s,创建时间%s ' % (key, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(creation_date / 1000))))
                self.es.indices.delete(key)
                self.log(u'删除日志名称:%s,创建时间%s ' %(key,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(creation_date/1000))))
        self.log('--------------------------end---------------------------------------')

    def  isMatch(self,key,re_partten=es_index):
        for partten in es_index:
            if re.match(partten,key): return True

if __name__ == '__main__':
    pass
    # es=ES()
    # es.delEsLogs()
    # es_prod=ES(hosts=['192.168.0.9:9200'],http_auth=('elastic','talkweb_hw'))
    # es_prod.delEsLogs()