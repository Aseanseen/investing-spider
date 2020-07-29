import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

class InvestingSpider(scrapy.Spider):
    name = "my-investing-spider"
    def __init__(self,link='',driver=''):
        self.start_urls = [f'{link}']
        opt = webdriver.ChromeOptions()
        opt.add_argument('headless')
        opt.add_argument('disable-popup-blocking')
        self.driver = webdriver.Chrome(f'{driver}',chrome_options=opt)
    def parse(self, response):
        self.driver.get(response.url + "-income-statement")        
        yield (scrapy.Request(response.url+"-income-statement",callback=self.parse_income))
    def parse_income(self,response):
        #Use scrapy for quarterly
        quarterly_net_income = response.xpath('//*[text() = "Net Income"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
        quarterly_revenue = response.xpath('//*[text() = "Total Revenue"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
        #Click the button
        annual_button = self.driver.find_element_by_link_text('Annual')
        self.driver.execute_script('arguments[0].click()',annual_button)
        #Wait for the page to load
        wait = WebDriverWait(self.driver,1)
        wait.until(
        #ec.element_to_be_clickable((By.XPATH,"//*[text() = 'Quarterly']"))
        ec.visibility_of_element_located((By.XPATH,"//*[text() = 'Net Income']"))
        )
        #time.sleep(1)
        #Use selenium for annual
        annualy_net_income = []
        annualy_revenue = []
        for i in range(2,6):
            income = self.driver.find_element(By.XPATH,'//*[text() = "Net Income"]/../../td[position()='+str(i)+']').text
            revenue = self.driver.find_element(By.XPATH,'//*[text() = "Total Revenue"]/../../td[position()='+str(i)+']').text
            annualy_net_income.append(income)
            annualy_revenue.append(revenue)
        results_dict = {
            'quarterly_net_income': quarterly_net_income,
            'annualy_net_income': annualy_net_income,
            'quarterly_revenue': quarterly_revenue,
            'annualy_revenue': annualy_revenue
            }
        self.driver.get(response.url[:-17] + "-balance-sheet")
        yield (scrapy.Request(response.url[:-17] + "-balance-sheet",callback=self.parse_balance,cb_kwargs=results_dict))

    def parse_balance(self,response,**results_dict):
        quarterly_net_equity = response.xpath('//*[text() = "Total Equity"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
        annual_button = self.driver.find_element_by_link_text('Annual')
        self.driver.execute_script('arguments[0].click()',annual_button)
        wait = WebDriverWait(self.driver,1)
        wait.until(
        #ec.element_to_be_clickable((By.XPATH,"//*[text() = 'Quarterly']"))
        ec.visibility_of_element_located((By.XPATH,"//*[text() = 'Total Equity']"))
        )
        #time.sleep(1)
        annualy_net_equity = []
        for i in range(2,6):
            equity = self.driver.find_element(By.XPATH,'//*[text() = "Total Equity"]/../../td[position()='+str(i)+']').text
            annualy_net_equity.append(equity)
        results_dict['quarterly_net_equity'] = quarterly_net_equity
        results_dict['annualy_net_equity'] = annualy_net_equity

        self.driver.get(response.url[:-14] + "-cash-flow")
        yield (scrapy.Request(response.url[:-14] + "-cash-flow",callback=self.parse_cash,cb_kwargs=results_dict))

    def parse_cash(self,response,**results_dict):
        quarterly_operating_cash = response.xpath('//*[text() = "Cash From Operating Activities"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
        
        annual_button = self.driver.find_element_by_link_text('Annual')
        self.driver.execute_script('arguments[0].click()',annual_button)
        wait = WebDriverWait(self.driver,1)
        wait.until(
        #ec.element_to_be_clickable((By.XPATH,"//*[text() = 'Quarterly']"))
        ec.visibility_of_element_located((By.XPATH,"//*[text() = 'Cash From Operating Activities']"))
        )
        #time.sleep(1)
        annualy_operating_cash = []
        for i in range(2,6):
            cash = self.driver.find_element(By.XPATH,'//*[text() = "Cash From Operating Activities"]/../../td[position()='+str(i)+']').text
            annualy_operating_cash.append(cash)
        results_dict['quarterly_operating_cash'] = quarterly_operating_cash
        results_dict['annualy_operating_cash'] = annualy_operating_cash
        yield results_dict
