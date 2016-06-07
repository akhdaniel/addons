delete from res_partner where initial_bu='RMI';
update reliance_import_rmi SET  is_imported = false;
update reliance_import_rmi_product_holding SET  is_imported = false;
-- delete from reliance_import_rmi
-- delete frmo reliance_import_rmi_product_holding

