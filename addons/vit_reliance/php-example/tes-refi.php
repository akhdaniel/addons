<?php
require_once('ripcord/ripcord.php');
$url = "http://erp2.vitraining.com:8069";
$db = "reliance";
$username = "admin";
$password = "1";
$common = ripcord::client("$url/xmlrpc/2/common");
$uid = $common->authenticate($db, $username, $password, array());
var_dump($uid);

echo "get kontrak by reliance_id";
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_refi_kontrak';
$reliance_id = '20';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
      $reliance_id 
));
var_dump($res);


echo "get by no_debitur";
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_refi_kontrak_by_no_debitur';
$no_debitur= '100100000001';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
      $no_debitur
));
var_dump($res);

echo "get_refi_customer_by_no_kontrak";
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_refi_customer_by_no_kontrak';
$no_kontrak= '100101120001';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
      $no_kontrak
));
var_dump($res);
