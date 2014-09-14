<?php
include("xmlrpc.inc");

class MyOpenERPLib 
{
	public $user      = "admin";
	public $password  = "1";
	public $dbname    = "devel";
	public $server_url= "http://127.0.0.1:8069/xmlrpc/";
	public $id        = null;

	function login(){
		$conn      = new xmlrpc_client($this->server_url . 'common');
		$msg       = new xmlrpcmsg('login');
		$msg->addParam( new xmlrpcval($this->dbname,   "string") );
		$msg->addParam( new xmlrpcval($this->user,     "string") );
		$msg->addParam( new xmlrpcval($this->password, "string") );
		$resp      = $conn->send( $msg );
		$val       = $resp->value();
		$this->id        = $val->scalarval();
		return $this->id>0 ? $this->id  : -1 ;
	}


	function search($relation, $key){
		$key_array = array(
			new xmlrpcval(
				array(
					new xmlrpcval("name","string"),
					new xmlrpcval("ilike","string"),
					new xmlrpcval($key, "string"),
				),
				"array"
			)
		);

		$msg 		= new xmlrpcmsg('execute');
		$msg->addParam(new xmlrpcval($this->dbname,   "string"));
		$msg->addParam(new xmlrpcval($this->id,       "int"));
		$msg->addParam(new xmlrpcval($this->password, "string"));
		$msg->addParam(new xmlrpcval($relation,   "string"));
		$msg->addParam(new xmlrpcval("search",    "string"));
		$msg->addParam(new xmlrpcval($key_array,  "array"));
		$conn      = new xmlrpc_client($this->server_url . 'object');
		$conn->return_type = 'phpvals';
		$resp = $conn->send($msg);
	    if ($resp->faultCode())
	    {
	    	var_dump($resp);
	        return -2;      	
	    }
	    else {
	        if($val = $resp->value()){
	            return $val;     
	        }
	        else
	        {
	            return -1;
	        }
	    }
	}	

	/*
	$relation = nama class
	$ids = array of ids
	$fields = array nama field 
	*/
	function read($relation , $ids, $fields){

		$id_val=array();
		foreach ($ids as $i) {
			$id_val[] = new xmlrpcval($i , "int");
		}

		$fields_val=array();
		foreach ($fields as $f) {
			$fields_val[] = new xmlrpcval($f, "string");
		}

	    $msg = new xmlrpcmsg('execute');
	    $msg->addParam(new xmlrpcval($this->dbname,    "string"));  
	    $msg->addParam(new xmlrpcval($this->id,        "int")); 
	    $msg->addParam(new xmlrpcval($this->password,  "string"));
	    $msg->addParam(new xmlrpcval($relation,        "string"));
	    $msg->addParam(new xmlrpcval("read",           "string"));
	    $msg->addParam(new xmlrpcval($id_val,          "array"));
	    $msg->addParam(new xmlrpcval($fields_val,      "array"));

		$conn      = new xmlrpc_client($this->server_url . 'object');
		$conn->return_type = 'phpvals';

	    $resp = $conn->send($msg);

	    if ($resp->faultCode()){
	    	var_dump($resp);
	        return -1;  
	    }
	    else
	        return ( $resp->value() );

	}




	function create($relation, $values){

	    $msg = new xmlrpcmsg('execute');
	    $msg->addParam(new xmlrpcval($this->dbname,    "string"));  
	    $msg->addParam(new xmlrpcval($this->id,        "int")); 
	    $msg->addParam(new xmlrpcval($this->password,  "string"));
	    $msg->addParam(new xmlrpcval($relation,        "string"));
	    $msg->addParam(new xmlrpcval("create",         "string"));
	    $msg->addParam(new xmlrpcval($values,          "struct"));

		$conn      = new xmlrpc_client($this->server_url . 'object');
		$conn->return_type = 'phpvals';
	    $resp = $conn->send($msg);

	    if ($resp->faultCode()){
	    	var_dump($resp);
	        return -1;  
	    }
	    else{
	        return $resp->value();
	    }
	}



	function delete($relation, $ids) {
		$id_val=array();
		foreach ($ids as $i) {
			$id_val[] = new xmlrpcval($i , "int");
		}

	    $msg = new xmlrpcmsg('execute');
	    $msg->addParam(new xmlrpcval($this->dbname,     "string"));  
	    $msg->addParam(new xmlrpcval($this->id,         "int")); 
	    $msg->addParam(new xmlrpcval($this->password,   "string"));
	    $msg->addParam(new xmlrpcval($relation,         "string"));
	    $msg->addParam(new xmlrpcval("unlink",          "string"));
	    $msg->addParam(new xmlrpcval($id_val,           "array"));

		$conn      = new xmlrpc_client($this->server_url . 'object');
		$conn->return_type = 'phpvals';

	    $resp = $conn->send($msg);

	    if ($resp->faultCode()){
	    	var_dump($resp);
	        return -1;  
	    }
	    else
	        return ( $resp->value() );
	}


	function write($relation, $ids, $values ){

		global $conn, $dbname, $id, $password, $server_url;

		$id_val=array();
		foreach ($ids as $i) {
			$id_val[] = new xmlrpcval($i , "int");
		}

	    $msg = new xmlrpcmsg('execute');
	    $msg->addParam(new xmlrpcval($dbname, "string"));  
	    $msg->addParam(new xmlrpcval($id, "int")); 
	    $msg->addParam(new xmlrpcval($password, "string"));
	    $msg->addParam(new xmlrpcval($relation, "string"));
	    $msg->addParam(new xmlrpcval("write", "string"));
	    $msg->addParam(new xmlrpcval($id_val, "array"));
	    $msg->addParam(new xmlrpcval($values, "struct"));

		$conn      = new xmlrpc_client($server_url . 'object');
		$conn->return_type = 'phpvals';

	    $resp = $conn->send($msg);

	    if ($resp->faultCode()){
	    	var_dump($resp);
	        return -1;  
	    }
	    else
	        return ( $resp->value() );

	}	

}


$openerp = new MyOpenERPLib;
$userId = $openerp->login();
if ($userId == -1) {
	die("Login error ....");
}


echo "===========================\Create one2many data .....\n";
$partners = array(
	array("id"=>7, "name" => "nomor1"),
	array("id"=>168, "name" => "nomor3"),
	array("id"=>172, "name" => "joko"),
);
$att_lines =  array();
foreach($partners as $p) {
	$att_lines[] = new xmlrpcval(
			array(
				new xmlrpcval(0,'int'),
				new xmlrpcval(0,'int'),
				new xmlrpcval(
					array(
						'partner_id'=> new xmlrpcval($p["id"], 'string'), 
						'name' 		=> new xmlrpcval($p["name"], 'string'), 
					), 
					"struct"
				)
			),
			"array"
		); // one record 
}

$attendee_ids = new xmlrpcval(
	$att_lines,
	"array"
);

$values = array(
	'name'          => new xmlrpcval("Session Create o2m dari XML","string"),
	'start_date'    => new xmlrpcval("2014-09-02","string"),
	'attendee_ids'  => $attendee_ids
);

$ret = $openerp->create("academic.session", $values);
echo $ret ;
echo "\n";


echo "===========================\nUpdating data id=2.....\n";
$ids = array(2);
$values = array(
	'name' => new xmlrpcval("Session update dari XML","string"),
	'start_date' => new xmlrpcval("2014-09-01","string")
);
$ret = $openerp->write("academic.session", $ids, $values);
echo $ret ;
echo "\n";


echo "===========================\nDeleting data id=1.....\n";
$ids = array(1);
$ret = $openerp->delete("academic.session", $ids );
echo $ret ;
echo "\n";


echo "===========================\nInserting data.....\n";
$values = array(
	'name'       => new xmlrpcval("Session test dari XML","string"),
	'start_date' => new xmlrpcval("2014-09-01","string")
);
$ret = $openerp->create("academic.session", $values);
echo $ret ;
echo "\n";


echo "===========================\Searching data containing java.....\n";
$session_ids    = $openerp->search("academic.session","java");
var_dump($session_ids);

echo "===========================\Reading data containing java.....\n";
$fields         = array("name","duration");
$records        = $openerp->read("academic.session" , $session_ids, $fields);
foreach ($records as $key => $value) {
	echo $value["name"];
	echo "\n";
}




?>






