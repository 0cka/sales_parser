from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
from good_sales_entry import GoodSalesEntry
import configurations


class Parser:

    @staticmethod
    def get_shop_urls():
        print('--PARSING SHOP URLS--')
        shops_urls = []

        for h3_element in BeautifulSoup(
                urlopen('https://lequeshop.com/goods/facebook').read().decode('utf-8'),
                'html.parser'
        ).find_all('h3'):
            span_element = h3_element.find('span', class_='label label-success')
            if span_element:
                shop_url = 'https://www.' + span_element.find_next_sibling(text=True).strip()
                print('FOUND: %s' % shop_url)
                shops_urls.append(shop_url)

        print('--SHOP URLS PARSING FINISHED--')
        return shops_urls

    @staticmethod
    def get_current_exchange_rate(currency):
        html = BeautifulSoup(
            urlopen('https://www.google.com/finance/quote/USD-' + currency).read().decode('utf-8'),
            'html.parser'
        )

        for div in html.find_all('div'):
            div_data_target = div.get('data-target')
            if div_data_target == currency:
                span_currency_rate = div.find('span')
                currency_rate = span_currency_rate.get_text(strip=True, separator=' ')
                return float(currency_rate)

    @staticmethod
    def get_all_shop_goods(proxy):
        print('--PARSING GOODS OF ALL SHOPS--')
        shop_goods = []
        proxy.set_default_proxy_settings(configurations.proxy)
        shop_urls = Parser.get_shop_urls()
        iteration_number = 0

        for shop_url in shop_urls:
            try:
                shop_goods.extend(Parser.get_shop_goods(shop_url))
                iteration_number += 1
                if iteration_number % 10 == 0:
                    print('--PARSED 10 SHOPS, CHANGING IP--')
                    proxy.change_proxy_ip()
            except Exception as e:
                print('AN EXCEPTION OCCURED WHILE PARSING GOODS OF SHOP %s.' % shop_url)

        print('--PARSING GOODS OF ALL SHOPS FINISHED.PARSED %s GOODS.' % len(shop_goods))

        proxy.set_default_proxy_settings()
        return shop_goods

    @staticmethod
    def is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
        inclusion_condition_meet = False

        for word in inclusion_words:
            if word.lower() in product_name.lower():
                inclusion_condition_meet = True
                break

        for word in exclusion_words:
            if word.lower() in product_name.lower():
                inclusion_condition_meet = False
                break

        for word in exception_goods:
            if word.lower() == product_name.lower():
                inclusion_condition_meet = True
                break

        return inclusion_condition_meet

    @staticmethod
    def append_write_line_to_file(file_name, line):
        with open(file_name, 'a') as file:
            file.write(line + '\n')

    @staticmethod
    def get_list_from_file(file_name):
        with open(file_name, 'r') as file:
            return [string.strip() for string in file.readlines()]

    @staticmethod
    def get_shop_goods(shop_url):
        print('--PARSING GOODS OF SHOP: %s.' % shop_url)
        try:
            with urlopen(shop_url, timeout=60) as response:
                html_content = response.read().decode('utf-8')
                html = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            return []

        shop_format = Parser.get_shop_format(html)

        shop_goods = []
        rubles_exchange_rate = Parser.get_current_exchange_rate('RUB')
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        inclusion_words = Parser.get_list_from_file('facebook_allow_keywords.txt')
        exclusion_words = Parser.get_list_from_file('facebook_dismiss_keywords.txt')
        exception_goods = Parser.get_list_from_file('facebook_exception_goods.txt')

        if shop_format == 'tr_goods':
            for tr_element in html.find_all('tr', class_='goods'):
                a_element = tr_element.find('a')

                # Ссылка
                product_url = shop_url + a_element.get('href')

                # Название
                product_name = a_element.get_text(strip=True, separator=' ')

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                # Цена
                price_td_element = tr_element.find('td', class_='td-price')
                price = price_td_element.get_text(strip=True, separator=' ')

                # Количество
                quantity_td_element = tr_element.find('td', class_='td-count')
                actual_stock = quantity_td_element.get_text(strip=True, separator=' ')

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url = shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)

        elif shop_format == 'tr_tt':
            for tr_element in html.find_all('tr', class_='tt'):
                # Ссылка
                product_url = shop_url

                td_elements = tr_element.find_all('td')

                name_td_element = td_elements[0]
                # Название
                product_name = name_td_element.get_text(strip=True, separator=' ')

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                price_td_element = td_elements[2]
                # Цена
                price = price_td_element.get_text(strip=True, separator=' ')

                # Количество
                quantity_td_element = td_elements[1]
                actual_stock = quantity_td_element.get_text(strip=True, separator=' ')

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url=shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)
        elif shop_format == 'div_buy__block':
            for div_element in html.find_all('div', class_='buy__block'):
                link_a_element = div_element.find('a')
                # Ссылка
                product_url = shop_url + link_a_element.get('href')

                # Название
                product_name = link_a_element.get_text(strip=True, separator=' ')

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                price_quantity_div_elements = div_element.find_all('div', class_='buy__price')

                price_div_element = price_quantity_div_elements[1]
                # Цена
                price = price_div_element.get_text(strip=True, separator=' ')

                quantity_div_element = price_quantity_div_elements[0]

                # Количество
                actual_stock = quantity_div_element.get_text(strip=True, separator=' ')

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url=shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)
            for div_element in html.find_all('div', class_='kings__block'):
                link_a_element = div_element.find('a')
                # Ссылка
                product_url = shop_url + link_a_element.get('href')

                # Название
                product_name = link_a_element.get_text(strip=True, separator=' ')

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                price_quantity_div_elements = div_element.find_all('div', class_='kings__num')

                price_div_element = price_quantity_div_elements[1]
                # Цена
                price = price_div_element.get_text(strip=True, separator=' ')

                quantity_div_element = price_quantity_div_elements[0]

                # Количество
                actual_stock = quantity_div_element.get_text(strip=True, separator=' ')

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url=shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)
        elif shop_format == 'div_product__item':
            for div_element in html.find_all('div', class_='product__item'):

                a_element = div_element.find('a')
                # Ссылка
                product_url = shop_url + a_element.get('href')
                # Название
                product_name = a_element.get_text(strip=True, separator=' ')

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                price_span_element = div_element.find('span', class_='prop--price')

                if price_span_element is not None:
                    price = price_span_element.get_text(strip=True, separator=' ')
                else:
                    price_div_element = div_element.find('div', class_='prop--price')
                    if price_div_element is not None:
                        price = price_div_element.get_text(strip=True, separator=' ')
                    else:
                        price_quantity_div_container = div_element.find('div', class_='product__item-props')
                        price_quantity_div_elements = price_quantity_div_container.find_all('div', class_='product__item-prop')
                        price_div_element = price_quantity_div_elements[1]
                        price = price_div_element.get_text(strip=True, separator=' ')

                quantity_span_element = div_element.find('span', class_='prop--pcs')
                if quantity_span_element is not None:
                    # Количество
                    actual_stock = quantity_span_element.get_text(strip=True, separator=' ')
                else:
                    quantity_div_element = div_element.find('div', class_='prop--pcs')
                    if quantity_div_element is not None:
                        actual_stock = quantity_div_element.get_text(strip=True, separator=' ')
                    else:
                        price_quantity_div_container = div_element.find('div', class_='product__item-props')
                        price_quantity_div_elements = price_quantity_div_container.find_all('div',
                                                                                            class_='product__item-prop')
                        quantity_div_element = price_quantity_div_elements[0]
                        actual_stock = quantity_div_element.get_text(strip=True, separator=' ')

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url=shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)

        elif shop_format == 'div_product-item':
            for div_element in html.find_all('div', class_='product-item'):
                a_element = div_element.find('a')
                # Ссылка
                product_url = shop_url + a_element.get('href')
                # Название
                product_name = a_element.get_text(strip=True, separator=' ')

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                price_div_element = div_element.find('div', class_='product-item-props_price')
                # Цена
                price = price_div_element.get_text(strip=True, separator=' ')

                quantity_div_element = div_element.find('div', class_='product-item-props_stock')
                # Количество
                actual_stock = quantity_div_element.get_text(strip=True, separator=' ')

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url=shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)

        elif shop_format == 'li_box-listing__item':
            for div_element in html.find_all('li', class_='box-listing__item'):
                if 'category_item' in div_element.get('class'):
                    continue

                link_a_element = div_element.find('a')
                # Ссылка
                product_url = shop_url + link_a_element.get('href')

                name_p_element = div_element.find('p')
                # Название
                product_name = name_p_element.get_text()

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                span_item_info_elements = div_element.find_all('span', class_='badge')
                # Цена
                price = span_item_info_elements[1].get_text(strip=True, separator=' ')
                # Количество
                actual_stock = span_item_info_elements[0].get_text(strip=True, separator=' ')

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url=shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)

        elif shop_format == 'div_product-item-value':
            for div_element in html.find_all('div', class_='product-item'):
                link_a_element = div_element.find('a', class_='product-item-link')

                # Ссылка
                product_url = shop_url + link_a_element.get('href')

                name_div_element = div_element.find('div', class_='product-item-title')
                # Название
                product_name = name_div_element.get_text()

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                price_quantity_div_elements = div_element.find_all('div', class_='product-item-value')
                # Цена
                price = price_quantity_div_elements[0].get_text()

                # Количество
                actual_stock = price_quantity_div_elements[1].get_text()

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url=shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)

        elif shop_format == 'div_product__item-prop_price':
            for div_element in html.find_all('div', class_='product__item'):
                link_a_element = div_element.find('a')

                # Ссылка
                product_url = shop_url + link_a_element.get('href')

                # Название
                product_name = link_a_element.get_text(strip=True, separator=' ')

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                price_div_element = div_element.find('div', class_='product__item-prop_price')

                #Цена
                price = price_div_element.get_text(strip=True, separator=' ')

                quantity_div_element = div_element.find('div', class_='product__item-prop_stock')

                # Количество
                actual_stock = quantity_div_element.get_text(strip=True, separator=' ')

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url=shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)


        elif shop_format == 'div_product__item-props_price':
            for div_element in html.find_all('div', class_='product__item'):
                link_a_element = div_element.find('a')

                # Ссылка
                product_url = shop_url + link_a_element.get('href')

                # Название
                product_name = link_a_element.get_text(strip=True, separator=' ')

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                # Цена
                price_div_element = div_element.find('div', class_='product__item-props_price')

                price = price_div_element.get_text(strip=True, separator=' ')

                quantity_div_element = div_element.find('div', class_='product__item-props_stock')
                # Количество
                actual_stock = quantity_div_element.get_text(strip=True, separator=' ')

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url=shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)

        elif shop_format == 'div_product-list__item':
            for div_element in html.find_all('div', class_='product-list__item'):
                link_a_element = div_element.find('a', class_='product-list__title')

                # Ссылка
                product_url = shop_url + link_a_element.get('href')

                # Название
                product_name = link_a_element.get_text(strip=True, separator=' ')

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                # Количество
                quantity_div_element = div_element.find('div', class_='product-list__counter')
                actual_stock = quantity_div_element.get_text(strip=True, separator=' ')

                # Цена
                price_span_element = div_element.find('div', class_='product-list__price').find('span',
                                                                                                   class_='badge')
                price = price_span_element.get_text(strip=True, separator=' ')

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url=shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)

        elif shop_format == 'table_shop_goods':
            for tr_element in html.find_all('tr'):
                td_elements = tr_element.find_all('td')
                if len(td_elements) < 4:
                    continue
                else:
                    # Ссылка
                    product_url = shop_url

                    # Название
                    product_name = td_elements[0].get_text()

                    if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                        continue

                    # Цена
                    price = td_elements[2].get_text()

                    # Количество
                    actual_stock = td_elements[1].get_text()

                    price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                    actual_stock = GoodSalesEntry.format_stock(actual_stock)

                    good_sales_entry_to_append = GoodSalesEntry(
                        shop_url=shop_url,
                        product_name=product_name,
                        product_url=product_url,
                        actual_stock=actual_stock,
                        price=price,
                        currency='$',
                        update_time=update_time,
                    )

                    shop_goods.append(good_sales_entry_to_append)

        elif shop_format == 'div_item-entry':
            for div_element in html.find_all('div', class_='item-entry'):
                # Ссылка
                product_url = shop_url

                # Название
                name_p_element = div_element.find('p', class_='i-titles')
                product_name = name_p_element.get_text(strip=True, separator=' ')

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                # Цена
                price_li_element = div_element.find('li', class_='i-price')
                price = price_li_element.get_text(strip=True, separator=' ')

                # Количество
                quantity_span_element = div_element.find('span', class_='i-value')
                actual_stock = quantity_span_element.get_text(strip=True, separator=' ')

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url=shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)

        elif shop_format == 'div_product-props_stock':
            for div_element in html.find_all('div', class_='product__item'):
                link_a_element = div_element.find('a')

                # Ссылка
                product_url = shop_url + link_a_element.get('href')

                # Название
                product_name = link_a_element.get_text(strip=True, separator=' ')

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                # Цена
                price_div_element = div_element.find('div', class_='product-props_price')
                price = price_div_element.get_text(strip=True, separator=' ')

                # Количество
                quantity_div_element = div_element.find('div', class_='product-props_stock')
                actual_stock = quantity_div_element.get_text(strip=True, separator=' ')

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url=shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)

        elif shop_format == 'div_bl__product':
            for div_element in html.find_all('div', class_='bl__product'):
                link_a_element = div_element.find('a', class_='button_product')

                # Ссылка
                product_url = shop_url + link_a_element.get('href')

                name_div_element = div_element.find('div', class_='bl__product_name')
                # Название
                product_name = name_div_element.get_text(strip=True, separator=' ')

                if not Parser.is_inclusion_condition_meet(product_name, inclusion_words, exclusion_words, exception_goods):
                    continue

                price_div_element = div_element.find('div', class_='bl__product_price')
                # Цена
                price = price_div_element.get_text(strip=True, separator=' ')

                quantity_div_element = div_element.find('div', class_='bl__product_num')
                # Количество
                actual_stock = quantity_div_element.get_text(strip=True, separator=' ')

                price = GoodSalesEntry.format_price(price, rubles_exchange_rate)
                actual_stock = GoodSalesEntry.format_stock(actual_stock)

                good_sales_entry_to_append = GoodSalesEntry(
                    shop_url=shop_url,
                    product_name=product_name,
                    product_url=product_url,
                    actual_stock=actual_stock,
                    price=price,
                    currency='$',
                    update_time=update_time,
                )

                shop_goods.append(good_sales_entry_to_append)
        elif shop_format == 'NONE':
            print('UNABLE TO DEFINE SHOP_FORMAT')

        print('--PARSING GOODS OF SHOP: %s FINISHED.PARSED %s GOODS.' % (shop_url, len(shop_goods)))
        return shop_goods

    @staticmethod
    def get_shop_format(html):
        print('--DEFINING SHOP MARKUP FORMAT--')
        if html.find_all('tr', class_='goods'):
            shop_format = 'tr_goods'
        elif html.find_all('tr', class_='tt'):
            shop_format = 'tr_tt'
        elif html.find_all('div', class_='bl__product'):
            shop_format = 'div_bl__product'
        elif html.find_all('div', class_='buy__block'):
            shop_format = 'div_buy__block'
        elif html.find_all('div', class_='product-props_stock'):
            shop_format = 'div_product-props_stock'
        elif html.find_all('div', class_='product__item-props_price'):
            shop_format = 'div_product__item-props_price'
        elif html.find_all('div', class_='product__item-prop_price'):
            shop_format = 'div_product__item-prop_price'
        elif html.find_all('div', class_='product__item'):
            shop_format = 'div_product__item'
        elif html.find_all('div', class_='product-item-value'):
            shop_format = 'div_product-item-value'
        elif html.find_all('div', class_='product-item'):
            shop_format = 'div_product-item'
        elif html.find_all('li', class_='box-listing__item'):
            shop_format = 'li_box-listing__item'
        elif html.find_all('div', class_='product-list__item'):
            shop_format = 'div_product-list__item'
        elif html.find_all('table', class_='shop_goods'):
            shop_format = 'table_shop_goods'
        elif html.find_all('div', class_='item-entry'):
            shop_format = 'div_item-entry'
        else:
            shop_format = 'NONE'

        print('--SHOP MARKUP FORMAT IS "%s"--' % shop_format)

        return shop_format
