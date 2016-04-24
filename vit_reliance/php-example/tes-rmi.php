<?php
require_once('ripcord/ripcord.php');
$url = "http://erp2.vitraining.com:8069";
$db = "reliance";
$username = "admin";
$password = "1";
$common = ripcord::client("$url/xmlrpc/2/common");
$uid = $common->authenticate($db, $username, $password, array());
var_dump($uid);

echo "get member by reliance_id";
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_rmi_customer';
$reliance_id = '20';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
      $reliance_id 
));
var_dump($res);


echo "get by sid";
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_rmi_customer_by_sid';
$sid= '1010084';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
      $sid
));
var_dump($res);


