-- Add 'orgpconly' column to 'help_topic' table if it doesn't exist
SET @s = (SELECT IF(
    (SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE table_name = CONCAT('%TABLE_PREFIX%', 'help_topic')
        AND table_schema = DATABASE()
        AND column_name = 'orgpconly'
    ) > 0,
    "SELECT 1",
    "ALTER TABLE `%TABLE_PREFIX%help_topic` ADD `orgpconly` tinyint(1) unsigned NOT NULL default '0' AFTER `ispublic`"
));
PREPARE stmt FROM @s;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Create 'help_topic_organization' table if it doesn't exist
CREATE TABLE IF NOT EXISTS `%TABLE_PREFIX%help_topic_organization` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `topic_id` int(11) unsigned NOT NULL,
  `organization_id` int(11) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `topic_organization` (`topic_id`,`organization_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
