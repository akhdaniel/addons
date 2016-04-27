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
$res = $models->execute_kw( $db, $uid, $password, 'res.partner', 'search_read',
[[
    '|',
    [
	'&',
        ['health_member_id','=','000525-1'],
        ['health_nomor_polis','=','00415121100043403'],
    ],
    [
	'&',
        ['ajri_nomor_partisipan','=','000525-1'],
        ['ajri_nomor_polis','=','00415121100043403']
    ]
]]);
var_dump($res);
