update product_category pc set mrp_location_id = (select id from stock_location where complete_name like '%GBA / Stock') where pc.name in ('Bahan Awal Aktif', 'Bahan Awal Pembantu');
update product_category pc set mrp_location_id = (select id from stock_location where complete_name like '%GBK / Stock') where pc.name in ('Bahan Pengemas');
update product_category set wo_start_no_stock = 'f' where name in ('Bahan Awal Aktif', 'Bahan Awal Pembantu');
update product_category set wo_start_no_stock = 't' where name in ('Bahan Pengemas');
