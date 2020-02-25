import json
import yaml
import scrapy
import requests
import pprint

from process.globalutils import logger


class Spyder:
    '''
    This class serves as a crawler.

    Makes a call to google boxes with the asin to retrieve the product info

    Gets the info parases the data in the required format

    '''
    IP_GC = ['35.224.23.138', '104.198.201.50', '35.232.148.233',
             '130.211.205.75', '35.232.191.95', '35.238.3.158']

    current_ip = ''
    count = 0

    def read_url(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        return requests.get(url, headers=headers, verify=False)

    def _strval(self, val):
        return ' '.join(''.join(val).split()).strip() if val else None

    def _processlist(self, arr):
        if(arr is not None and len(arr) > 0):
            plist = list(map(lambda v: v.strip(), arr))
            return list(filter(None, plist))
        else:
            return None

    def _processreviewrating(self, arr):
        if(arr is not None and len(arr) > 0):
            return float(arr[0].split()[0])
        else:
            return None

    def _firstItem(self, arr):
        if(arr is not None and len(arr) > 0):
            return arr[0]
        else:
            return None

    def _processreview(self, revselector):
        return {
            'rating': 0,
            'review': revselector
        }

    def read_xpath(self, selector, path, prepfn=None):
        val = selector.xpath(path).extract()
        if(val is None):
            return None
        if(prepfn is None):
            prepfn = self._strval
        return prepfn(val)

    def url_construct(self, platform, asin):

        if platform == 'Amazon':
            # url = 'https://www.amazon.com/dp/{}'.format(asin.strip())

            self.current_ip = Spyder.IP_GC[Spyder.count % len(Spyder.IP_GC)]
            Spyder.count += 1
            # print('current count{}'.format(Spyder.count))
            url = 'http://{0}/scrape?asin={1}'.format(
                self.current_ip, asin.strip())
            logger.info('construcuted url {}'.format(url))
            return url

    def _scrapecontent(self, response):
        root = scrapy.Selector(text=response.content)

        data = {
            'metaLink': self.read_xpath(root, '//link[(@rel = "canonical")]/@href'),
            'metaContent': self.read_xpath(root, '//meta[(@name = "description")]/@content'),
            'metaTitle': self.read_xpath(root, '//meta[(@name = "title")]/@content'),
            'metaKeywords': self.read_xpath(root, '//meta[(@name = "keywords")]/@content'),
            'metaPageTitle': self.read_xpath(root, '//title/text()'),
            'title': self.read_xpath(root, '//*[(@id = "productTitle")]/text()'),
            'bylineInfo': self.read_xpath(root, '//*[(@id = "bylineInfo")]/text()'),
            'bylineUrl': self.read_xpath(root, '//*[(@id = "bylineInfo")]/@href'),
            'currentReviewRating': self.read_xpath(root, '//*[(@id = "averageCustomerReviews")]/span/span/@title', self._processreviewrating),
            'noOfReviews': self.read_xpath(root, '//span[(@id = "acrCustomerReviewText")]/text()', self._processreview),
            'listItems': self.read_xpath(root, '//div[(@data-feature-name = "featurebullets")]//span[(@class="a-list-item")]/text()', self._processlist),
            'buyboxSellerName': self.read_xpath(root, '//*[(@id = "merchant-info")]/a/text()', self._firstItem),
            'fullfilledBy': self.read_xpath(root, '//*[(@id = "merchant-info")]/a/text()'),
            'merchantId': self.read_xpath(root, '//form[(@id = "addToCart")]/input[(@id="merchantID")]/@value'),
            'sellingCustomerId': self.read_xpath(root, '//form[(@id = "addToCart")]/input[(@id="sellingCustomerID")]/@value'),
            'isMerchantExclusive': self.read_xpath(root, '//form[(@id = "addToCart")]/input[(@id="isMerchantExclusive")]/@value'),
            'sellerDescription': self.read_xpath(root, '//*[(@cel_widget_id = "aplus")]'),
            'description': self.read_xpath(root, '//*[(@id = "productDescription")]'),
            'price': self.read_xpath(root, '//div[@id="cerberus-data-metrics"]/@data-asin-price'),
            'bestSeller': self.read_xpath(root, '//*[contains(concat( " ", @class, " " ), concat( " ", "p13n-best-seller-badge", " " ))]/text()')
        }

        # , (lambda v: v[1])

        r = root.xpath('//script').extract()
        images = []
        for s in r:
            if 'ImageBlockATF' in s and '\'colorImages\'' in s:
                start = s.find('\'colorImages\':')+14
                end = s.find('\'colorToAsin\'', start)
                imagesScript = s[start:end]
                f = imagesScript.strip()[13:-2]
                images = json.loads(f)

        data['images'] = images

        # 1. sponsored products
        # 2. Need more work to format this review, extract the review, rating, person, date, verified purchase, desc
        # commenting out the reviews temp
        '''revs = root.xpath(
            '//div[contains(@data-hook, "review-collapsed")]/text()')
        prevs = []

        for rev in revs:
            prevs.append({
                'review': rev.extract()
            })

        data['reviews'] = prevs'''

        if data['title']:
            logger.info('The title for the scrapped product is {0}'.format(
                data['title']))
        else:
            data['title']
            data['ip'] = self.current_ip
            logger.debug(json.dumps(data))
            logger.warn('scraping might have messed up!')

        # Extract seller name
        pd_headings = root.xpath(
            '//*[(@id = "productDetails_detailBullets_sections1")]//th/text()').extract()
        pd_tds = root.xpath(
            '//*[(@id = "productDetails_detailBullets_sections1")]//td').extract()

        if(pd_headings and pd_tds):
            for i in range(0, len(pd_headings)):
                heading = self._strval(pd_headings[i])
                root = scrapy.Selector(text=pd_tds[i])
                td_val = self._strval(root.xpath('//text()').extract())
                if(heading == 'Product Dimensions' or heading == 'Package Dimensions'):
                    data['productDimension'] = td_val
                elif (heading == 'Best Sellers Rank'):
                    data['bestSellerRank'] = td_val

        return data

    def crawl(self, product):

        # Fetch the content from the url

        try:
            url = self.url_construct(product.platform, product.asin)
            response = self.read_url(url)

            # Process the response
            data = self._scrapecontent(response)

            return data
        except Exception as e:
            logger.error(
                'There is an issue in the processing the scrapping request {0}'.format(e))

    # persist_page('https://www.amazon.com/dp/B071WBWGBT/', 'hdmi.html')
    def persist_page(self, url, filename):
        self.read_url(url)
