# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import logging

import arrow
from scrapy.exceptions import DropItem

from github_status_notification import slack


DATABASE = 'messages.jl'
KEY_TIMESTAMP = 't'
KEY_STATUS = 's'

notified = set()

def load_database(spider):
    spider.latest_status = 'good'
    try:
        with open(DATABASE, 'r') as f:
            for line in f:
                log = json.loads(line)
                notified.add(log[KEY_TIMESTAMP])
                spider.latest_status = log[KEY_STATUS]
    except FileNotFoundError:
        pass


class DataTidyPipeline(object):
    def process_item(self, item, spider):
        if item['status'] is None:
            item['status'] = 'good'
        return item


class NewMessagePipeline(object):

    def process_item(self, item, spider):
        if item['timestamp'] in notified:
            raise DropItem('Already notified')
        notified.add(item['timestamp'])
        return item


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        load_database(spider)
        self.file = open(DATABASE, 'w+')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps({KEY_TIMESTAMP: item['timestamp'], KEY_STATUS: item['status']}) + '\n'
        self.file.write(line)
        return item


class NotifiablePipeline(object):

    def process_item(self, item, spider):
        if item['status'] == spider.latest_status == 'good':
            raise DropItem('Stable status: old == new == \'good\'')
        spider.latest_status = item['status']
        return item


class SlackPipeline(object):

    def process_item(self, item, spider):
        timestamp = arrow.get(item['timestamp']).to('Asia/Seoul').format('hh:mm A') + ' (KST)'
        logging.info('Send to slack : {} {} {}'.format(timestamp, item['status'], item['text']))
        slack.write(timestamp, item['status'], item['text'])
        return item

