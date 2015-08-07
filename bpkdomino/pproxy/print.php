<?php
header('Access-Control-Allow-Origin: *'); 
header('Access-Control-Allow-Methods: GET, PUT, POST, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept, Key');
header("Content-type: application/json");
$json = json_decode(file_get_contents("php://input"));
//var_dump($json->barcode);die;
require_once("printer.php");
$printername = 'Zebra2';

if(isset($json->barcode)){
	$printer = new RawPrinter($printername);
	$printer->send($json->barcode);
}