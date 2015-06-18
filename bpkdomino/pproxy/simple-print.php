<?php
require_once("printer.php");
$printername = 'EPSON L110 Series';

$printer = new RawPrinter($printername);
$printer->send("asoy");