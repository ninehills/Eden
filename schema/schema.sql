SET @saved_cs_client = @@character_set_client;
SET character_set_client = utf8;


CREATE TABLE `cron` (
  `cron_id` INT(11) unsigned NOT NULL AUTO_INCREMENT,
  `task_id` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(124) NOT NULL,
  `action` VARCHAR(124) NOT NULL,
  `data` TEXT DEFAULT NULL,
  `event`  VARCHAR(64) NOT NULL,
  `next_run` DATETIME DEFAULT NULL,
  `last_run` DATETIME DEFAULT NULL,
  `run_times` INT(11) unsigned NOT NULL,
  `attempts` TINYINT DEFAULT 0 NOT NULL,
  `status` TINYINT unsigned DEFAULT 0,
  
  PRIMARY KEY `cron_id` (`cron_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB CHARSET=utf8;




SET @@character_set_client = @saved_cs_client;
