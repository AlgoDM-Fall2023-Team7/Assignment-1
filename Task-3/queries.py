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
"Query5": {
    "sql": """
    SELECT 
        s_store_name,
        i_item_desc,
        sc.revenue,
        i_current_price,
        i_wholesale_cost,
        i_brand
     FROM {database}.{schema}.store, {database}.{schema}.item,
         (SELECT ss_store_sk, AVG(revenue) AS ave
          FROM
              (SELECT ss_store_sk, ss_item_sk, 
                     SUM(ss_sales_price) AS revenue
               FROM {database}.{schema}.store_sales, {database}.{schema}.date_dim
               WHERE ss_sold_date_sk = d_date_sk AND d_month_seq BETWEEN {DMS} AND {DMS}+11
               GROUP BY ss_store_sk, ss_item_sk) sa
          GROUP BY ss_store_sk) sb,
         (SELECT ss_store_sk, ss_item_sk, SUM(ss_sales_price) AS revenue
          FROM {database}.{schema}.store_sales, {database}.{schema}.date_dim
          WHERE ss_sold_date_sk = d_date_sk AND d_month_seq BETWEEN {DMS} AND {DMS}+11
          GROUP BY ss_store_sk, ss_item_sk) sc
     WHERE sb.ss_store_sk = sc.ss_store_sk AND 
           sc.revenue <= 0.1 * sb.ave AND
           s_store_sk = sc.ss_store_sk AND
           i_item_sk = sc.ss_item_sk
     ORDER BY s_store_name, i_item_desc
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
            "min": 0,  # Define the minimum value for the slider
            "max": 2400,  # Define the maximum value for the slider
        }
    },
    "description": "In a given period, for each store, report the list of items with revenue less than 10% of the average revenue for all the items in that store.",
    "explanation": "In a given period, for each store, he or she is tasked with reporting the list of items that have generated revenue less than 10% of the average revenue for all the items in that particular store. This analysis helps identify products that may not be performing well in relation to the average sales of items within each store during that time frame."
},
"Query6": {
    "sql": """
    SELECT
        w_warehouse_name,
        w_warehouse_sq_ft,
        w_city,
        w_county,
        w_state,
        w_country,
        ship_carriers,
        year,
        SUM(jan_sales) AS jan_sales,
        SUM(feb_sales) AS feb_sales,
        SUM(mar_sales) AS mar_sales,
        SUM(apr_sales) AS apr_sales,
        SUM(may_sales) AS may_sales,
        SUM(jun_sales) AS jun_sales,
        SUM(jul_sales) AS jul_sales,
        SUM(aug_sales) AS aug_sales,
        SUM(sep_sales) AS sep_sales,
        SUM(oct_sales) AS oct_sales,
        SUM(nov_sales) AS nov_sales,
        SUM(dec_sales) AS dec_sales,
        SUM(jan_sales / w_warehouse_sq_ft) AS jan_sales_per_sq_foot,
        SUM(feb_sales / w_warehouse_sq_ft) AS feb_sales_per_sq_foot,
        SUM(mar_sales / w_warehouse_sq_ft) AS mar_sales_per_sq_foot,
        SUM(apr_sales / w_warehouse_sq_ft) AS apr_sales_per_sq_foot,
        SUM(may_sales / w_warehouse_sq_ft) AS may_sales_per_sq_foot,
        SUM(jun_sales / w_warehouse_sq_ft) AS jun_sales_per_sq_foot,
        SUM(jul_sales / w_warehouse_sq_ft) AS jul_sales_per_sq_foot,
        SUM(aug_sales / w_warehouse_sq_ft) AS aug_sales_per_sq_foot,
        SUM(sep_sales / w_warehouse_sq_ft) AS sep_sales_per_sq_foot,
        SUM(oct_sales / w_warehouse_sq_ft) AS oct_sales_per_sq_foot,
        SUM(nov_sales / w_warehouse_sq_ft) AS nov_sales_per_sq_foot,
        SUM(dec_sales / w_warehouse_sq_ft) AS dec_sales_per_sq_foot,
        SUM(jan_net) AS jan_net,
        SUM(feb_net) AS feb_net,
        SUM(mar_net) AS mar_net,
        SUM(apr_net) AS apr_net,
        SUM(may_net) AS may_net,
        SUM(jun_net) AS jun_net,
        SUM(jul_net) AS jul_net,
        SUM(aug_net) AS aug_net,
        SUM(sep_net) AS sep_net,
        SUM(oct_net) AS oct_net,
        SUM(nov_net) AS nov_net,
        SUM(dec_net) AS dec_net
    FROM (
        SELECT
            w_warehouse_name,
            w_warehouse_sq_ft,
            w_city,
            w_county,
            w_state,
            w_country,
            '{SMC_01}' || ',' || '{SMC_02}' AS ship_carriers,
            d_year AS year,
            SUM(CASE WHEN d_moy = 1 THEN ws_ext_sales_price * ws_quantity ELSE 0 END) AS jan_sales,
            SUM(CASE WHEN d_moy = 2 THEN ws_ext_sales_price * ws_quantity ELSE 0 END) AS feb_sales,
            SUM(CASE WHEN d_moy = 3 THEN ws_ext_sales_price * ws_quantity ELSE 0 END) AS mar_sales,
            SUM(CASE WHEN d_moy = 4 THEN ws_ext_sales_price * ws_quantity ELSE 0 END) AS apr_sales,
            SUM(CASE WHEN d_moy = 5 THEN ws_ext_sales_price * ws_quantity ELSE 0 END) AS may_sales,
            SUM(CASE WHEN d_moy = 6 THEN ws_ext_sales_price * ws_quantity ELSE 0 END) AS jun_sales,
            SUM(CASE WHEN d_moy = 7 THEN ws_ext_sales_price * ws_quantity ELSE 0 END) AS jul_sales,
            SUM(CASE WHEN d_moy = 8 THEN ws_ext_sales_price * ws_quantity ELSE 0 END) AS aug_sales,
            SUM(CASE WHEN d_moy = 9 THEN ws_ext_sales_price * ws_quantity ELSE 0 END) AS sep_sales,
            SUM(CASE WHEN d_moy = 10 THEN ws_ext_sales_price * ws_quantity ELSE 0 END) AS oct_sales,
            SUM(CASE WHEN d_moy = 11 THEN ws_ext_sales_price * ws_quantity ELSE 0 END) AS nov_sales,
            SUM(CASE WHEN d_moy = 12 THEN ws_ext_sales_price * ws_quantity ELSE 0 END) AS dec_sales,
            SUM(CASE WHEN d_moy = 1 THEN ws_net_paid * ws_quantity ELSE 0 END) AS jan_net,
            SUM(CASE WHEN d_moy = 2 THEN ws_net_paid * ws_quantity ELSE 0 END) AS feb_net,
            SUM(CASE WHEN d_moy = 3 THEN ws_net_paid * ws_quantity ELSE 0 END) AS mar_net,
            SUM(CASE WHEN d_moy = 4 THEN ws_net_paid * ws_quantity ELSE 0 END) AS apr_net,
            SUM(CASE WHEN d_moy = 5 THEN ws_net_paid * ws_quantity ELSE 0 END) AS may_net,
            SUM(CASE WHEN d_moy = 6 THEN ws_net_paid * ws_quantity ELSE 0 END) AS jun_net,
            SUM(CASE WHEN d_moy = 7 THEN ws_net_paid * ws_quantity ELSE 0 END) AS jul_net,
            SUM(CASE WHEN d_moy = 8 THEN ws_net_paid * ws_quantity ELSE 0 END) AS aug_net,
            SUM(CASE WHEN d_moy = 9 THEN ws_net_paid * ws_quantity ELSE 0 END) AS sep_net,
            SUM(CASE WHEN d_moy = 10 THEN ws_net_paid * ws_quantity ELSE 0 END) AS oct_net,
            SUM(CASE WHEN d_moy = 11 THEN ws_net_paid * ws_quantity ELSE 0 END) AS nov_net,
            SUM(CASE WHEN d_moy = 12 THEN ws_net_paid * ws_quantity ELSE 0 END) AS dec_net
        FROM
            {database}.{schema}.web_sales,
            {database}.{schema}.warehouse,
            {database}.{schema}.date_dim,
            {database}.{schema}.time_dim,
            {database}.{schema}.ship_mode
        WHERE
            ws_warehouse_sk = w_warehouse_sk
            AND ws_sold_date_sk = d_date_sk
            AND ws_sold_time_sk = t_time_sk
            AND ws_ship_mode_sk = sm_ship_mode_sk
            AND d_year = {YEAR_01}
            AND t_time BETWEEN {TIMEONE_01} AND {TIMEONE_01} + 28800
            AND sm_carrier IN ('{SMC_01}', '{SMC_02}')
        GROUP BY
            w_warehouse_name,
            w_warehouse_sq_ft,
            w_city,
            w_county,
            w_state,
            w_country,
            d_year
        UNION ALL
        SELECT
            w_warehouse_name,
            w_warehouse_sq_ft,
            w_city,
            w_county,
            w_state,
            w_country,
            '{SMC_01}' || ',' || '{SMC_02}' AS ship_carriers,
            d_year AS year,
            SUM(CASE WHEN d_moy = 1 THEN cs_sales_price * cs_quantity ELSE 0 END) AS jan_sales,
            SUM(CASE WHEN d_moy = 2 THEN cs_sales_price * cs_quantity ELSE 0 END) AS feb_sales,
            SUM(CASE WHEN d_moy = 3 THEN cs_sales_price * cs_quantity ELSE 0 END) AS mar_sales,
            SUM(CASE WHEN d_moy = 4 THEN cs_sales_price * cs_quantity ELSE 0 END) AS apr_sales,
            SUM(CASE WHEN d_moy = 5 THEN cs_sales_price * cs_quantity ELSE 0 END) AS may_sales,
            SUM(CASE WHEN d_moy = 6 THEN cs_sales_price * cs_quantity ELSE 0 END) AS jun_sales,
            SUM(CASE WHEN d_moy = 7 THEN cs_sales_price * cs_quantity ELSE 0 END) AS jul_sales,
            SUM(CASE WHEN d_moy = 8 THEN cs_sales_price * cs_quantity ELSE 0 END) AS aug_sales,
            SUM(CASE WHEN d_moy = 9 THEN cs_sales_price * cs_quantity ELSE 0 END) AS sep_sales,
            SUM(CASE WHEN d_moy = 10 THEN cs_sales_price * cs_quantity ELSE 0 END) AS oct_sales,
            SUM(CASE WHEN d_moy = 11 THEN cs_sales_price * cs_quantity ELSE 0 END) AS nov_sales,
            SUM(CASE WHEN d_moy = 12 THEN cs_sales_price * cs_quantity ELSE 0 END) AS dec_sales,
            SUM(CASE WHEN d_moy = 1 THEN cs_net_paid * cs_quantity ELSE 0 END) AS jan_net,
            SUM(CASE WHEN d_moy = 2 THEN cs_net_paid * cs_quantity ELSE 0 END) AS feb_net,
            SUM(CASE WHEN d_moy = 3 THEN cs_net_paid * cs_quantity ELSE 0 END) AS mar_net,
            SUM(CASE WHEN d_moy = 4 THEN cs_net_paid * cs_quantity ELSE 0 END) AS apr_net,
            SUM(CASE WHEN d_moy = 5 THEN cs_net_paid * cs_quantity ELSE 0 END) AS may_net,
            SUM(CASE WHEN d_moy = 6 THEN cs_net_paid * cs_quantity ELSE 0 END) AS jun_net,
            SUM(CASE WHEN d_moy = 7 THEN cs_net_paid * cs_quantity ELSE 0 END) AS jul_net,
            SUM(CASE WHEN d_moy = 8 THEN cs_net_paid * cs_quantity ELSE 0 END) AS aug_net,
            SUM(CASE WHEN d_moy = 9 THEN cs_net_paid * cs_quantity ELSE 0 END) AS sep_net,
            SUM(CASE WHEN d_moy = 10 THEN cs_net_paid * cs_quantity ELSE 0 END) AS oct_net,
            SUM(CASE WHEN d_moy = 11 THEN cs_net_paid * cs_quantity ELSE 0 END) AS nov_net,
            SUM(CASE WHEN d_moy = 12 THEN cs_net_paid * cs_quantity ELSE 0 END) AS dec_net
        FROM
            {database}.{schema}.catalog_sales,
            {database}.{schema}.warehouse,
            {database}.{schema}.date_dim,
            {database}.{schema}.time_dim,
            {database}.{schema}.ship_mode
        WHERE
            cs_warehouse_sk = w_warehouse_sk
            AND cs_sold_date_sk = d_date_sk
            AND cs_sold_time_sk = t_time_sk
            AND cs_ship_mode_sk = sm_ship_mode_sk
            AND d_year = {YEAR_01}
            AND t_time BETWEEN {TIMEONE_01} AND {TIMEONE_01} + 28800
            AND sm_carrier IN ('{SMC_01}', '{SMC_02}')
        GROUP BY
            w_warehouse_name,
            w_warehouse_sq_ft,
            w_city,
            w_county,
            w_state,
            w_country,
            d_year
    ) x
    GROUP BY
        w_warehouse_name,
        w_warehouse_sq_ft,
        w_city,
        w_county,
        w_state,
        w_country,
        ship_carriers,
        year
    ORDER BY w_warehouse_name
    LIMIT 100;
    """.format(
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
        SALESTWO_01 = '{SALESTWO_01}',
        SALESONE_01 = '{SALESONE_01}',
        NETTWO_01 = '{NETTWO_01}',
        NETONE_01 = '{NETONE_01}',
        YEAR_01='{YEAR_01}',  # Replace with the actual value
        TIMEONE_01='{TIMEONE_01}',  # Replace with the actual value
        SMC_01='{SMC_01}',  # Replace with the actual value
        SMC_02='{SMC_02}',  # Replace with the actual value
    ),
    "placeholders": {
            "SALESTWO_01": {
                "label": "Select SALESTWO_01",  
                "type": "dropdown",
                "options": ["cs_sales_price"]
            },  
            "SALESONE_01": {
                "label": "Select SALESTWO_01",  
                "type": "dropdown",
                "options": ["ws_ext_sales_price"]
            }, 
            "NETTWO_01": {
                "label": "Select NETTWO_01",  
                "type": "dropdown",
                "options": ["cs_net_paid_inc_tax"]
            },      
            "NETONE_01": {
                "label": "Select NETONE_01",  
                "type": "dropdown",
                "options": ["ws_net_paid"]
            },           
            "SMC_01": {
                "label": "Enter SMC_01:",
                "type": "dropdown",
                "options": ["UPS", "FEDEX", "USPS", "TBS", "ZHOU", "ZOUDOS", "MSC", "LATVIAN", "BOXBUNDLES", "GREAT EASTERN", "DIAMOND", "RUPEKSA", "HARMSTORF", "PRIVATECARRIER", "ORIENTAL", "GERMA", "AIRBORNE", "DHL", "BARIAN", "ALLIANCE"]
            },
            "SMC_02": {
                "label": "Enter SMC_02:",
                "type": "dropdown",
                "options": ["UPS", "FEDEX", "USPS", "TBS", "ZHOU", "ZOUDOS", "MSC", "LATVIAN", "BOXBUNDLES", "GREAT EASTERN", "DIAMOND", "RUPEKSA", "HARMSTORF", "PRIVATECARRIER", "ORIENTAL", "GERMA", "AIRBORNE", "DHL", "BARIAN", "ALLIANCE"]
            },           
            "YEAR": {
                "label": "Select YEAR:",
                "type": "slider",
                "min": 1900,
                "max": 2049
            },
            "TIMEONE_01": {
                "label": "Select TIMEONE_01:",
                "type": "slider",
                "min": 0,
                "max": 86399,
            },
    },
    "description": "Compute web and catalog sales and profits by warehouse. Report results by month for a given year during a given 8-hour period.",
    "explanation": "Calculates the sales and profits generated through two different channels: web and catalog sales for each warehouse location on a monthly basis, specifically for a particular year. However, there's an additional requirement that focuses on an 8-hour period within each day. This analysis is helpful for understanding the sales and profitability trends for different sales channels and warehouses over the course of a year, with a particular emphasis on a specific time frame during each day."
},
"Query7": {
    "sql": """
    SELECT *
    FROM (
        SELECT
            i_category,
            i_class,
            i_brand,
            i_product_name,
            d_year,
            d_qoy,
            d_moy,
            s_store_id,
            sumsales,
            RANK() OVER (PARTITION BY i_category ORDER BY sumsales DESC) rk
        FROM (
            SELECT
                i_category,
                i_class,
                i_brand,
                i_product_name,
                d_year,
                d_qoy,
                d_moy,
                s_store_id,
                SUM(COALESCE(ss_sales_price * ss_quantity, 0)) sumsales
            FROM
                {database}.{schema}.store_sales,
                {database}.{schema}.date_dim,
                {database}.{schema}.store,
                {database}.{schema}.item
            WHERE
                ss_sold_date_sk = d_date_sk
                AND ss_item_sk = i_item_sk
                AND ss_store_sk = s_store_sk
                AND d_month_seq BETWEEN {DMS} AND {DMS} + 11
            GROUP BY
                ROLLUP(i_category, i_class, i_brand, i_product_name, d_year, d_qoy, d_moy, s_store_id)
        ) dw1
    ) dw2
    WHERE rk <= 100
    ORDER BY
        i_category,
        i_class,
        i_brand,
        i_product_name,
        d_year,
        d_qoy,
        d_moy,
        s_store_id,
        sumsales,
        rk
    LIMIT 100;
    """.format(
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
        DMS='{DMS}'  # Replace with the actual value
    ),
    "placeholders": {
        "DMS": {
            "label": "Select DMS:",
            "type": "slider",
            "min": 0,  # Define the minimum value for the slider
            "max": 2400,  # Define the maximum value for the slider
        }
    },
    "description": "Find top stores for each category based on store sales in a specific year. ",
    "explanation": "Identifies the top-performing stores within each product category by looking at their sales for a particular year. It helps identify which stores excelled in selling products in different categories during that specific time period."
},
"Query8": {
    "sql": """
    SELECT
        c_last_name,
        c_first_name,
        ca_city,
        bought_city,
        ss_ticket_number,
        extended_price,
        extended_tax,
        list_price
    FROM (
        SELECT
            ss_ticket_number,
            ss_customer_sk,
            ca_city AS bought_city,
            SUM(ss_ext_sales_price) AS extended_price,
            SUM(ss_ext_list_price) AS list_price,
            SUM(ss_ext_tax) AS extended_tax
        FROM
            {database}.{schema}.store_sales,
            {database}.{schema}.date_dim,
            {database}.{schema}.store,
            {database}.{schema}.household_demographics,
            {database}.{schema}.customer_address
        WHERE
            store_sales.ss_sold_date_sk = date_dim.d_date_sk
            AND store_sales.ss_store_sk = store.s_store_sk
            AND store_sales.ss_hdemo_sk = household_demographics.hd_demo_sk
            AND store_sales.ss_addr_sk = customer_address.ca_address_sk
            AND date_dim.d_dom BETWEEN 1 AND 2
            AND (household_demographics.hd_dep_count = {DEPCNT_01} OR household_demographics.hd_vehicle_count = {VEHCNT_01})
            AND date_dim.d_year IN ({YEAR_01}, {YEAR_01} + 1, {YEAR_01} + 2)
            AND store.s_city IN ('{CITY_B_01}', '{CITY_A_01}')
        GROUP BY
            ss_ticket_number,
            ss_customer_sk,
            ss_addr_sk,
            ca_city
    ) dn,
    {database}.{schema}.customer,
    {database}.{schema}.customer_address current_addr
    WHERE
        ss_customer_sk = c_customer_sk
        AND customer.c_current_addr_sk = current_addr.ca_address_sk
        AND current_addr.ca_city <> bought_city
    ORDER BY
        c_last_name,
        ss_ticket_number
    LIMIT 100;
    """.format(
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
        DEPCNT_01='{DEPCNT_01}',  # Replace with the actual value
        VEHCNT_01='{VEHCNT_01}',  # Replace with the actual value
        YEAR_01='{YEAR_01}',      # Replace with the actual value
        CITY_B_01='{CITY_B_01}',  # Replace with the actual value
        CITY_A_01='{CITY_A_01}'   # Replace with the actual value
    ),
    "placeholders": {
        "DEPCNT_01": {
            "label": "Dependent Count:",
                "type": "dropdown",
                "options": [0,1,2,3,4,5,6,7,8,9]
        },
        "VEHCNT_01": {
            "label": "Vehicle Count:",
                "type": "dropdown",
                "options": [-1,0,1,2,3,4,]        },
        "YEAR_01": {
            "label": "Year:",
            "type": "slider",
            "min": 1900,  # Define the minimum value for the slider
            "max": 2049,  # Define the maximum value for the slider
        },
        "CITY_B_01": {
            "label": "City B:",
            "type": "dropdown",
            "options":["Cherry Hill", "Shannon", "Foster", "Fernwood", "Roosevelt", "Crossroads", "Plainview", "Hopewell", "Elba", "Wright", "Tracy", "Fowler", "Edgewater", "Bryant", "Klondike", "Cedar Creek", "Arnold", "Morton", "Weston", "Brookfield", "Berlin", "Newark", "West Liberty", "Sherwood Forest", "Stanley", "Adams", "Jerusalem", "Porter", "Belmont", "Clifford", "Peru", "Sheffield", "Howard", "Goshen", "Webster", "Thomas", "Cherry Grove", "Milltown", "Twin Lakes", "Beech Grove", "Flat Rock", "Scott", "Louisville", "Norton", "Benson", "Summit", "Woodlawn", "Plainville", "Andover", "Amherst", "Lyons", "Four Points", "Price", "Crystal Springs", "Bay View", "Roy", "Cumberland", "Glenville", "Rolling Hills", "Mount Airy", "Chesterfield", "Fredonia", "Alton", "Knollwood", "Victor", "Jefferson", "Wakefield", "Fairfield", "Quincy", "Martinsville", "Whitney", "Cooper", "Mount Tabor", "Armstrong", "Utica", "Roseville", "Paradise", "Springville", "Sand Hill", "Rock Creek", "Mill Creek", "Parker", "Fletcher", "Morgantown", "Florence", "Providence", "Empire", "Gum Springs", "Saint George", "Westminster", "Derby", "Enon", "Boyd", "Houston", "Plymouth", "Five Corners", "Needmore", "Clyde", "Princeton", "Hickory Hill"]
        },
        "CITY_A_01": {
            "label": "City A:",
            "type": "dropdown",
            "options":["Cherry Hill", "Shannon", "Foster", "Fernwood", "Roosevelt", "Crossroads", "Plainview", "Hopewell", "Elba", "Wright", "Tracy", "Fowler", "Edgewater", "Bryant", "Klondike", "Cedar Creek", "Arnold", "Morton", "Weston", "Brookfield", "Berlin", "Newark", "West Liberty", "Sherwood Forest", "Stanley", "Adams", "Jerusalem", "Porter", "Belmont", "Clifford", "Peru", "Sheffield", "Howard", "Goshen", "Webster", "Thomas", "Cherry Grove", "Milltown", "Twin Lakes", "Beech Grove", "Flat Rock", "Scott", "Louisville", "Norton", "Benson", "Summit", "Woodlawn", "Plainville", "Andover", "Amherst", "Lyons", "Four Points", "Price", "Crystal Springs", "Bay View", "Roy", "Cumberland", "Glenville", "Rolling Hills", "Mount Airy", "Chesterfield", "Fredonia", "Alton", "Knollwood", "Victor", "Jefferson", "Wakefield", "Fairfield", "Quincy", "Martinsville", "Whitney", "Cooper", "Mount Tabor", "Armstrong", "Utica", "Roseville", "Paradise", "Springville", "Sand Hill", "Rock Creek", "Mill Creek", "Parker", "Fletcher", "Morgantown", "Florence", "Providence", "Empire", "Gum Springs", "Saint George", "Westminster", "Derby", "Enon", "Boyd", "Houston", "Plymouth", "Five Corners", "Needmore", "Clyde", "Princeton", "Hickory Hill"]
        }
    },
    "description": "Compute the per customer extended sales price, extended list price, and extended tax for out-of-town shoppers buying from stores located in two cities in the first two days of each month of three consecutive years. Only consider customers with specific dependent and vehicle counts.",
    "explanation": "Calculates the total sales price, list price, and tax for customers who meet specific requirements. These calculations are made for customers who are shopping in two specific cities during the first two days of each month for three consecutive years. The focus is on customers with particular numbers of dependents and vehicles. This analysis can provide insights into the spending patterns of a specific group of customers in these two cities during this specific time frame."
},
"Query9": {
    "sql": """
    SELECT
        cd_gender,
        cd_marital_status,
        cd_education_status,
        COUNT(*) AS cnt1,
        cd_purchase_estimate,
        COUNT(*) AS cnt2,
        cd_credit_rating,
        COUNT(*) AS cnt3
    FROM
        {database}.{schema}.customer c,
        {database}.{schema}.customer_address ca,
        {database}.{schema}.customer_demographics
    WHERE
        c.c_current_addr_sk = ca.ca_address_sk
        AND ca.ca_state IN ('{STATE_01}', '{STATE_02}', '{STATE_03}')
        AND cd_demo_sk = c.c_current_cdemo_sk
        AND EXISTS (
            SELECT *
            FROM
                {database}.{schema}.store_sales,
                {database}.{schema}.date_dim
            WHERE
                c.c_customer_sk = ss_customer_sk
                AND ss_sold_date_sk = d_date_sk
                AND d_year = {YEAR_01}
                AND d_moy BETWEEN {MONTH} AND {MONTH}+2
        )
        AND (
            NOT EXISTS (
                SELECT *
                FROM
                    {database}.{schema}.web_sales,
                    {database}.{schema}.date_dim
                WHERE
                    c.c_customer_sk = ws_bill_customer_sk
                    AND ws_sold_date_sk = d_date_sk
                    AND d_year = {YEAR_01}
                    AND d_moy BETWEEN {MONTH} AND {MONTH}+2
            )
            AND NOT EXISTS (
                SELECT *
                FROM
                    {database}.{schema}.catalog_sales,
                    {database}.{schema}.date_dim
                WHERE
                    c.c_customer_sk = cs_ship_customer_sk
                    AND cs_sold_date_sk = d_date_sk
                    AND d_year = {YEAR_01}
                    AND d_moy BETWEEN {MONTH} AND {MONTH}+2
            )
        )
    GROUP BY
        cd_gender,
        cd_marital_status,
        cd_education_status,
        cd_purchase_estimate,
        cd_credit_rating
    ORDER BY
        cd_gender,
        cd_marital_status,
        cd_education_status,
        cd_purchase_estimate,
        cd_credit_rating
    LIMIT 100;
    """.format(
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
        STATE_01='{STATE_01}',       # Replace with the actual value
        STATE_02='{STATE_02}',       # Replace with the actual value
        STATE_03='{STATE_03}',       # Replace with the actual value
        YEAR_01='{YEAR_01}',         # Replace with the actual value
        MONTH='{MONTH}',             # Replace with the actual value
    ),
    "placeholders": {
        "STATE_01": {
            "label": "State 01:",
            "type": "dropdown",
            "options": ["WI", "MO", "NE", "CO", "OK", "SD", "WV", "ID", "NY", "AR", "NC", "IA", "DC", "TX", "AL", "WY", "RI", "IL", "OH", "MT", "LA", "MD", "GA", "CA", "FL", "AZ", "ND", "HI", "WA", "KY", "DE", "NM", "MA", "CT", "VA", "IN", "AK", "ME", "NV", "UT", "SC", "OR", "MN", "VT", "MS", "NH", "NJ", "TN", "MI", "PA", "KS"]  # Change the input type to "text" if you prefer a text input
        },
        "STATE_02": {
            "label": "State 02:",
             "type": "dropdown",
            "options": ["WI", "MO", "NE", "CO", "OK", "SD", "WV", "ID", "NY", "AR", "NC", "IA", "DC", "TX", "AL", "WY", "RI", "IL", "OH", "MT", "LA", "MD", "GA", "CA", "FL", "AZ", "ND", "HI", "WA", "KY", "DE", "NM", "MA", "CT", "VA", "IN", "AK", "ME", "NV", "UT", "SC", "OR", "MN", "VT", "MS", "NH", "NJ", "TN", "MI", "PA", "KS"]  # Change the input type to "text" if you prefer a text input
        },
        "STATE_03": {
            "label": "State 03:",
             "type": "dropdown",
            "options": ["WI", "MO", "NE", "CO", "OK", "SD", "WV", "ID", "NY", "AR", "NC", "IA", "DC", "TX", "AL", "WY", "RI", "IL", "OH", "MT", "LA", "MD", "GA", "CA", "FL", "AZ", "ND", "HI", "WA", "KY", "DE", "NM", "MA", "CT", "VA", "IN", "AK", "ME", "NV", "UT", "SC", "OR", "MN", "VT", "MS", "NH", "NJ", "TN", "MI", "PA", "KS"]  # Change the input type to "text" if you prefer a text input
        },
        "YEAR_01": {
           "label": "Year_01:",
            "type": "slider",
            "min": 1900,  # Define the minimum value for the slider
            "max": 2049,  # Define the maximum value for the slider
        },
        "MONTH": {
            "label": "Month:",
            "type": "dropdown",
            "options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]  # Add appropriate options for the dropdown
        }
    },
    "description": "Count the customers with the same gender, marital status, education status, purchase estimate, and credit rating who live in certain states and who have purchased from stores but neither form the catalog nor from the web during a two-month time period of a given year.",
    "explanation": "Count the number of customers who share specific characteristics such as gender, marital status, education, purchase behavior, and credit rating. These customers live in certain states, have shopped in physical stores, but have not made purchases from catalogs or online during a two-month period in a particular year. This analysis can help identify a specific group of customers with these characteristics within the given time frame."
},
"Query10": {
    "sql": """
    SELECT
        SUM(ss_net_profit) AS total_sum,
        s_state,
        s_county,
        grouping(s_state) + grouping(s_county) AS lochierarchy,
        RANK() OVER (
            PARTITION BY grouping(s_state) + grouping(s_county),
            CASE WHEN grouping(s_county) = 0 THEN s_state END
            ORDER BY SUM(ss_net_profit) DESC
        ) AS rank_within_parent
    FROM
        {database}.{schema}.store_sales,
        {database}.{schema}.date_dim d1,
        {database}.{schema}.store
    WHERE
        d1.d_month_seq BETWEEN {DMS} AND {DMS} + 11
        AND d1.d_date_sk = ss_sold_date_sk
        AND s_store_sk = ss_store_sk
        AND s_state IN (
            SELECT s_state
            FROM (
                SELECT
                    s_state AS s_state,
                    RANK() OVER (PARTITION BY s_state ORDER BY SUM(ss_net_profit) DESC) AS ranking
                FROM
                    {database}.{schema}.store_sales,
                    {database}.{schema}.store,
                    {database}.{schema}.date_dim
                WHERE
                    d_month_seq BETWEEN {DMS} AND {DMS} + 11
                    AND d_date_sk = ss_sold_date_sk
                    AND s_store_sk = ss_store_sk
                GROUP BY s_state
            ) tmp1
            WHERE ranking <= 5
        )
    GROUP BY ROLLUP(s_state, s_county)
    ORDER BY
        lochierarchy DESC,
        CASE WHEN lochierarchy = 0 THEN s_state END,
        rank_within_parent
    LIMIT 100;
    """.format(
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
        DMS='{DMS}'  # Replace with the actual value
    ),
    "placeholders": {
            "DMS": {
               "label": "Select DMS:",
                "type": "slider",
                "min": 0,
                "max": 2400
            }
        },
    "description": "Compute store sales net profit ranking by state and county for a given year and determine the five most profitable states.",
    "explanation": "Figures out how much profit each store made after expenses in different states and counties for a specific year. Then, it aims to find and list the top five states with the highest net profits. This analysis helps identify the most financially successful areas for the given time period."
},


}
