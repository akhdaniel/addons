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
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', 'get_ls_stock', array(
    array(
        '000088888'
    )
));
var_dump($res);
