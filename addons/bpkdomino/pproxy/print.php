<?php
header('Access-Control-Allow-Origin: *'); 
header('Access-Control-Allow-Methods: GET, PUT, POST, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept, Key');
header("Content-type: application/json");
$json = json_decode(file_get_contents("php://input"));

require_once("printer.php");
$printername = 'EPSON L110 Series';

if(isset($json->barcode)){
	$printer = new RawPrinter($printername);
	$printer->send($json->barcode);
}