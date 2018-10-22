# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

from scrapy.exceptions import DropItem


DATABASE = 'messages.jl'
KEY_TIMESTAMP = 't'
KEY_STATUS = 's'


class DataTidyPipeline(object):
    def process_item(self, item, spider):
        if item['status'] is None:
            item['status'] = 'good'
        return item


class NewMessagePipeline(object):

    def open_spider(self, spider):
        self.notified = set()
        spider.latest_status = 'good'
        try:
            with open(DATABASE, 'r') as f:
                for line in f:
                    log = json.loads(line)
                    self.notified.add(log[KEY_TIMESTAMP])
                    spider.latest_status = log[KEY_STATUS]
        except FileNotFoundError:
            pass

    def process_item(self, item, spider):
        if item['timestamp'] in self.notified:
            raise DropItem('Already notified')
        self.notified.add(item['timestamp'])

        return item


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open(DATABASE, 'a+')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps({KEY_TIMESTAMP: item['timestamp'], KEY_STATUS: item['status']}) + '\n'
        self.file.write(line)
        return item


class NotifiablePipeline(object):

    def process_item(self, item, spider):
        if item['status'] == spider.latest_status == 'good':
            raise DropItem('Stable status')
        spider.latest_status = item['status']
        return item


class SlackPipeline(object):

    def process_item(self, item, spider):
        print('Send to slack : {} {} {}'.format(item['timestamp'], item['status'], item['text']))
        return item

