update product_template pp set 	parent_id=(select id from product_template where name=substr(pp.name,1,position(',' in pp.name )-1) limit 1) where  position(',' in pp.name )>0
