<?php 
define('ESC' , chr(27));
define('LF'  , chr(0x0a));
define('NUL' , chr(0x00));

class RawPrinter {
	var $printername ;

	function __construct($printername = 'Zebra2' ) {
	   $this->printername = $printername;
	}

	public function openPrinter(){
		$handle = printer_open($this->printername); 
		printer_set_option($handle, PRINTER_MODE, 'text');		
		//printer_set_option($handle, PRINTER_COPIES, 2);		
		//printer_set_option($handle, PRINTER_PAPER_FORMAT, PRINTER_FORMAT_A4);		
		//printer_set_option($handle, PRINTER_TEXT_COLOR, "005533");		
		//printer_set_option($handle, PRINTER_TEXT_ALIGN, PRINTER_TA_BASELINE);		
		return $handle;
	}
	
	public function writePrinter($handle, $data){
		$ret = printer_write($handle, $data);
		return $ret;
	}
	

	public function closePrinter($handle){
		printer_close($handle);	
	}

	public function send($data, $shopname='', $company_name =''){
		$handle = $this->openPrinter();
		$ret = $this->writePrinter($handle, $data);		
		$this->closePrinter($handle);
		return $ret;
	}
}