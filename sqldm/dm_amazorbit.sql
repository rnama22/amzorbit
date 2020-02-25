-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema amzorbit
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema amzorbit
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `amzorbit` DEFAULT CHARACTER SET utf8 ;
USE `amzorbit` ;

-- -----------------------------------------------------
-- Table `amzorbit`.`product`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `amzorbit`.`product` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `uid` VARCHAR(45) NOT NULL,
  `asin` VARCHAR(45) NOT NULL,
  `platform` VARCHAR(45) NOT NULL,
  `ideal_state` TEXT NULL,
  `health_status` VARCHAR(45) NOT NULL,
  `current_state` TEXT NULL,
  `state_diff` VARCHAR(10000) NULL,
  `market` VARCHAR(45) NULL,
  `product_info_status` VARCHAR(45) NULL,
  `title` VARCHAR(5000) NULL,
  `archive` TINYINT NULL,
  `image` VARCHAR(1000) NULL,
  `refresh_dt` DATETIME NULL,
  `create_dt` DATETIME NOT NULL,
  `created_by` INT NOT NULL,
  `update_dt` DATETIME NULL,
  `updated_by` INT NULL,
  `tenant_id` INT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `amzorbit`.`product_state_history`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `amzorbit`.`product_state_history` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `current_state` TEXT NOT NULL,
  `state_diff` VARCHAR(10000) NULL,
  `ideal_state` TEXT NULL,
  `create_dt` DATETIME NOT NULL,
  `created_by` DATETIME NULL,
  `update_dt` INT NULL,
  `updated_by` INT NULL,
  `tenant_id` INT NULL,
  `product_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `fk_product_state_history_product_idx` (`product_id` ASC),
  CONSTRAINT `fk_product_state_history_product`
    FOREIGN KEY (`product_id`)
    REFERENCES `amzorbit`.`product` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `amzorbit`.`alert`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `amzorbit`.`alert` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `alert_type` VARCHAR(45) NOT NULL,
  `message` VARCHAR(1000) NOT NULL,
  `meta_data` VARCHAR(1000) NULL,
  `status` VARCHAR(45) NOT NULL,
  `create_dt` DATETIME NOT NULL,
  `created_by` INT NULL,
  `update_dt` DATETIME NULL,
  `updated_by` INT NULL,
  `tenant_id` INT NULL,
  `product_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `fk_alert_product1_idx` (`product_id` ASC),
  CONSTRAINT `fk_alert_product1`
    FOREIGN KEY (`product_id`)
    REFERENCES `amzorbit`.`product` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
