<?php
require_once('ripcord/ripcord.php');
$url = "http://relianceku.com:8069";
$db = "reliance3";
$username = "relianceku";
//$username = "admin";
$password = "reliance2016";
//$password = "admin789";
$common = ripcord::client("$url/xmlrpc/2/common");
$uid = $common->authenticate($db, $username, $password, array());
var_dump($uid);

$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'search_read';
$res = $models->execute_kw( $db, $uid, $password, 'ir.filters', $method , 
[[
	['name', '!=', 'imported'],
	['is_default', '=', false],
	['model_id', '=', 'res.partner']
]]
);
var_dump($res);


