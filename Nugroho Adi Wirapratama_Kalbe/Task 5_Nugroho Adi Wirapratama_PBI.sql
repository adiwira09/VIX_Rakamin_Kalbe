-- rata-rata umur customer dilihat dari marital status
select "Marital Status", round(avg(age)) 
from public.customer
group by "Marital Status"

--rata-rata umur customer dilihat dari gender
select gender, round(avg(age)) 
from public.customer
group by gender

-- store dengan total quantity terbanyak
select store.storename as storename, sum(transaction.qty) as sum_qty
from public.transaction transaction
join public.store store
on store.storeid = transaction.storeid
group by store.storename
order by sum_qty desc
limit 1

-- nama produk terlaris dengan total amount terbanyak
select product.productid, max(product."Product Name") as product_name,
sum(transaction.totalamount) as total_amount
from public.transaction transaction
join public.product product
on product.productid = transaction.productid
group by product.productid
order by total_amount desc
limit 1