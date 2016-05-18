delete from res_partner where comment like 'RMI%';
update reliance_import_rmi SET  is_imported = false;
update reliance_import_rmi_product_holding SET  is_imported = false;
