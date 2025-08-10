select "shopapp_product"."id",
       "shopapp_product"."name",
       "shopapp_product"."description",
       "shopapp_product"."price",
       "shopapp_product"."discount",
       "shopapp_product"."created_at",
       "shopapp_product"."archived",
       "shopapp_product"."preview"
from "shopapp_product"
where not "shopapp_product"."archived"
order by "shopapp_product"."name" asc, "shopapp_product"."price" asc;
args
=(); alias
=default

(0.001) select "shopapp_order"."id", "shopapp_order"."delivery_address", "shopapp_order"."promocode", "shopapp_order"."created_at", "shopapp_order"."user_id", "shopapp_order"."receipt", (cast(coalesce((cast(sum("shopapp_product"."price") as numeric)), (cast('0' as numeric))) as numeric)) as "total", count("shopapp_order_products"."product_id") as "products_count" from "shopapp_order" left outer join "shopapp_order_products" on ("shopapp_order"."id" = "shopapp_order_products"."order_id") left outer join "shopapp_product" on ("shopapp_order_products"."product_id" = "shopapp_product"."id") group by "shopapp_order"."id", "shopapp_order"."delivery_address", "shopapp_order"."promocode", "shopapp_order"."created_at", "shopapp_order"."user_id", "shopapp_order"."receipt"; args=(Decimal('0'),); alias=default
