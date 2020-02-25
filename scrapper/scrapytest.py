from process.spyder.spyder import Spyder
import scrapy

spy = Spyder()
# response = spy.read_url('http://localhost:3000/testproducts/prod1.html')
response = spy.read_url('https://www.amazon.com/dp/B071WBWGBT/')

path = '//*[(@id = "productTitle")]/text()'
root = scrapy.Selector(text=response.content)
val = root.xpath(path).extract()

# with open('./scraped_data.html', 'wb') as f:
#     f.write(response.content)
