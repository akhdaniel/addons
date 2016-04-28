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
$method = 'get_health_all_member';
$nomor_polis = '00158151100113700';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
	$nomor_polis
));
var_dump($res);

$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_health_member';
$reliance_id= '011';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
        $reliance_id
));
var_dump($res);
*/

/*
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_health_member_by_member_id';
$member_id= '000092-1';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
        $member_id
));
var_dump($res);
$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_health_holder';
$reliance_id= '011';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
        $reliance_id
));
var_dump($res);
*/

$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_health_limit';
$reliance_id= '119';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
        $reliance_id
));
var_dump($res);

$models = ripcord::client($url . '/xmlrpc/2/object');
$method = 'get_health_limit_by_member_id';
$member_id= '000284-1';
$polis_no= '00014131100070802';
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', $method , array(
        $polis_no,$member_id 
));
var_dump($res);
