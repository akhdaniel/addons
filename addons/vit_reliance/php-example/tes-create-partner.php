<?php
require_once('ripcord/ripcord.php');
$url = "http://127.0.0.1:8069";
$db = "reliance";
$username = "relianceku";
$password = "reliance2016";
$common = ripcord::client("$url/xmlrpc/2/common");
$uid = $common->authenticate($db, $username, $password, array());
var_dump($uid);


$models = ripcord::client($url . '/xmlrpc/2/object');

//now create partner 
$user_id = $models->execute_kw($db, $uid, $password, 'res.partner', 'create',
	[[
	"name"=>"anwar123", 
	"email"=>"anwar123", 
	]]
);
var_dump($user_id);

