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
$method = 'in_campaign';
$reliance_id = '100';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
        $reliance_id
));
var_dump($res);




