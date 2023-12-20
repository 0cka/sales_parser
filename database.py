#from psycopg2 import connect
import sqlite3
from configurations import database
import sql
from datetime import datetime
import pandas

class Database:

    @staticmethod
    def execute_query(query):
        print('--QUERY EXECUTION--')
        print('QUERY TO EXECUTE: %s' % query)
        try:
            connection = sqlite3.connect(
                'sales_parser.db')
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            try:
                print('--QUERY SUCCESSFULLY EXECUTED--')
                return cursor.fetchall()
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)
    @staticmethod
    def get_good_previous_stock(product_name):
        select_good_previous_stock = sql.SELECT_GOOD_PREVIOUS_STOCK.format(product_name=product_name.replace("'", "''"))

        good_previous_stock_row = Database.execute_query(select_good_previous_stock)
        print(good_previous_stock_row)
        if good_previous_stock_row is not None and good_previous_stock_row:
            good_previous_stock = good_previous_stock_row[0][5]
            return good_previous_stock
        else:
            return None

    @staticmethod
    def get_good_day_sales(product_name, update_time):
        select_good_day_sales = sql.SELECT_GOOD_DAY_SALES.format(
            product_name=product_name.replace("'", "''"),
            update_time_date_part=update_time[0:11]
        )

        good_day_sales_row = Database.execute_query(select_good_day_sales)
        if good_day_sales_row is not None and good_day_sales_row[0][0] is not None:
            print(good_day_sales_row)
            good_day_sales = good_day_sales_row[0][0]
            return good_day_sales
        else:
            return 0

    @staticmethod
    def get_good_week_sales(product_name):
        select_good_week_sales = sql.SELECT_GOOD_WEEK_SALES.format(
            product_name=product_name.replace("'", "''")
        )

        good_week_sales_row = Database.execute_query(select_good_week_sales)
        if good_week_sales_row is not None and good_week_sales_row[0][0] is not None:
            good_week_sales = good_week_sales_row[0][0]
            return good_week_sales
        else:
            return 0

    @staticmethod
    def get_good_month_sales(product_name):
        select_good_month_sales = sql.SELECT_GOOD_MONTH_SALES.format(
            product_name=product_name.replace("'", "''")
        )

        good_month_sales_row = Database.execute_query(select_good_month_sales)
        if good_month_sales_row is not None and good_month_sales_row[0][0] is not None:
            good_month_sales = good_month_sales_row[0][0]
            return good_month_sales
        else:
            return 0

    @staticmethod
    def get_good_day_profit(product_name, update_time):
        select_good_day_profit = sql.SELECT_GOOD_DAY_PROFIT.format(
            product_name=product_name.replace("'", "''"),
            update_time_date_part=update_time[0:11]
        )

        good_day_profit_row = Database.execute_query(select_good_day_profit)
        if good_day_profit_row is not None and good_day_profit_row[0][0] is not None:
            good_day_sales = good_day_profit_row[0][0]
            return good_day_sales
        else:
            return 0

    @staticmethod
    def get_good_week_profit(product_name):
        select_good_week_profit = sql.SELECT_GOOD_WEEK_PROFIT.format(
            product_name=product_name.replace("'", "''")
        )

        good_week_profit_row = Database.execute_query(select_good_week_profit)
        if good_week_profit_row is not None and good_week_profit_row[0][0] is not None:
            good_week_profit = good_week_profit_row[0][0]
            return good_week_profit
        else:
            return 0

    @staticmethod
    def get_good_month_profit(product_name):
        select_good_month_profit = sql.SELECT_GOOD_MONTH_PROFIT.format(
            product_name=product_name.replace("'", "''")
        )

        good_month_profit_row = Database.execute_query(select_good_month_profit)
        if good_month_profit_row is not None and good_month_profit_row[0][0] is not None:
            good_month_profit = good_month_profit_row[0][0]
            return good_month_profit
        else:
            return 0

    @staticmethod
    def get_daily_sales_by_hour():
        try:
            connection = sqlite3.connect('sales_parser.db')
            today_date = datetime.now().date()
            select_good_daily_sales_by_hour = sql.SELECT_GOOD_DAILY_SALES_BY_HOUR.format(today_date=today_date)
            print(sql.SELECT_GOOD_DAILY_SALES_BY_HOUR.format(today_date=today_date))
            data_frame = pandas.read_sql_query(select_good_daily_sales_by_hour, connection)
            return data_frame
        except Exception as e:
            print(e)
            pass

    @staticmethod
    def get_daily_profit_by_hour():
        try:
            connection = sqlite3.connect('sales_parser.db')
            today_date = datetime.now().date()
            select_good_daily_profit_by_hour = sql.SELECT_GOOD_DAILY_PROFIT_BY_HOUR.format(today_date=today_date)
            print(sql.SELECT_GOOD_DAILY_PROFIT_BY_HOUR.format(today_date=today_date))
            data_frame = pandas.read_sql_query(select_good_daily_profit_by_hour, connection)
            return data_frame
        except Exception as e:
            print(e)
            pass

    @staticmethod
    def get_sales_profit_report_by_days_in_month():
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_month_str = start_of_month.strftime('%Y-%m-%d')

        select_good_sales_profit_by_days_in_month = sql.SELECT_GOOD_SALES_PROFIT_BY_DAYS_IN_MONTH.format(
            start_of_month = start_of_month_str
        )

        sales_profit_report_by_days_in_month = Database.execute_query(select_good_sales_profit_by_days_in_month)

        dates = [item[0] for item in sales_profit_report_by_days_in_month]
        total_sales = [item[1] for item in sales_profit_report_by_days_in_month]
        total_profit = [item[2] for item in sales_profit_report_by_days_in_month]

        return {'dates': dates, 'total_sales': total_sales, 'total_profit': total_profit}



    @staticmethod
    def get_daily_shop_rating_by_profit():
        today_date = datetime.now().date()
        select_daily_shop_rating_by_profit = sql.SELECT_DAILY_SHOP_RATING_BY_PROFIT.format(today_date=today_date)
        shops_data = Database.execute_query(select_daily_shop_rating_by_profit)

        daily_shop_rating_by_profit = []

        for shop_data in shops_data:
            shop_url, daily_profit, daily_sales = shop_data
            daily_shop_rating_by_profit.append(
                {
                    'shop_url': shop_url,
                    'daily_profit': daily_profit,
                    'daily_sales': daily_sales
                }
            )

        return daily_shop_rating_by_profit

    @staticmethod
    def get_good_daily_sales_sorted_by_profit():
        today_date = datetime.now().date()
        select_good_daily_sales = sql.SELECT_GOOD_DAILY_SALES.format(today_date=today_date)
        goods_data = Database.execute_query(select_good_daily_sales)
        print(goods_data)
        good_daily_sales_sorted_by_profit = []

        for good_data in goods_data:
            good_daily_sales_sorted_by_profit.append(
                {
                    'id': good_data[0],
                    'shop_url': good_data[1],
                    'product_name': good_data[2],
                    'product_url': good_data[3],
                    'actual_stock': good_data[4],
                    'previous_stock': good_data[5],
                    'price': good_data[6],
                    'currency': good_data[7],
                    'sales': good_data[8],
                    'profit': good_data[9],
                    'update_time': good_data[10],
                    'day_sales': good_data[11],
                    'day_profit': good_data[12],
                    'week_sales': good_data[13],
                    'week_profit': good_data[14],
                    'month_sales': good_data[15],
                    'month_profit': good_data[16]
                }
            )

        return good_daily_sales_sorted_by_profit

    @staticmethod
    def insert_good_sales_entries(good_sales_entries):
        insert_good_sales_entries = sql.INSERT_GOOD_SALES_ENTRIES
        for good_sales_entry in good_sales_entries:
            insert_good_sales_entries += sql.INSERT_GOOD_SALES_ENTRY_TEMPLATE.format(
                shop_url=good_sales_entry.shop_url,
                product_name=good_sales_entry.product_name.replace("'", "''"),
                product_url=good_sales_entry.product_url,
                previous_stock=good_sales_entry.previous_stock,
                actual_stock=good_sales_entry.actual_stock,
                price=good_sales_entry.price,
                currency=good_sales_entry.currency,
                sales=good_sales_entry.sales,
                profit=good_sales_entry.profit,
                update_time=good_sales_entry.update_time,
                day_sales=good_sales_entry.day_sales,
                day_profit=good_sales_entry.day_profit,
                week_sales=good_sales_entry.week_sales,
                week_profit=good_sales_entry.week_profit,
                month_sales=good_sales_entry.month_sales,
                month_profit=good_sales_entry.month_profit
            )

            insert_good_sales_entries += ','

        insert_good_sales_entries = insert_good_sales_entries[:-1] + ';'
        Database.execute_query(insert_good_sales_entries)