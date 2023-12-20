import types

from aiogram import Bot, types
from aiogram.utils import executor
import textwrap
from aiogram.dispatcher import Dispatcher
import asyncio
import ssl
from parser import Parser
from database import Database
from good_sales_entry import GoodSalesEntry
from datetime import datetime, timedelta
import json
from proxy import Proxy
import configurations
import os


def get_date_from_file():
    with open('dates.txt', 'r') as file:
        try:
            return json.load(file)
        except Exception as e:
            print(e)
            return []


def write_date_to_file(dates):
    with open('dates.txt', 'w') as file:
        json.dump(dates, file)


def get_time_from_file():
    with open('time.txt', 'r') as file:
        try:
            return json.load(file)
        except Exception as e:
            print(e)
            return []


def write_time_to_file(dates):
    with open('time.txt', 'w') as file:
        json.dump(dates, file)


def daily_reports_sent_today():
    current_datetime = datetime.now()
    dates = get_date_from_file()
    if dates:
        if datetime.strptime(dates[-1], '%Y-%m-%d %H:%M:%S').date() == current_datetime.date():
            return True
        else:
            dates.append(current_datetime.strftime("%Y-%m-%d %H:%M:%S"))
            write_date_to_file(dates)
            return False
    else:
        dates.append(current_datetime.strftime("%Y-%m-%d %H:%M:%S"))
        write_date_to_file(dates)
        return False


def time_passed(minutes):
    current_datetime = datetime.now()
    time = get_time_from_file()
    if time:
        if (current_datetime - datetime.strptime(time[-1], '%Y-%m-%d %H:%M:%S')) >= timedelta(minutes=minutes):
            time.append(current_datetime.strftime("%Y-%m-%d %H:%M:%S"))
            write_time_to_file(time)
            return True
        else:
            return False
    else:
        time.append(current_datetime.strftime("%Y-%m-%d %H:%M:%S"))
        write_time_to_file(time)
        return True


async def send_xlsx_file(bot, filename):
    with open(filename, 'rb') as file:
        await bot.send_document(configurations.reports_telegram_chat_id, file)
    os.remove(filename)


async def send_photo(bot, filename):
    with open(filename, 'rb') as file:
        await bot.send_photo(configurations.reports_telegram_chat_id, file)
    os.remove(filename)


async def monitor(bot, proxy):
    while True:
        await asyncio.sleep(10)
        if time_passed(minutes=30):
            current_date_time = datetime.now()

            goods_sales_entries = Parser.get_all_shop_goods(proxy)

            goods_sales_entries = Parser.get_shop_goods('https://hq-accounts.com')
            if goods_sales_entries is None or not goods_sales_entries:
                continue

            goods_sales_entries = GoodSalesEntry.remove_duplicates(goods_sales_entries)
            goods_sales_entries = GoodSalesEntry.get_new_good_sales_entries(goods_sales_entries)
            Database.insert_good_sales_entries(goods_sales_entries)

            GoodSalesEntry.create_daily_sales_by_hour_plot_from_good_sales_entries(
                filename=current_date_time.strftime("%Y_%m_%d_%H_%M") + '_daily_sales_by_hour.png'
            )

            await send_photo(bot, current_date_time.strftime("%Y_%m_%d_%H_%M") + '_daily_sales_by_hour.png')

            GoodSalesEntry.create_xlsx_sales_report_file_from_good_sales_entries(
                goods_sales_entries,
                '30_minutes_sales_report(%s).xlsx' % current_date_time.strftime("%Y_%m_%d_%H_%M")
            )

            await send_xlsx_file(bot, '30_minutes_sales_report(%s).xlsx' % current_date_time.strftime("%Y_%m_%d_%H_%M"))

            report_text = textwrap.dedent("""
            <b>Отчёт за последние 30 минут</b>
            Время на сервере: {time_on_server}
            
            Проданные аккаунты: {overall_sales_number} шт.
            Оборот: {overall_volume} $
            """)

            overall_sales_volume = GoodSalesEntry.get_overall_sales_volume(goods_sales_entries)

            report_text = report_text.format(
                time_on_server=current_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                overall_sales_number=overall_sales_volume['overall_sales_number'],
                overall_volume=overall_sales_volume['overall_volume']
            )

            await bot.send_message(
                configurations.reports_telegram_chat_id,
                report_text,
                parse_mode=types.ParseMode.HTML
            )

            if current_date_time.hour == 23 and not daily_reports_sent_today():
                report_text = '<b>Отчёт с рейтингом магазинов по продажам за 24 часа</b>'

                await bot.send_message(
                    configurations.reports_telegram_chat_id,
                    report_text,
                    parse_mode=types.ParseMode.HTML
                )

                GoodSalesEntry.create_xlsx_daily_shop_rating_by_profit(
                    'daily_shop_rating(%s).xlsx' % current_date_time.strftime("%Y_%m_%d")
                )

                await send_xlsx_file(bot, 'daily_shop_rating(%s).xlsx' % current_date_time.strftime("%Y_%m_%d"))

                overall_daily_sales_volume = GoodSalesEntry.create_good_daily_sales_report_sorted_by_profit(
                    'daily_good_sales_report(%s).xlsx' % current_date_time.strftime("%Y_%m_%d")
                )

                GoodSalesEntry.create_sales_profit_report_by_days_in_month(
                    current_date_time.strftime("%Y_%m_%d_%H_%M") + '_day_in_month_report.png'
                )

                await send_photo(bot, current_date_time.strftime("%Y_%m_%d_%H_%M") + '_day_in_month_report.png')

                report_text = textwrap.dedent("""
                                        <b>Отчёт за прошедший день</b>
                                        Время на сервере: {time_on_server}

                                        Проданные аккаунты: {overall_daily_sales} шт.
                                        Оборот: {overall_daily_profit} $
                                        """)

                report_text = report_text.format(
                    time_on_server=current_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                    overall_daily_sales=overall_daily_sales_volume['overall_daily_sales'],
                    overall_daily_profit=overall_daily_sales_volume['overall_daily_profit']
                )

                await bot.send_message(
                    configurations.reports_telegram_chat_id,
                    report_text,
                    parse_mode=types.ParseMode.HTML
                )

                await send_xlsx_file(bot, 'daily_good_sales_report(%s).xlsx' % current_date_time.strftime("%Y_%m_%d"))

bot = Bot(configurations.bot_telegram_token)
dispatcher = Dispatcher(bot)
event_loop = asyncio.get_event_loop()
proxy = Proxy()
ssl._create_default_https_context = ssl._create_unverified_context
event_loop.create_task(monitor(bot, proxy))
executor.start_polling(dispatcher, skip_updates=True)