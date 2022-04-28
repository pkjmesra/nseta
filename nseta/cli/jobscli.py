# -*- coding: utf-8 -*-
from time import time

from nseta.common.log import tracelog, default_logger

from nseta.jobs.dataDownloaderJob import *
import click

__all__ = ['jobs']

JOB_MAPPING = {
  "download": dataDownloaderJob,
}

@click.command(help='Starts or stops the jobs in the background')
@click.option('--job','-j', default='download', type=click.Choice(JOB_MAPPING),
  help=', '.join(JOB_MAPPING) + '. Choose one.')
@click.option('--start', default=False, is_flag=True, help='By default(False). --start, if you would like the job to be started')
@click.option('--stop', default=False, is_flag=True, help='By default(False). --stop, if you would like the job to be stopped')
@tracelog
def jobs(job, start, stop):
  start_time = time()
  try:
    downloadJob = dataDownloaderJob()
    if start:
      downloadJob.start()
    elif stop:
      downloadJob.stop()
    end_time = time()
    time_spent = end_time-start_time
    print('\nThis run of job took {:.1f} sec'.format(time_spent))
  except Exception as e:
    default_logger().debug(e, exc_info=True)
    click.secho('Failed to run the job. Please check the inputs.', fg='red', nl=True)
    return
  except SystemExit:
    pass
