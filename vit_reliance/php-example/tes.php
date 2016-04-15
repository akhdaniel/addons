<?php
require_once('ripcord/ripcord.php');
$info = ripcord::client('http://erp2.vitraining.com')->start();
var_dump($info);

