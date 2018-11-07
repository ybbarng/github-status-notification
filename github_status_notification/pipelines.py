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


DATABASE = 'messages.json'
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
        database = []
        try:
            with open(DATABASE, 'r') as f:
                database = json.load(f)
        except FileNotFoundError:
            pass

        for entry in database:
            self.notified.add(entry[KEY_TIMESTAMP])
            self.latest_status = entry[KEY_STATUS]


class JsonWriterPipeline(object):

    database = []

    def close_spider(self, spider):
        if len(self.database):
            with open(DATABASE, 'w+') as f:
                json.dump(self.database, f)

    def process_item(self, item, spider):
        self.database.append(self.to_database_entry(item))
        return item

    def to_database_entry(self, item):
        return {KEY_TIMESTAMP: item['timestamp'], KEY_STATUS: item['status']}


class SlackPipeline(object):

    def process_item(self, item, spider):
        if item['notifiable']:
            timestamp = arrow.get(item['timestamp']).to('Asia/Seoul').format('hh:mm A') + ' (KST)'
            logging.info('Send to slack : {} {} {}'.format(timestamp, item['status'], item['text']))
            slack.write(timestamp, item['status'], item['text'])
        return item

