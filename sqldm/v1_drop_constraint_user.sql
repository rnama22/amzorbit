-- drop the null constraint on subscription id in user table

ALTER TABLE user CHANGE COLUMN subscription_id subscription_id int NULL;

-- update the user table to nullify the effects of adding constraint
update user set subscription_id=null where subscription_id = 1 and user_id >= 1;

-- adding subscription and payment tables

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



alter table user add column subscription_id INT ;
alter table user add column suscription_expiry datetime ;
alter table user add column email_daily_digest boolean;