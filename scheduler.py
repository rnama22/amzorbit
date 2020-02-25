import os
import yaml
from flask import request
from flask_restful import Resource
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from globalinfo.globalutils import engine, mode, logger
from productmanagement.product.service.productservice import ProductService

with open('config.yml') as config_input:
    config = yaml.load(config_input)


product_service = ProductService()
scheduler = BackgroundScheduler()

scheduler.add_jobstore(SQLAlchemyJobStore(
    url=config[mode]['SQL_ENGINE']))


def start_scraping():
    '''
        method to invoke the scraping for all the products
    '''
    logger.info('Scheduler Initiated Scraping all method')
    product_service.scrape_all()


def start_daily_digest():
    '''
    method to invoke the daily digest
    '''
    logger.info('Scheduler Initiated Daily Digest')
    product_service.daily_digest_task()


def start_scheduler():
    '''
        This method adds the jobs to the scheduler. 

        It checks if the table exists and creates if it doesn't
        Need to drop the table if we need to add a new job

        currently schedules two jobs
            - scrapping for every one hour
            - daily digest every day at 5am

    '''

    logger.debug('In scheduler start method')

    if 'apscheduler_jobs' not in engine.table_names():

        scheduler.add_job(start_scraping, 'interval', hours=23)
        scheduler.add_job(start_daily_digest, trigger='cron', hour='09')

    try:
        scheduler.start()
    except:
        scheduler.shutdown()
