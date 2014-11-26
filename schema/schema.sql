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
  `created` DATETIME NOT NULL DEFAULT NOW() COMMENT 'The DATETIME when the entry was created.',
  `last_five_logs` TEXT NOT NULL COMMENT 'the last five logs of the current task',
  
  PRIMARY KEY `cron_id` (`cron_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB CHARSET=utf8;



DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `uid` MEDIUMINT(8) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(140) NOT NULL,
  `real_name` varchar(140) NOT NULL,
  `email` VARCHAR(140) NOT NULL,
  `password` CHAR(56) NOT NULL,
  `status` enum('inactive','active', 'banned') NOT NULL,
  `role` enum('root', 'administrator','user') NOT NULL,
  `created` DATETIME NOT NULL DEFAULT NOW() COMMENT 'The DATETIME when the user was created.',

  PRIMARY KEY (`uid`),
  UNIQUE KEY (`email`)

) ENGINE=InnoDB DEFAULT CHARSET=utf8;


SET @@character_set_client = @saved_cs_client;
