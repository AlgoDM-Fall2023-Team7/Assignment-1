import os

queries = {
    "Query1": {
        "sql": """
        SELECT promotions, total, CAST(promotions AS DECIMAL(17, 4)) / CAST(total AS DECIMAL(17, 4)) * 100
        FROM
          (SELECT SUM(ss_ext_sales_price) AS promotions
           FROM  {database}.{schema}.store_sales
                ,{database}.{schema}.store
                ,{database}.{schema}.promotion
                ,{database}.{schema}.date_dim
                ,{database}.{schema}.customer
                ,{database}.{schema}.customer_address 
                ,{database}.{schema}.item
           WHERE ss_sold_date_sk = d_date_sk
           AND   ss_store_sk = s_store_sk
           AND   ss_promo_sk = p_promo_sk
           AND   ss_customer_sk = c_customer_sk
           AND   ca_address_sk = c_current_addr_sk
           AND   ss_item_sk = i_item_sk 
           AND   ca_gmt_offset = {GMT}
           AND   i_category = '{CATEGORY}'
           AND   (p_channel_dmail = 'Y' OR p_channel_email = 'Y' OR p_channel_tv = 'Y')
           AND   s_gmt_offset = '{GMT}'
           AND   d_year = {YEAR}
           AND   d_moy  = {MONTH}) promotional_sales,
          (SELECT SUM(ss_ext_sales_price) AS total
           FROM  {database}.{schema}.store_sales
                ,{database}.{schema}.store
                ,{database}.{schema}.date_dim
                ,{database}.{schema}.customer
                ,{database}.{schema}.customer_address
                ,{database}.{schema}.item
           WHERE ss_sold_date_sk = d_date_sk
           AND   ss_store_sk = s_store_sk
           AND   ss_customer_sk = c_customer_sk
           AND   ca_address_sk = c_current_addr_sk
           AND   ss_item_sk = i_item_sk
           AND   ca_gmt_offset = {GMT}
           AND   i_category = '{CATEGORY}'
           AND   s_gmt_offset = {GMT}
           AND   d_year = {YEAR}
           AND   d_moy  = {MONTH}) all_sales
        ORDER BY promotions, total
        LIMIT 100;
        """.format(
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA'),
            GMT='{GMT}',  # Replace with the actual value for GMT
            CATEGORY='{CATEGORY}',  # Replace with the actual value for CATEGORY
            YEAR='{YEAR}',  # Replace with the actual value for YEAR
            MONTH='{MONTH}'  # Replace with the actual value for MONTH
        ),
        "placeholders": {
            "CATEGORY": {
                "label": "Enter CATEGORY:",
                "type": "dropdown",
                "options": ["Sports", "Men", "Music", "Children", "Electronics", "Home", "Women", "Shoes", "Jewelry", "Books"]
            },
            "GMT": {
                "label": "Enter GMT:",
                "type": "dropdown",
                "options": [-5,-6,-7,-8]
            },
            "MONTH": {
                "label": "Enter MONTH:",
                "type": "dropdown",
                "options": [1,2,3,4,5,6,7,8,9,10,11,12]
            },
            "YEAR": {
                "label": "Select YEAR:",
                "type": "slider",
                "min": 1900,
                "max": 2049
            },
        },
        "description": "Find the ratio of items sold with and without promotions in a given month and year. Only items in certain categories sold to customers living in a specific time zone are considered.",
        "explanation": "Determines how many items in certain categories were sold at full price (without promotions) and how many were sold with discounts or special offers (with promotions) during a specific month and year, but only for customers in a specific time zone. The ratio provides insight into the effectiveness of promotions for those particular items and target customers. "
    },
 "Query2": {
        "sql": """
        SELECT  
           SUBSTR(w_warehouse_name, 1, 20)
          ,sm_type
          ,web_name
          ,SUM(CASE WHEN (ws_ship_date_sk - ws_sold_date_sk <= 30 ) THEN 1 ELSE 0 END) AS "30 days" 
          ,SUM(CASE WHEN (ws_ship_date_sk - ws_sold_date_sk > 30) AND 
                         (ws_ship_date_sk - ws_sold_date_sk <= 60) THEN 1 ELSE 0 END ) AS "31-60 days" 
          ,SUM(CASE WHEN (ws_ship_date_sk - ws_sold_date_sk > 60) AND 
                         (ws_ship_date_sk - ws_sold_date_sk <= 90) THEN 1 ELSE 0 END) AS "61-90 days" 
          ,SUM(CASE WHEN (ws_ship_date_sk - ws_sold_date_sk > 90) AND
                         (ws_ship_date_sk - ws_sold_date_sk <= 120) THEN 1 ELSE 0 END) AS "91-120 days" 
          ,SUM(CASE WHEN (ws_ship_date_sk - ws_sold_date_sk  > 120) THEN 1 ELSE 0 END) AS ">120 days" 
        FROM
           {database}.{schema}.web_sales
          ,{database}.{schema}.warehouse
          ,{database}.{schema}.ship_mode
          ,{database}.{schema}.web_site
          ,{database}.{schema}.date_dim
        WHERE
            d_month_seq BETWEEN {DMS} AND {DMS} + 11
        AND ws_ship_date_sk   = d_date_sk
        AND ws_warehouse_sk   = w_warehouse_sk
        AND ws_ship_mode_sk   = sm_ship_mode_sk
        AND ws_web_site_sk    = web_site_sk
        GROUP BY
           SUBSTR(w_warehouse_name, 1, 20)
          ,sm_type
          ,web_name
        ORDER BY SUBSTR(w_warehouse_name, 1, 20)
                ,sm_type
               ,web_name
        LIMIT 100;
        """.format(
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA'),
            DMS='{DMS}'  # Replace with the actual values for DMS or other placeholders as needed
        ),
        "placeholders": {
            "DMS": {
               "label": "Select DMS:",
                "type": "slider",
                "min": 0,
                "max": 2400
            }
        },
        "description": "For web sales, create a report showing the counts of orders shipped within 30 days, from 31 to 60 days, from 61 to 90 days, from 91 to 120 days and over 120 days within a given year, grouped by warehouse, shipping mode and web site.",
        "explanation": "Shows how quickly orders are shipped, based on different timeframes (like within a month or between one and two months) and where they are coming from (which warehouse, shipping method, and website). This will help you understand how efficient your shipping process is across different parts of your business."
    },
    "Query3": {
    "sql": """
    SELECT * 
    FROM (SELECT i_manager_id
                 ,SUM(ss_sales_price) AS sum_sales
                 ,AVG(SUM(ss_sales_price)) OVER (PARTITION BY i_manager_id) AS avg_monthly_sales
          FROM {database}.{schema}.item
              ,{database}.{schema}.store_sales
              ,{database}.{schema}.date_dim
              ,{database}.{schema}.store
          WHERE ss_item_sk = i_item_sk
            AND ss_sold_date_sk = d_date_sk
            AND ss_store_sk = s_store_sk
            AND d_month_seq IN ({DMS},{DMS}+1,{DMS}+2,{DMS}+3,{DMS}+4,{DMS}+5,{DMS}+6,{DMS}+7,{DMS}+8,{DMS}+9,{DMS}+10,{DMS}+11)
            AND ((    i_category IN ('Books','Children','Electronics')
                  AND i_class IN ('personal','portable','reference','self-help')
                  AND i_brand IN ('scholaramalgamalg #14','scholaramalgamalg #7',
                                  'exportiunivamalgamalg #9','scholaramalgamalg #9'))
               OR(    i_category IN ('Women','Music','Men')
                  AND i_class IN ('accessories','classical','fragrances','pants')
                  AND i_brand IN ('amalgimporto #1','edu packscholar #1','exportiimporto #1',
                                   'importoamalg #1')))
        GROUP BY i_manager_id, d_moy) tmp1
    WHERE CASE WHEN avg_monthly_sales > 0 THEN ABS (sum_sales - avg_monthly_sales) / avg_monthly_sales ELSE NULL END > 0.1
    ORDER BY i_manager_id
            ,avg_monthly_sales
            ,sum_sales
    LIMIT 100;
    """.format(
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
        DMS='{DMS}'  # Replace with the actual values for DMS or other placeholders as needed
    ),
    "placeholders": {
            "DMS": {
               "label": "Select DMS:",
                "type": "slider",
                "min": 0,
                "max": 2400
            }
    },
    "description": "For a given year, calculate the monthly sales of items of specific categories, classes, and brands that were sold in stores and group the results by store manager. Additionally, for every month and manager, print the yearly average sales of those items.",
    "explanation": "Determines how much money the store made each month in a particular year from specific types of products that were sold in your physical stores for each store manager. Also finds out the average sales of those items for each month and manager over the whole year. This will help you track sales performance and identify any trends or patterns."
},
