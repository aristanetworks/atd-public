<?php

$vms = array();
$vms[] = array('spine1','192.168.0.10');
$vms[] = array('spine2','192.168.0.11');
$vms[] = array('leaf1','192.168.0.14');
$vms[] = array('leaf2','192.168.0.15');
$vms[] = array('leaf3','192.168.0.16');
$vms[] = array('leaf4','192.168.0.17');
$vms[] = array('host1','192.168.0.31');
$vms[] = array('host2','192.168.0.32');
$vms[] = array('cvx01','192.168.0.44');

$port = 22;
$timeout = 4;

foreach($vms as $vm){

  $socket = fsockopen($vm[1], $port, $errno, $errstr, $timeout); 

  if(!$socket){ 
    $status = '<font color="RED">down</font>'; 
  } else { 
    $status = '<font color="GREEN">up</font>'; 
    fclose($socket);
  }
  echo "$vm[0] is $status<br>\n";
}
?>
