# Ozon-products-parser
A parser that parses products and their characteristics from the catalog you need on the website https://www.ozon.ru. Output to JSON file.

How to work with this parser:
================================

Here is example of code you need to parse 1 page to json file

```html
from Parser import OzonParser

parser = OzonParser(url = "https://www.ozon.ru/category/telefony-i-smart-chasy-15501/")

parser.parse(pages_count=1)

parser.convertToJsonFile(file_name="test.json")
```

As final result we would have a json file which would like this:

![image](https://github.com/Asikul1415/Ozon-products-parser/assets/83174848/67664e03-cd05-4557-badf-0b6d41655dd5)

If you need to apply filters to search for specific products
----------------------
Go to https://www.ozon.ru. Then apply the filters you need and paste the full link into your code.

If you want to change the number of pages being parsed
-----------------------
Change the page_count argument in the parse method to the value you need

If you want to specify the path
------------------------
In the convertToJsonFile method, change the file_path argument to the one you need.

If you want to change the file name
------------------------
Change the file_name argument in the convertToJsonFile method (must contain .json at the end)

P.S
-----------------
### Why not scrapy?
Because <https://www.ozon.ru> have anti-DDOS system, which turns the spider to hell and lets it parse the Cloudflare checking page

### Why parser so slow?
This is because I use undected_chromedriver in this parser, a modified selenium to bypass anti-DDoS systems. Theoretically, you can do this faster by reducing the wait time between page parses, but most likely you will not have all the product characteristics or not all the products in the final file. You can try change wait time yourself. Maybe your computer would load pages much faster than mine.

### HTTP 404 Not Found
Check if you have the latest version of undetected_chromedriver installed
You can do this by writing this command in the terminal:

```html
pip install undetected_chromedriver --upgrade
```
