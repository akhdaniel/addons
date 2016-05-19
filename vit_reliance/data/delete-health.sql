delete from reliance_partner_health_limit;
delete from res_partner where comment like 'HEALTH%';
update reliance_import_health_polis SET  is_imported = false;
update reliance_import_health_peserta SET  is_imported = false;
update reliance_import_health_limit SET is_imported = false;
