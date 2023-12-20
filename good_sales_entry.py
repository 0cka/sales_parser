import sql
from database import Database
from datetime import datetime
import matplotlib.pyplot as plot
import pandas
class GoodSalesEntry:
    def __init__(self, shop_url, product_name, product_url, actual_stock, price, currency, update_time):
        self.shop_url = shop_url
        self.product_name = product_name
        self.product_url = product_url
        self.actual_stock = int(actual_stock)
        self.previous_stock = self.get_previous_stock()
        self.price = price
        self.currency = currency
        self.sales = self.calculate_sales('30 minutes')
        self.profit = self.calculate_profit('30 minutes')
        self.update_time = update_time
        self.day_sales = self.calculate_sales('day')
        self.day_profit = self.calculate_profit('day')
        self.week_sales = self.calculate_sales('week')
        self.week_profit = self.calculate_profit('week')
        self.month_sales = self.calculate_sales('month')
        self.month_profit = self.calculate_profit('month')

    def __eq__(self, other):
        return (
            isinstance(other, GoodSalesEntry) and
            #self.shop_url == other.shop_url and
            self.product_name == other.product_name and
          # self.product_url == other.product_url and
            self.actual_stock == other.actual_stock and
            self.previous_stock == other.previous_stock and
            self.price == other.price and
            self.currency == other.currency and
            self.sales == other.sales and
            self.profit == other.profit and
            self.update_time == other.update_time and
            self.day_sales == other.day_sales and
            self.day_profit == other.day_profit and
            self.week_sales == other.week_sales and
            self.week_profit == other.week_profit and
            self.month_sales == other.month_sales and
            self.month_profit == other.month_profit
        )

    @staticmethod
    def remove_duplicates(good_sales_entries):
        unique_entries = []
        for entry in good_sales_entries:
            if entry not in unique_entries:
                unique_entries.append(entry)
        return unique_entries

    @staticmethod
    def get_new_good_sales_entries(good_sales_entries):
        new_good_sales_entries = []

        for entry in good_sales_entries:
            if (entry.sales > 0 or entry.is_goods_top_up() or
                    Database.get_good_previous_stock(entry.product_name) is None):
                new_good_sales_entries.append(entry)

        return new_good_sales_entries

    @staticmethod
    def format_price(price, exchange_rate):
        if '$ / 1 шт.' in price:
            return float(price.split('$ / 1 шт.')[0])
        elif '$.' in price:
            return float(price.split('$.')[0])
        elif '$' in price:
            return float(price.split('$')[0])
        elif 'Руб. / 1 шт.' in price:
            price = float(price.split('Руб. / 1 шт.')[0])
            return price / exchange_rate
        elif 'Руб.' in price:
            price = float(price.split('Руб.')[0])
            return price / exchange_rate
        elif 'руб/шт' in price:
            price = float(price.split('руб/шт')[0])
            return price / exchange_rate
        elif '₽' in price:
            price = float(price.split('₽')[0])
            return price / exchange_rate
        elif 'р.' in price:
            price = float(price.split('р.')[0])
            return price / exchange_rate
        elif 'руб.' in price:
            price = float(price.split('руб.')[0])
            return price / exchange_rate

    @staticmethod
    def format_stock(stock):
        if 'шт.' in stock:
            return int(stock.split('шт.')[0])
        else:
            return int(stock)

    def is_goods_top_up(self):
        return self.actual_stock > self.previous_stock

    def calculate_sales(self, time_period):
        if time_period == '30 minutes':
            stock_difference = self.previous_stock - self.actual_stock
            if stock_difference > 0:
                return stock_difference
            else:
                return 0
        elif time_period == 'day':
            return float(Database.get_good_day_sales(self.product_name, self.update_time)) + self.sales
        elif time_period == 'week':
            return float(Database.get_good_week_sales(self.product_name)) + self.sales
        elif time_period == 'month':
            return float(Database.get_good_month_sales(self.product_name)) + self.sales

    def calculate_profit(self, time_period):
        if time_period == '30 minutes':
            profit = self.sales * self.price
            return profit
        elif time_period == 'day':
            return float(Database.get_good_day_profit(self.product_name, self.update_time)) + self.profit
        elif time_period == 'week':
            return float(Database.get_good_week_profit(self.product_name)) + self.profit
        elif time_period == 'month':
            return float(Database.get_good_month_profit(self.product_name)) + self.profit

    def get_previous_stock(self):
        good_previous_stock = Database.get_good_previous_stock(self.product_name)
        if good_previous_stock is not None:
            return good_previous_stock
        else:
            return self.actual_stock
    @staticmethod
    def get_overall_sales_volume(good_sales_entries):
        overall_sales_number = 0
        overall_volume = 0
        for entry in good_sales_entries:
            overall_sales_number += entry.sales
            overall_volume += entry.profit

        overall_sales_number = int(overall_sales_number)
        overall_volume = round(overall_volume, 2)

        return {'overall_sales_number': overall_sales_number, 'overall_volume': overall_volume}

    @staticmethod
    def create_daily_sales_by_hour_plot_from_good_sales_entries(filename):
        sales_data = Database.get_daily_sales_by_hour()
        sales_data['update_time'] = pandas.to_datetime(sales_data['update_time'])
        sales_data['hour'] = sales_data['update_time'].dt.hour
        hourly_sales = sales_data.groupby('hour')['sales'].sum().reset_index()
        print(hourly_sales)

        profit_data = Database.get_daily_profit_by_hour()
        profit_data['update_time'] = pandas.to_datetime(profit_data['update_time'])
        profit_data['hour'] = profit_data['update_time'].dt.hour
        hourly_profit = profit_data.groupby('hour')['profit'].sum().reset_index()

        plot.figure(figsize=(10, 6))
        plot.plot(hourly_sales['hour'], hourly_sales['sales'], label='Sales', marker='o')
        plot.plot(hourly_profit['hour'], hourly_profit['profit'], label='Profit', marker='o')
        plot.xlabel('TIME(HOUR)')
        plot.ylabel('AMOUNT')
        plot.title('DAILY SALES AND PROFIT BY HOUR, DATE: {today_date}'.format(today_date=datetime.now().date()))
        plot.legend()
        plot.xticks(range(0, 25))
        plot.grid(True)

        plot.savefig(filename)
        plot.close()

    @staticmethod
    def create_sales_profit_report_by_days_in_month(filename):
        sales_profit_by_days_in_month_data = Database.get_sales_profit_report_by_days_in_month()

        plot.plot(
            sales_profit_by_days_in_month_data['dates'],
            sales_profit_by_days_in_month_data['total_sales'], label='SALES',
            marker='o'
        )

        plot.plot(
            sales_profit_by_days_in_month_data['dates'],
            sales_profit_by_days_in_month_data['total_profit'],
            label='PROFIT',
            marker='o'
        )

        plot.xlabel('DATES')
        plot.ylabel('AMOUNT')
        plot.title('SALES/PROFIT BY DAY IN MONTH')
        plot.legend()
        plot.xticks(rotation=45)
        plot.grid(True)

        plot.tight_layout()

        plot.savefig(filename)
        plot.close()


    @staticmethod
    def create_xlsx_daily_shop_rating_by_profit(filename):
        shop_rating = Database.get_daily_shop_rating_by_profit()
        dataframe = pandas.DataFrame(shop_rating)
        dataframe.to_excel(filename, index=False)

    @staticmethod
    def create_good_daily_sales_report_sorted_by_profit(filename):
        good_daily_sales_sorted_by_profit = Database.get_good_daily_sales_sorted_by_profit()
        dataframe = pandas.DataFrame(good_daily_sales_sorted_by_profit)
        dataframe.to_excel(filename, index=False)

        overall_daily_sales = 0
        overall_daily_profit = 0

        for entry in good_daily_sales_sorted_by_profit:
            overall_daily_sales += entry['day_sales']
            overall_daily_profit += entry['day_profit']

        overall_daily_sales = int(overall_daily_sales)
        overall_daily_profit = round(overall_daily_profit, 2)

        return {'overall_daily_sales': overall_daily_sales, 'overall_daily_profit': overall_daily_profit}

    @staticmethod
    def create_xlsx_sales_report_file_from_good_sales_entries(good_sales_entries, filename):
        print('--CREATING XLSX REPORT FROM GOOD SALES ENTRIES--')
        print('--GOOD SALES ENTRIES NUMBER: %s.' % len(good_sales_entries))

        good_sales_entries_sorted_by_profit = sorted(good_sales_entries, key=lambda x: x.profit, reverse=True)

        xlsx_report_data = [
            {
                'shop_url': good_sales_entry.shop_url,
                'product_name': good_sales_entry.product_name,
                'product_url': good_sales_entry.product_url,
                'actual_stock': good_sales_entry.actual_stock,
                'previous_stock': good_sales_entry.previous_stock,
                'price': good_sales_entry.price,
                'currency': good_sales_entry.currency,
                'sales': good_sales_entry.sales,
                'profit': good_sales_entry.profit,
                'update_time': good_sales_entry.update_time,
                'day_sales': good_sales_entry.day_sales,
                'day_profit': good_sales_entry.day_profit,
                'week_sales': good_sales_entry.week_sales,
                'week_profit': good_sales_entry.week_profit,
                'month_sales': good_sales_entry.month_sales,
                'month_profit': good_sales_entry.month_profit
            }
            for good_sales_entry in good_sales_entries_sorted_by_profit
            if good_sales_entry.sales > 0
        ]

        dataframe = pandas.DataFrame(xlsx_report_data)
        dataframe.to_excel(filename, index=False)