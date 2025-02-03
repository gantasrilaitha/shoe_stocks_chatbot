few_shots = [
    {'Question' : "How many shoes do we have left for Nike in extra small size and white color?",
     'SQLQuery' : "SELECT stock_quantity FROM shoes WHERE brand = 'Nike' AND color = 'White' AND size = '36'",
     'SQLResult': "Result of the SQL query",
     'Answer' : "86"},
    {'Question': "How many white color CampusX shoes do I have?",
         'SQLQuery' : "SELECT sum(stock_quantity) FROM shoes WHERE brand = 'CampusX' AND color = 'White' ;",
         'SQLResult': "Result of the SQL query",
         'Answer' : "208"
         },
    {'Question': "If we have to sell all the CampusX shoes today with discounts applied. How much revenue  our store will generate (post discounts)?" ,
         'SQLQuery' : """
                      SELECT sum(a.total_amount * ((100-COALESCE(shoe_discounts.pct_discount,0))/100)) as total_revenue from
    (select sum(price*stock_quantity) as total_amount, shoe_id from shoes where brand = 'CampusX'
    group by shoe_id) a left join shoe_discounts on a.shoe_id = shoe_discounts.shoe_id ;
""",
         'SQLResult': "Result of the SQL query",
         'Answer': "24106.800000"} ,
    {'Question' : "If we have to sell all the Bata shoes today. How much revenue our store will generate without discount?" ,
          'SQLQuery': "SELECT SUM(price * stock_quantity) FROM shoes WHERE brand = 'Bata'",
          'SQLResult': "Result of the SQL query",
          'Answer' : "27661"},
    {'Question': "How much is the total price of the inventory for all 40-size shoes?",
         'SQLQuery':"SELECT SUM(price*stock_quantity) FROM shoes WHERE size = '40'",
         'SQLResult': "Result of the SQL query",
         'Answer': "18700"}

]


