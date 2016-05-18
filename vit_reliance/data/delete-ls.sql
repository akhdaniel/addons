delete from reliance_partner_cash;
delete from reliance_partner_stock;     
delete from res_partner where comment like 'LS%';
update reliance_import_ls SET  is_imported = false;
update reliance_import_ls_stock SET  is_imported = false;
update reliance_import_ls_cash SET  is_imported = false;
