from parser import Parser
import ssl
from database import Database
from good_sales_entry import GoodSalesEntry
from proxy import Proxy

ssl._create_default_https_context = ssl._create_unverified_context
Database.execute_query('DELETE FROM facebook_goods_sales')
#goods_sales_entries = []
#goods_sales_entries.append(GoodSalesEntry(shop_url='https://test1.com', product_name='test good 1',
                                                     # product_url='https://test1.com/test_good_1', actual_stock=20,
                                                     # price=1, currency='$', update_time='2023-12-20 19:00:00'))
#goods_sales_entries.append(GoodSalesEntry(shop_url='https://test1.com', product_name='test good 1',
#                                                     product_url='https://test1.com/test_good_1', actual_stock=1,
#                                                      price=1, currency='$', update_time='2023-12-20 19:30:00'))
#goods_sales_entries.append(GoodSalesEntry(shop_url='https://test2.com', product_name='test good 2',
                                                      #product_url='https://test2.com/test_good_2', actual_stock=10,
                                                      #price=1, currency='$', update_time='2023-12-20 19:00:00'))
#goods_sales_entries.append(GoodSalesEntry(shop_url='https://test2.com', product_name='test good 2',
                                                      #product_url='https://test2.com/test_good_2', actual_stock=5,
                                                      #price=1, currency='$', update_time='2023-12-20 19:30:00'))

#Database.insert_good_sales_entries(goods_sales_entries)
#proxy = Proxy()
#goods_sales_entries = []
#goods_sales_entries.append(GoodSalesEntry(shop_url='https://test1.com', product_name='test good 1', product_url='https://test1.com/test_good_1', actual_stock=20, price = 1, currency='$', update_time='2023-12-20 19:00:00'))
#goods_sales_entries.append(GoodSalesEntry(shop_url='https://test1.com', product_name='test good 1', product_url='https://test1.com/test_good_1', actual_stock=5, price = 1, currency='$', update_time='2023-12-20 19:30:00'))
#goods_sales_entries.append(GoodSalesEntry(shop_url='https://test2.com', product_name='test good 2', product_url='https://test2.com/test_good_2', actual_stock=10, price = 1, currency='$', update_time='2023-12-20 19:00:00'))
#goods_sales_entries.append(GoodSalesEntry(shop_url='https://test2.com', product_name='test good 2', product_url='https://test2.com/test_good_2', actual_stock=5, price = 1, currency='$', update_time='2023-12-20 19:30:00'))

#shop_url, product_name, product_url, actual_stock, price, currency, update_time):
#shop_goods = Parser.get_all_shop_goods(proxy)
#shop_goods = GoodSalesEntry.remove_duplicates(shop_goods)
#shop_goods = GoodSalesEntry.get_new_good_sales_entries(shop_goods)
#print(shop_goods)
#Database.insert_good_sales_entries(shop_goods)
#GoodSalesEntry.create_xlsx_sales_report_file_from_good_sales_entries(shop_goods, 'test11.xlsx')