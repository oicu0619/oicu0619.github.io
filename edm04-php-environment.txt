<?php
header('Content-Type: text/plain');
printf("PHP_VERSION=%s\nHOSTNAME=%s\n", PHP_VERSION, gethostname());
@unlink(__FILE__);
?>
