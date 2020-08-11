import scrapy
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

class InvestSpider(scrapy.Spider):
    name = "my-bank-investing-spider"
    urls=[]
    def __init__(self,inv_link='',yahoo_link='',driver=''):
        self.urls.append(f'{yahoo_link}')
        self.start_urls = [f'{inv_link}']
        opt = webdriver.ChromeOptions()
        opt.add_argument('disable-popup-blocking')
        self.driver = webdriver.Chrome(f'{driver}',chrome_options=opt)
    def parse(self, response):
        self.driver.get(response.url + "-income-statement")
        yield (scrapy.Request(response.url+"-income-statement",callback=self.parse_income))
    def parse_income(self,response):
        #Use scrapy for quarterly
        quarterly_net_income = response.xpath('//*[text() = "Net Income"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
        #quarterly_revenue = response.xpath('//*[text() = "Total Revenue"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
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
        #annualy_revenue = []
        for i in range(2,6):
            income = self.driver.find_element(By.XPATH,'//*[text() = "Net Income"]/../../td[position()='+str(i)+']').text
            #revenue = self.driver.find_element(By.XPATH,'//*[text() = "Total Revenue"]/../../td[position()='+str(i)+']').text
            annualy_net_income.append(income)
            #annualy_revenue.append(revenue)
        quarterly_revenue = []
        annualy_revenue = []
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
        annual_debt = []
        for i in range(2,6):
            equity = self.driver.find_element(By.XPATH,'//*[text() = "Total Equity"]/../../td[position()='+str(i)+']').text
            debt = self.driver.find_element(By.XPATH,'//*[text() = "Total Long Term Debt"]/../../td[position()='+str(i)+']').text
            annualy_net_equity.append(equity)
            annual_debt.append(debt)
        results_dict['quarterly_net_equity'] = quarterly_net_equity
        results_dict['annualy_net_equity'] = annualy_net_equity
        results_dict['annual_debt']=annual_debt

        self.driver.get(response.url[:-14] + "-cash-flow")
        yield (scrapy.Request(response.url[:-14] + "-cash-flow",callback=self.parse_cash,cb_kwargs=results_dict))

    def parse_cash(self,response,**results_dict):
        quarterly_operating_cash = response.xpath('//*[text() = "Cash From Operating Activities"]/../../td[position()=2 or position()=3 or position()=4 or position()=5]/text()').getall()
        annual_button = self.driver.find_element_by_link_text('Annual')
        self.driver.execute_script('arguments[0].click()',annual_button)
        wait = WebDriverWait(self.driver,1)
        wait.until(
        ec.visibility_of_element_located((By.XPATH,"//*[text() = 'Cash From Operating Activities']"))
        )
        #time.sleep(1)
        annualy_operating_cash = []
        for i in range(2,6):
            cash = self.driver.find_element(By.XPATH,'//*[text() = "Cash From Operating Activities"]/../../td[position()='+str(i)+']').text
            annualy_operating_cash.append(cash)
        results_dict['quarterly_operating_cash'] = quarterly_operating_cash
        results_dict['annualy_operating_cash'] = annualy_operating_cash
        self.driver.get(response.url[:-10] + "-ratios")
        yield (scrapy.Request(response.url[:-10] + "-ratios",callback=self.parse_ratios,cb_kwargs=results_dict)) 
        #yield results_dict
    def parse_ratios(self,response,**results_dict):
        pe_ratio = response.xpath('//*[text() = "P/E Ratio "]/../../td[position()=2 or position()=3]/text()').getall()
        psr = response.xpath('//*[text() = "Price to Sales "]/../../td[position()=2 or position()=3]/text()').getall()
        roe = response.xpath('//*[text() = "Return on Equity "]/../../td[position()=2 or position()=3]/text()').getall()
        roa = response.xpath('//*[text() = "Return on Assets "]/../../td[position()=2 or position()=3]/text()').getall() 
        payout_ratio = response.xpath('//*[text() = "Payout Ratio "]/../../td[position()=2 or position()=3]/text()').getall() 
        profit_margin = response.xpath('//*[text() = "Net Profit margin "]/../../td[position()=2 or position()=3]/text()').getall()
        results_dict['ttm_industry_pe_ratio'] = pe_ratio
        results_dict['ttm_industry_psr'] = psr
        results_dict['ttm_industry_5ya_industry_roe'] = roe
        results_dict['ttm_industry_5ya_industry_roa'] = roa
        results_dict['ttm_industry_payout_ratio'] = payout_ratio
        results_dict['ttm_industry_5ya_industry_profit_margin'] = profit_margin
        
        self.driver.get(self.urls[0])
        yield(scrapy.Request(self.urls[0],callback=self.parse_yahoo,cb_kwargs=results_dict))

    # Yahoo page
    def parse_yahoo(self, response,**results_dict):
        self.driver.get(response.url)  
        #Wait for the page to load
        wait = WebDriverWait(self.driver,5)
        wait.until(
        ec.visibility_of_element_located((By.XPATH,"//*[contains(@data-test,'EPS_RATIO-value')]"))
        )
        time.sleep(1)
        #Take EPS,PE data
        eps = self.driver.find_element(By.XPATH,"//*[contains(@data-test,'EPS_RATIO-value')]").text
        pe = self.driver.find_element(By.XPATH,"//*[contains(@data-test,'PE_RATIO-value')]").text
        #Click Financials
        financials_button = self.driver.find_element_by_link_text('Financials')
        self.driver.execute_script('arguments[0].click()',financials_button)
        #Wait for the page to load
        wait = WebDriverWait(self.driver,5)
        wait.until(
        ec.visibility_of_element_located((By.XPATH,"//*[contains(@title,'Net income')]"))
        )
        time.sleep(1)
        #Take data from Income
        net_income = self.driver.find_element(By.XPATH,"//*[contains(@title,'Net income')]/../../div[position()=2]").text
        income_tax = self.driver.find_element(By.XPATH,"//*[contains(@title,'Income tax expense')]/../../div[position()=2]").text
        
        quarterly_revenue = []
        annualy_revenue = []
        for i in range(3,7):
            rev = self.driver.find_element(By.XPATH,"//*[contains(@title,'Total revenue')]/../../div[position()="+str(i)+']').text
            annualy_revenue.append(rev)
        
        #Click quarterly
        quarterly_button = self.driver.find_element(By.XPATH,"//*[span/text()='Quarterly']/..")
        self.driver.execute_script('arguments[0].click()',quarterly_button)
        time.sleep(1)
        for i in range(3,7):
            rev = self.driver.find_element(By.XPATH,"//*[contains(@title,'Total revenue')]/../../div[position()="+str(i)+']').text
            quarterly_revenue.append(rev)
        results_dict['quarterly_revenue'] = quarterly_revenue
        results_dict['annualy_revenue'] = annualy_revenue

        #Click Cash flow
        cash_flow_button = self.driver.find_element_by_link_text('Cash flow')
        self.driver.execute_script('arguments[0].click()',cash_flow_button)
        #Wait for the page to load
        wait = WebDriverWait(self.driver,5)
        wait.until(
        ec.visibility_of_element_located((By.XPATH,"//*[contains(@title,'Net income')]"))
        )
        time.sleep(1)
        #Take data from Cash flow
        #amt_receivable_ttm = self.driver.find_element(By.XPATH,"//*[contains(@title,'Accounts receivable')]/../../div[position()=2]").text
        #amt_receivable_1 = self.driver.find_element(By.XPATH,"//*[contains(@title,'Accounts receivable')]/../../div[position()=3]").text
        #amt_receivable_2 = self.driver.find_element(By.XPATH,"//*[contains(@title,'Accounts receivable')]/../../div[position()=4]").text 
        #Accounts payable choice
        #amt_payable = self.driver.find_element(By.XPATH,"//*[contains(@title,'Accounts payable')]/../../div[position()=2]").text
        capital_expen = self.driver.find_element(By.XPATH,"//*[contains(@title,'Capital expenditure')]/../../div[position()=3]").text
        free_cash_flow = self.driver.find_elements(By.XPATH,"//*[contains(@title,'Free cash flow')]/../../div[position()=3]")
        free_cash_flow = free_cash_flow[1].text
        depre_amor = self.driver.find_element(By.XPATH,"//*[contains(@title,'Depreciation & amortisation')]/../../div[position()=3]").text
 
        #Accounts payable choice
        #Click Balance Sheet
        #balance_button = self.driver.find_element_by_link_text('Balance sheet')
        #self.driver.execute_script('arguments[0].click()',balance_button)
        #Wait for the page to load
        #wait = WebDriverWait(self.driver,5)
        #wait.until(
        #ec.visibility_of_element_located((By.XPATH,"//*[contains(@title,'Total cash')]"))
        #)
        #amt_payable = self.driver.find_element(By.XPATH,"//*[contains(@title,'Accounts payable')]/../../div[position()=2]").text
        #amt_receivable_ttm = self.driver.find_element(By.XPATH,"//*[contains(@title,'Net receivable')]/../../div[position()=2]").text
        #amt_receivable_1 = self.driver.find_element(By.XPATH,"//*[contains(@title,'Net receivable')]/../../div[position()=3]").text
        #amt_receivable_2 = self.driver.find_element(By.XPATH,"//*[contains(@title,'Net receivable')]/../../div[position()=4]").text 
        
        #Note: these data appear to not be available for DBS, hence the '0'
        amt_receivable_ttm = '0'
        amt_receivable_1 = '0'
        amt_receivable_2 = '0'
        amt_payable = '0'
        #Corrects the values to proper numbers
        l = [net_income,income_tax,depre_amor,amt_receivable_ttm,amt_receivable_1,amt_receivable_2,amt_payable,capital_expen,free_cash_flow]
        for n in range(len(l)):
            if (l[n] == '-' or l[n] == 'N/A' or l[n] == '0'):
                l[n] = '0'
            else:
                l[n] += ',000'
        #Click Statistics
        stats_button = self.driver.find_element_by_link_text('Statistics')
        self.driver.execute_script('arguments[0].click()',stats_button)
        #Wait for the page to load
        wait = WebDriverWait(self.driver,10)
        wait.until(
        ec.visibility_of_element_located((By.XPATH,"//*[span/text()='PEG Ratio (5 yr expected)']"))
        )
        peg = self.driver.find_element(By.XPATH,"//*[span/text()='PEG Ratio (5 yr expected)']/../td[position()=2]").text
        psr = self.driver.find_element(By.XPATH,"//*[span/text()='Price/sales']/../td[position()=2]").text

        roa = self.driver.find_element(By.XPATH,"//*[span/text()='Return on assets']/../td[position()=2]").text
        roe = self.driver.find_element(By.XPATH,"//*[span/text()='Return on equity']/../td[position()=2]").text
        payout_ratio = self.driver.find_element(By.XPATH,"//*[span/text()='Payout ratio']/../td[position()=2]").text
        profit_margin = self.driver.find_element(By.XPATH,"//*[span/text()='Profit margin']/../td[position()=2]").text
        levered_free_cash = self.driver.find_element(By.XPATH,"//*[span/text()='Levered free cash flow']/../td[position()=2]").text 
        num_shares = self.driver.find_element(By.XPATH,"//*[span/text()='Shares outstanding']/../td[position()=2]").text
        if (eps == '-' or eps == 'N/A' or eps == '0'):
            eps = '0'
        if (levered_free_cash == '-' or levered_free_cash == 'N/A' or levered_free_cash == '0'):
            levered_free_cash = '0'
        if (peg == '-' or peg == 'N/A' or peg == '0'):
            peg = '0'
        results_dict['ttm_eps,peg,ttm_levered_cash'] = [eps,peg,levered_free_cash]
        results_dict['ttm_net_income,ttm_income_tax,ttm_depre'] = [l[0],l[1],l[2]]
        results_dict['ttm_receivable,receivable_1,receivable_2,ttm_payable'] = [l[3],l[4],l[5],l[6]]
        results_dict['ttm_capital_expen,ttm_free_cash_flow,num_shares'] = [l[7],l[8],num_shares]
        
        yield results_dict
