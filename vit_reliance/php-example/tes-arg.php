<?php
require_once('ripcord/ripcord.php');
$url = "http://erp2.vitraining.com:8069";
$db = "reliance";
$username = "admin";
$password = "1";
$common = ripcord::client("$url/xmlrpc/2/common");
$uid = $common->authenticate($db, $username, $password, array());
var_dump($uid);

echo "get_arg_customer\n\n";
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_arg_customer';
$reliance_id = "REL40";
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
	$reliance_id
));
var_dump($res);



echo "get_arg_customer_by_cust_code\n\n";
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_arg_customer_by_cust_code';
$cust_code = 'C0035240';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
	$cust_code
));
var_dump($res);

echo "get_arg_customer_all_polis\n\n";
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_arg_customer_all_polis';
$reliance_id = "REL40";
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
	$reliance_id
));
var_dump($res);

echo "get_arg_customer_by_polis_number\n\n";
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_arg_customer_by_polis_number';
$policy_no= "JK-R02-00-2012-08-00001663-000";
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
	$policy_no
));
var_dump($res);


echo "get_arg_polis\n\n";
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_arg_polis';
$policy_no= "JK-R02-00-2012-08-00001663-000";
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
	$policy_no
));
var_dump($res);
