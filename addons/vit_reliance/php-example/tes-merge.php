<?php
require_once('ripcord/ripcord.php');
$url = "http://erp2.vitraining.com:8069";
$db = "reliance";
$username = "admin";
$password = "1";
$common = ripcord::client("$url/xmlrpc/2/common");
$uid = $common->authenticate($db, $username, $password, array());
var_dump($uid);

$models = ripcord::client($url . '/xmlrpc/2/object');
$method = '_merge';
$partner_ids = [552,551];
$dest_partner_id=551;
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , [
	$partner_ids,
	$dest_partner_id
]);
var_dump($res);
