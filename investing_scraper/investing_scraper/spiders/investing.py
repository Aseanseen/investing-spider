import scrapy
from selenium import webdriver

class InvestingSpider(scrapy.Spider):
    name = "investing-spider"
    def __init__(self,link='',driver=''):
        self.start_urls = [f'{link}']
        self.driver = webdriver.Chrome(f'{driver}',chrome_options=webdriver.ChromeOptions().add_argument('headless'))
    def parse(self, response):
        self.driver.get(response.url + "-income-statement")        
        yield (scrapy.Request(response.url+"-income-statement",callback=self.parse_income))
        self.driver.get(response.url + "-balance-sheet") 
        yield (scrapy.Request(response.url+"-balance-sheet",callback=self.parse_balance))
        self.driver.get(response.url + "-cash-flow") 
        yield (scrapy.Request(response.url+"-cash-flow",callback=self.parse_cash)) 
    def parse_income(self,response):
        
        quarterly_net_income = response.xpath('//*[text() = "Net Income"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
        quarterly_revenue = response.xpath('//*[text() = "Total Revenue"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()

        annual_button = self.driver.find_element_by_link_text('Annual')
        annual_button.click()
        
        annualy_net_income = response.xpath('//*[text() = "Net Income"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
        annualy_revenue = response.xpath('//*[text() = "Total Revenue"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
        yield {
            'quarterly_net_income': quarterly_net_income,
            'annualy_net_income': annualy_net_income,
            'quarterly_revenue': quarterly_revenue,
            'annualy_revenue': annualy_revenue
        }

    def parse_balance(self,response):
        
        quarterly_net_equity = response.xpath('//*[text() = "Total Equity"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
        
        annual_button = self.driver.find_element_by_link_text('Annual')
        annual_button.click()
        
        annualy_net_equity = response.xpath('//*[text() = "Total Equity"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
        yield {
            'quarterly_net_equity': quarterly_net_equity,
            'annualy_net_equity': annualy_net_equity
        }

    def parse_cash(self,response):
        
        quarterly_operating_cash = response.xpath('//*[text() = "Cash From Operating Activities"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
        
        annual_button = self.driver.find_element_by_link_text('Annual')
        annual_button.click()
        
        annualy_operating_cash = response.xpath('//*[text() = "Cash From Operating Activities"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
        yield {
            'quarterly_operating_cash': quarterly_operating_cash,
            'annualy_operating_cash': annualy_operating_cash
        }

