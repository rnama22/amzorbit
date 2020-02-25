-- add jwt token columnn to account table 

USE `amzorbit`;
alter table account add column jwt_token varchar
(500);