<?php
require_once('ripcord/ripcord.php');
$url = "http://127.0.0.1:8069";
$db = "reliance";
$username = "admin";
$password = "1";
$common = ripcord::client("$url/xmlrpc/2/common");
$uid = $common->authenticate($db, $username, $password, array());
var_dump($uid);

$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'merge';
$partner_id1 = 551;
$partner_id2 = 552;
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
        $partner_id1, $partner_id2
));
var_dump($res);




