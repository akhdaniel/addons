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
$method = 'get_ajri_participant';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
        '1021307000007'
));
var_dump($res);



$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_ajri_pemegang';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
        '000000093'
));
var_dump($res);

