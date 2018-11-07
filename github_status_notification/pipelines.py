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


class DataTidyPipeline(object):
    def process_item(self, item, spider):
        if item['status'] is None:
            item['status'] = 'good'
        return item


class NewMessagePipeline(object):

    notified = set()
    latest_status = 'good'

    def open_spider(self, spider):
        self.load_database()

    def process_item(self, item, spider):
        if item['timestamp'] in self.notified:
            raise DropItem('Already notified')

        if item['status'] == self.latest_status == 'good':
            logging.info('Stable status: old == new == \'good\'')
            item['notifiable'] = False
        else:
            item['notifiable'] = True
        self.notified.add(item['timestamp'])
        self.latest_status = item['status']
        return item

    def load_database(self):
        try:
            with open(DATABASE, 'r') as f:
                for line in f:
                    log = json.loads(line)
                    self.notified.add(log[KEY_TIMESTAMP])
                    self.latest_status = log[KEY_STATUS]
        except FileNotFoundError:
            pass


class JsonWriterPipeline(object):

    items = []

    def close_spider(self, spider):
        if len(self.items):
            with open(DATABASE, 'w+') as f:
                for item in self.items:
                    line = json.dumps({KEY_TIMESTAMP: item['timestamp'], KEY_STATUS: item['status']}) + '\n'
                    f.write(line)

    def process_item(self, item, spider):
        self.items.append(item)
        return item


class SlackPipeline(object):

    def process_item(self, item, spider):
        if item['notifiable']:
            timestamp = arrow.get(item['timestamp']).to('Asia/Seoul').format('hh:mm A') + ' (KST)'
            logging.info('Send to slack : {} {} {}'.format(timestamp, item['status'], item['text']))
            slack.write(timestamp, item['status'], item['text'])
        return item

