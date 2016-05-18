delete from reliance_arg_partner_polis_risk;
delete from reliance_arg_partner_polis;     
delete from res_partner where comment like 'ARG%';
update reliance_import_arg SET  is_imported = false;
update reliance_import_arg_polis_risk SET  is_imported = false;
