<?php
require_once('ripcord/ripcord.php');
$url = "http://127.0.0.1:8069";
$db = "reliance3";
$username = "admin";
$password = "admin789";
$common = ripcord::client("$url/xmlrpc/2/common");
$uid = $common->authenticate($db, $username, $password, array());
var_dump($uid);



//1. find partner id
$models = ripcord::client($url . '/xmlrpc/2/object');
$partner_id = $models->execute_kw($db, $uid, $password, 'res.partner', 'search',
	[[['refi_no_debitur','=','100100000044']]]
);
var_dump($partner_id);


//2. now create user
$user_id = $models->execute_kw($db, $uid, $password, 'res.users', 'create',
	[[
	"login"=>"anwar", 
	"password"=>"anwar123", 
	"partner_id"=>$partner_id[0], 
	]]
);
var_dump($user_id);

