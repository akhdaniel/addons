<?php
require_once('ripcord/ripcord.php');
$url = "http://127.0.0.1:8069";
$db = "reliance3";
$username = "admin";
$password = "admin789";
$common = ripcord::client("$url/xmlrpc/2/common");
$uid = $common->authenticate($db, $username, $password, array());
var_dump($uid);

$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_ls_stock2';
//$method = 'get_ls_cash2';
$sid='SCD240480353254';
$cid='SYR011';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method ,
[$sid, $cid]
);
var_dump($res);
