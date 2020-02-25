-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS
, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS
, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE
, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema amzorbit
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema amzorbit
-- -----------------------------------------------------
CREATE SCHEMA
IF NOT EXISTS `amzorbit` DEFAULT CHARACTER
SET utf8 ;
USE `amzorbit`
;

-- -----------------------------------------------------
-- Table `amzorbit`.`subscription`
-- -----------------------------------------------------
CREATE TABLE
IF NOT EXISTS `amzorbit`.`subscription`
(
  `id` INT NOT NULL AUTO_INCREMENT,
  `plan_id` VARCHAR
(45) NOT NULL,
  `plan_name` VARCHAR
(45) NOT NULL,
  `tenant_id` VARCHAR
(45) NOT NULL,
  `created_by` INT NULL,
  `create_dt` DATETIME NULL,
  `updated_by` INT NULL,
  `updated_dt` DATETIME NULL,
  PRIMARY KEY
(`id`),
  UNIQUE INDEX `id_UNIQUE`
(`id` ASC),
  UNIQUE INDEX `plan_id_UNIQUE`
(`plan_id` ASC),
  UNIQUE INDEX `plan_name_UNIQUE`
(`plan_name` ASC),
  UNIQUE INDEX `tenant_id_UNIQUE`
(`tenant_id` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `amzorbit`.`user`
-- -----------------------------------------------------
CREATE TABLE
IF NOT EXISTS `amzorbit`.`user`
(
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR
(45) NOT NULL,
  `last_name` VARCHAR
(45) NOT NULL,
  `email_id` VARCHAR
(45) NOT NULL,
  `mobile_num` BIGINT
(20) NULL,
  `tenant_id` INT NOT NULL,
  `create_dt` DATETIME NULL,
  `update_dt` DATETIME NULL,
  `created_by` INT NULL,
  `updated_by` INT NULL,
  `email_alert` TINYINT NULL,
  `sms_alert` TINYINT NULL,
  `alert_preference` VARCHAR
(250) NULL,
  `email_validation` TINYINT NULL,
  `email_daily_digest` TINYINT NULL,
  `subscription_id` INT NOT NULL,
  PRIMARY KEY
(`user_id`),
  UNIQUE INDEX `user_id_UNIQUE`
(`user_id` ASC),
  INDEX `fk_user_subscription1_idx`
(`subscription_id` ASC),
  CONSTRAINT `fk_user_subscription1`
    FOREIGN KEY
(`subscription_id`)
    REFERENCES `amzorbit`.`subscription`
(`id`)
    ON
DELETE NO ACTION
    ON
UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `amzorbit`.`tenant`
-- -----------------------------------------------------
CREATE TABLE
IF NOT EXISTS `amzorbit`.`tenant`
(
  `tenant_id` INT NOT NULL AUTO_INCREMENT,
  `tenant_name` VARCHAR
(45) NULL,
  `create_dt` DATETIME NULL,
  `update_dt` DATETIME NULL,
  `created_by` INT NULL,
  `updated_by` INT NULL,
  PRIMARY KEY
(`tenant_id`),
  UNIQUE INDEX `tenant_id_UNIQUE`
(`tenant_id` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `amzorbit`.`account`
-- -----------------------------------------------------
CREATE TABLE
IF NOT EXISTS `amzorbit`.`account`
(
  `account_id` INT NOT NULL AUTO_INCREMENT,
  `user_name` VARCHAR
(45) NOT NULL,
  `password` VARCHAR
(500) NOT NULL,
  `create_dt` DATETIME NULL,
  `update_dt` DATETIME NULL,
  `created_by` INT NULL,
  `updated_by` INT NULL,
  `user_id` INT NOT NULL,
  `tenant_id` INT NOT NULL,
  PRIMARY KEY
(`account_id`),
  UNIQUE INDEX `account_id_UNIQUE`
(`account_id` ASC),
  UNIQUE INDEX `user_name_UNIQUE`
(`user_name` ASC),
  INDEX `fk_account_user_idx`
(`user_id` ASC),
  INDEX `fk_account_tenant1_idx`
(`tenant_id` ASC),
  CONSTRAINT `fk_account_user`
    FOREIGN KEY
(`user_id`)
    REFERENCES `amzorbit`.`user`
(`user_id`)
    ON
DELETE NO ACTION
    ON
UPDATE NO ACTION,
  CONSTRAINT `fk_account_tenant1`
    FOREIGN KEY
(`tenant_id`)
    REFERENCES `amzorbit`.`tenant`
(`tenant_id`)
    ON
DELETE NO ACTION
    ON
UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `amzorbit`.`role`
-- -----------------------------------------------------
CREATE TABLE
IF NOT EXISTS `amzorbit`.`role`
(
  `role_id` INT NOT NULL AUTO_INCREMENT,
  `role` VARCHAR
(45) NULL,
  `name` VARCHAR
(45) NULL,
  `description` VARCHAR
(100) NULL,
  `configurable` VARCHAR
(45) NULL,
  `create_dt` DATETIME NULL,
  `update_dt` DATETIME NULL,
  `created_by` INT NULL,
  `updated_by` INT NULL,
  `tenant_id` INT NULL,
  PRIMARY KEY
(`role_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `amzorbit`.`account_role`
-- -----------------------------------------------------
CREATE TABLE
IF NOT EXISTS `amzorbit`.`account_role`
(
  `account_id` INT NOT NULL,
  `role_id` INT NOT NULL,
  PRIMARY KEY
(`account_id`, `role_id`),
  INDEX `fk_account_has_role_role1_idx`
(`role_id` ASC),
  INDEX `fk_account_has_role_account1_idx`
(`account_id` ASC),
  CONSTRAINT `fk_account_has_role_account1`
    FOREIGN KEY
(`account_id`)
    REFERENCES `amzorbit`.`account`
(`account_id`)
    ON
DELETE NO ACTION
    ON
UPDATE NO ACTION,
  CONSTRAINT `fk_account_has_role_role1`
    FOREIGN KEY
(`role_id`)
    REFERENCES `amzorbit`.`role`
(`role_id`)
    ON
DELETE NO ACTION
    ON
UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `amzorbit`.`privilege`
-- -----------------------------------------------------
CREATE TABLE
IF NOT EXISTS `amzorbit`.`privilege`
(
  `privilege_id` INT NOT NULL AUTO_INCREMENT,
  `type` VARCHAR
(45) NOT NULL,
  `description` VARCHAR
(200) NULL,
  `tenant_id` INT NULL,
  `create_dt` DATETIME NULL,
  `update_dt` DATETIME NULL,
  `created_by` INT NULL,
  `updated_by` INT NULL,
  PRIMARY KEY
(`privilege_id`),
  UNIQUE INDEX `privilege_id_UNIQUE`
(`privilege_id` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `amzorbit`.`role_privilege`
-- -----------------------------------------------------
CREATE TABLE
IF NOT EXISTS `amzorbit`.`role_privilege`
(
  `role_id` INT NOT NULL,
  `privilege_id` INT NOT NULL,
  PRIMARY KEY
(`role_id`, `privilege_id`),
  INDEX `fk_role_has_privilege_privilege1_idx`
(`privilege_id` ASC),
  INDEX `fk_role_has_privilege_role1_idx`
(`role_id` ASC),
  CONSTRAINT `fk_role_has_privilege_role1`
    FOREIGN KEY
(`role_id`)
    REFERENCES `amzorbit`.`role`
(`role_id`)
    ON
DELETE NO ACTION
    ON
UPDATE NO ACTION,
  CONSTRAINT `fk_role_has_privilege_privilege1`
    FOREIGN KEY
(`privilege_id`)
    REFERENCES `amzorbit`.`privilege`
(`privilege_id`)
    ON
DELETE NO ACTION
    ON
UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `amzorbit`.`payment`
-- -----------------------------------------------------
CREATE TABLE
IF NOT EXISTS `amzorbit`.`payment`
(
  `id` INT NOT NULL AUTO_INCREMENT,
  `last4` VARCHAR
(45) NOT NULL,
  `brand` VARCHAR
(45) NOT NULL,
  `exp_month` INT NOT NULL,
  `exp_year` INT NOT NULL,
  `name` VARCHAR
(45) NOT NULL,
  `stripe_token` VARCHAR
(500) NOT NULL,
  `user_id` INT NOT NULL,
  `create_dt` DATETIME NULL,
  `update_dt` DATETIME NULL,
  `created_by` INT NULL,
  `updated_by` INT NULL,
  PRIMARY KEY
(`id`),
  UNIQUE INDEX `id_UNIQUE`
(`id` ASC),
  INDEX `fk_payment_user1_idx`
(`user_id` ASC),
  CONSTRAINT `fk_payment_user1`
    FOREIGN KEY
(`user_id`)
    REFERENCES `amzorbit`.`user`
(`user_id`)
    ON
DELETE NO ACTION
    ON
UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE
=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS
=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS
=@OLD_UNIQUE_CHECKS;
