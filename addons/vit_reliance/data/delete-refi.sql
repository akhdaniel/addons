delete from reliance_refi_kontrak;
delete from res_partner where comment like 'REFI%';
update reliance_import_refi_partner SET  is_imported = false;
update reliance_import_refi_pekerjaan SET is_imported = false;
update reliance_import_refi_keluarga SET  is_imported = false;
update reliance_import_refi_statement SET  is_imported = false;
update reliance_import_refi_kontrak SET  is_imported = false;

delete from reliance_import_refi_partner;
delete from reliance_import_refi_pekerjaan;
delete from reliance_import_refi_keluarga;
delete from reliance_import_refi_statement;
delete from reliance_import_refi_kontrak;
