<?php
require_once('ripcord/ripcord.php');
$url = "http://relianceku.com:8069";
$db = "reliance3";
$username = "admin";
$password = "admin789";
$common = ripcord::client("$url/xmlrpc/2/common");
$uid = $common->authenticate($db, $username, $password, array());
var_dump($uid);

$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_ls_stock2';
$sid='SCD240480353254';
$cid='SYA158';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method ,
[$sid]
);
var_dump($res);
