SELECT_GOOD_PREVIOUS_STOCK = (
    "SELECT * FROM facebook_goods_sales WHERE product_name = '{product_name}' "
    "ORDER BY id DESC LIMIT 1;"
)

SELECT_GOOD_DAY_SALES = (
    "SELECT SUM(sales) FROM facebook_goods_sales WHERE product_name = '{product_name}' "
    "AND SUBSTR(update_time, 1, 10) = '{update_time_date_part}';"
)

SELECT_GOOD_WEEK_SALES = (
    "SELECT SUM(sales) FROM facebook_goods_sales WHERE product_name = '{product_name}' "
    "AND DATE(update_time) >= DATE('now', 'weekday 0', '-7 days') "
    "AND DATE(update_time) <= DATE('now', 'weekday 0');"
)

SELECT_GOOD_MONTH_SALES = (
    "SELECT SUM(sales) FROM facebook_goods_sales WHERE product_name = '{product_name}' "
    "AND DATE(update_time) >= DATE('now', 'start of month') "
    "AND DATE(update_time) <= DATE('now', 'start of month', '+1 month', '-1 day');"
)

SELECT_GOOD_DAY_PROFIT = (
    "SELECT SUM(profit) FROM facebook_goods_sales WHERE product_name = '{product_name}' "
    "AND SUBSTR(update_time, 1, 10) = '{update_time_date_part}';"
)

SELECT_GOOD_WEEK_PROFIT = (
    "SELECT SUM(profit) FROM facebook_goods_sales WHERE product_name = '{product_name}' "
    "AND DATE(update_time) >= DATE('now', 'weekday 0', '-7 days') "
    "AND DATE(update_time) <= DATE('now', 'weekday 0');"
)

SELECT_GOOD_MONTH_PROFIT = (
    "SELECT SUM(profit) FROM facebook_goods_sales WHERE product_name = '{product_name}' "
    "AND DATE(update_time) >= DATE('now', 'start of month') "
    "AND DATE(update_time) <= DATE('now', 'start of month', '+1 month', '-1 day');"
)

INSERT_GOOD_SALES_ENTRIES = (
    "INSERT INTO facebook_goods_sales (shop_url, product_name, product_url, previous_stock, actual_stock, price, "
    "currency, sales, profit, update_time, day_sales, day_profit, week_sales, week_profit, month_sales, month_profit) "
    "VALUES"
)

SELECT_GOOD_DAILY_SALES_BY_HOUR = (
    "SELECT update_time, sales from facebook_goods_sales WHERE DATE(update_time) = '{today_date}'"
)

SELECT_GOOD_DAILY_PROFIT_BY_HOUR = (
    "SELECT update_time, profit from facebook_goods_sales WHERE DATE(update_time) = '{today_date}'"
)

SELECT_DAILY_SHOP_RATING_BY_PROFIT = (
    "SELECT shop_url, SUM(profit) as total_profit, SUM(sales) as total_sales "
    "FROM facebook_goods_sales "
    "WHERE DATE(update_time) = \'{today_date}\' "
    "GROUP BY shop_url "
    "HAVING total_sales > 0 " 
    "ORDER BY total_profit DESC"
)

#SELECT_GOOD_DAILY_SALES = (
#    "SELECT fb.* "
#    "FROM facebook_goods_sales fb "
#    "WHERE fb.id IN ("
#    "    SELECT MAX(id) "
#    "    FROM facebook_goods_sales "
#    "    WHERE product_name = fb.product_name "
#    "    AND DATE(update_time) = '{today_date}'"
#    "    GROUP BY product_name "
#    ") ORDER BY fb.day_profit DESC;"
#)

# NEED TO CHANGE:
SELECT_GOOD_DAILY_SALES = (
    "SELECT id, "
    "    shop_url, "
    "    product_name, "
    "    product_url, "
    "    actual_stock, "
    "    previous_stock, "
    "    price, "
    "    currency, "
    "    sales, "
    "    profit, "
    "    update_time, "
    "    day_sales, "
    "    day_profit, "
    "    week_sales, "
    "    week_profit, "
    "    month_sales, "
    "    month_profit "
    "FROM "
    "    facebook_goods_sales "
    "WHERE day_profit > 0 AND DATE(update_time) = '{today_date}' AND"
    "    (product_name, day_profit) IN ("
    "        SELECT "
    "            product_name, "
    "            MAX(day_profit) AS max_day_profit "
    "        FROM "
    "            facebook_goods_sales "
    "        GROUP BY "
    "            product_name "
    "    ) ORDER BY day_profit DESC"
)

SELECT_GOOD_SALES_PROFIT_BY_DAYS_IN_MONTH = (
    "SELECT DATE(update_time) AS sales_date, SUM(sales) AS total_sales, SUM(profit) AS total_profit "
    "FROM facebook_goods_sales "
    "WHERE DATE(update_time) >= '{start_of_month}' "
    "GROUP BY DATE(update_time)"
)


INSERT_GOOD_SALES_ENTRY_TEMPLATE = (
    "('{shop_url}', '{product_name}', '{product_url}', {previous_stock}, {actual_stock}, {price}, '{currency}', "
    "{sales}, {profit}, '{update_time}', {day_sales}, {day_profit}, {week_sales}, {week_profit}, {month_sales}, "
    "{month_profit})"
)