import time
import os

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

import json
import psutil


class OzonParser() : 
    __products = []
    __links_to_products = []
    __path_to_directory = os.path.abspath(__file__).replace(os.path.basename(__file__),'')
    

    def __init__(self,url: str,driver_path: str = None):
        self.url = url
        self.driver_path = driver_path
        self.driver = uc.Chrome(driver_executable_path=self.driver_path)



    def __parse_pages(self,begining_page,pages_count):
        page = begining_page 
        temp = page
        url = self.url
        if(url.count('?') == 1): 
            url += f'&page={page}'
        else: 
            url += f'/?page={page}'

        while page < temp + pages_count:
            print(f'\n\n\n\nСтраница №{page}')

            self.driver.get(url)

            scroll_position = 0
            for i in range(8):
                scroll_position += 400
                self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                time.sleep(1)

            page += 1

            self.__parse_links_to_products()

            
            #Checking if next page exist
            url_temp = self.driver.find_elements(By.CSS_SELECTOR, "[class$='tsBodyControl400Small']")
            if(url_temp != [] ):
                grapefruit_count = 0
                for _temp in url_temp:
                    if( _temp.text != 'Дальше'):
                        grapefruit_count += 1
                if(grapefruit_count != len(url_temp)):
                    url = url.replace(f'page={page-1}',f'page={page}')
                else:
                    break


        
    def __parse_links_to_products(self) -> None:
        urls = self.driver.find_elements(By.CSS_SELECTOR,"[class^='tile-hover-target']")
        for url in urls:
            href = url.get_attribute("href")
            self.__links_to_products.append(href.split('?')[0])



    def __parse_products(self):
        
        for url in self.__links_to_products:      
            product = {}
            
            print({f"\n{url}"})

            memory_percent = psutil.virtual_memory().percent

            if(memory_percent >= 75): 
                self.driver.quit()
                self.driver = uc.Chrome(driver_executable_path=self.driver_path)
                
            try:
                self.driver.get(url = url)
            except TimeoutException:
                self.driver.quit()
                self.driver = uc.Chrome(driver_executable_path=self.driver_path)
                self.driver.get(url = url)
                time.sleep(3)
            

            scroll_position = 0

            # Прокручиваем страницу до последнего элемента
            for i in range(4):
                scroll_position += 500
                self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                time.sleep(1)
            
            try:    
                price_temp = self.__parse_price()

                product['Название'] = self.__parse_name()
                product['Цена со скидкой'] = price_temp[0] #price_with_discount
                product['Цена без скидки'] = price_temp[1] #price_without_discount
                product['Рейтинг'] = self.__parse_rating()
                product['Ссылка'] = url
                self.__parse_charasterics(product = product)

                self.__products.append(product)
            except NoSuchElementException:
                print("\n\nТовар кончился\n\n")
                return


    def __parse_price(self) -> tuple[str,str]:
        prices = []

        webPrice = self.driver.find_element(By.CSS_SELECTOR,"div[data-widget='webPrice']")
        class_temp = webPrice.get_attribute("class").split()[0]
        class_temp_temp = self.driver.find_element(By.CSS_SELECTOR,f".{class_temp}")
        prices_temp = class_temp_temp.text.split('\n')

        for price in prices_temp:
            if('₽' in price):
                prices.append(price)

        price_without_discount = prices[-1]
        if(len(prices) == 3):
            price_with_discount = prices[1]
        elif(len(prices) == 2):
            price_with_discount = prices[0]
        else:
            price_with_discount = 'Нету'
        
        return (price_with_discount,price_without_discount)
         
         
    def __parse_rating(self):
        columns = self.driver.find_elements(By.CSS_SELECTOR,"div[data-widget='column']")
        for column in columns:
            if( '/ 5' in column.text ):
                return column.text.split('\n')[0]

    def __parse_name(self):   
        name_temp = self.driver.find_element(By.CSS_SELECTOR,"div[data-widget='webProductHeading']")
        
        return name_temp.text

    def __parse_charasterics(self,product):
        section_characteristics = self.driver.find_element(By.CSS_SELECTOR,"div[id='section-characteristics']")
        names_of_characteristics = section_characteristics.find_elements(By.CSS_SELECTOR, "dt")
        characteristics = section_characteristics.find_elements(By.CSS_SELECTOR, "dd")

        for i in range(len(characteristics)):
            characteristic = characteristics[i].text
            name_of_characteristic = names_of_characteristics[i].text

            if(name_of_characteristic not in product.keys()):
                product[name_of_characteristic] = characteristic


    def __exit(self):
        time.sleep(2)
        self.driver.quit()
        self.driver.service.stop()


    def parse(self,pages_count,begining_page=1):
        self.__parse_pages(begining_page,pages_count)
        self.__parse_products()
        self.__exit()
        print('Было спарсено: '  + str(len(self.__products)))
        return self.__products
    

    def printProduct(self,index):
        product = self.__products[index]
        keys = product.keys()
        for key in keys:
            print(key + ': ' + product[key])


    def convertToJsonFile(self,file_name='products.json',path=''):
        if(path == ''): path = self.__path_to_directory + file_name
        elif(path != ''): path = path + file_name

        with open(path,'w',encoding='utf-8') as json_file:
            json.dump(self.__products, json_file,indent = 2, ensure_ascii= False)


