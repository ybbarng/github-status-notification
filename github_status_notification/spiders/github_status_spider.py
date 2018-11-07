import scrapy

class GithubStatusSpider(scrapy.Spider):
    name = 'github-status'

    custom_settings = {
        'ITEM_PIPELINES': {
            'github_status_notification.pipelines.DataTidyPipeline': 1,
            'github_status_notification.pipelines.JsonWriterPipeline': 2,
            'github_status_notification.pipelines.NewMessagePipeline': 3,
            'github_status_notification.pipelines.SlackPipeline': 4,
        }
    }

    def start_requests(self):
        urls = ['https://status.github.com/messages']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for message in reversed(response.css('.message')):
            status = message.css('::attr(data-status)').extract_first()
            if status is None:
                status = 'good'
            timestamp = message.css('time::attr(datetime)').extract_first()
            text = message.css('span::text').extract_first()
            yield {
                'timestamp': timestamp,
                'status': status,
                'text': text,
            }
