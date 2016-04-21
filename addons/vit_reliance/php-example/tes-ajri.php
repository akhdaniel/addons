<?php
require_once('ripcord/ripcord.php');
$url = "http://erp2.vitraining.com:8069";
$db = "reliance";
$username = "admin";
$password = "1";
$common = ripcord::client("$url/xmlrpc/2/common");
$uid = $common->authenticate($db, $username, $password, array());
var_dump($uid);
/*
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_ajri_product';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
        '13060001147-75'
));
var_dump($res);
*/

$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_ajri_pemegang';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
        '13060001147-75'
));
var_dump($res);
/*
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_ajri_participant';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
        '1021306000002'
));
var_dump($res);
*/
