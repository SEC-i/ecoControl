#!/usr/bin/env python
import threading, time
import logging

from django.utils.timezone import utc

from server.helpers import write_pidfile_or_fail
from server.models import Task

from functions import *
import commands

logger = logging.getLogger('planner')

# Planner thread class
class Planner(threading.Thread):
    def __init__(self, frequency=60):
        threading.Thread.__init__(self)
        self.daemon = True
        self.frequency = frequency
        #make sure only one instance is running at a time
        self.is_unique_thread = True
        if not write_pidfile_or_fail("/tmp/planner.pid"):
            self.is_unique_thread = False
        # start thread immediately
        self.start()
        self.running_tasks = []

    def run(self):
        if self.is_unique_thread:
            print " * Planner started..."
            logger.debug("planner started")
            


            while(True):
                simple_moisture_check()
                simple_battery_check()
                #update_delta()
                #check_rules()
                #self.check_and_execute_tasks()
                # log function calls if frequency >= 10 seconds
                if self.frequency>9:
                    logger.debug("Planner function called")
                
                time.sleep(self.frequency)
        else:
            logger.debug("Duplicate planner thread avoided")
            print " * Duplicate planner thread avoided"

    def check_and_execute_tasks(self):
        #remove finished tasks
        for task in self.running_tasks:
            if task.running == False:
                task.join()
                self.running_tasks.remove(task)

        for task in Task.objects.all():
            if task.execution_timestamp <= datetime.now().replace(tzinfo=utc) and task.status == 0:
                t = TaskThread(task)
                self.running_tasks.append(t)
                logger.debug("execute task" + task.command)




class TaskThread(threading.Thread):
    def __init__(self,task):
        threading.Thread.__init__(self)
        self.task = task
        task.status = 1
        task.save()
        self.running = True
        self.start()

    def run(self):
        self.status = eval("commands." + self.task.command + "()")
        self.running = False
        self.task.delete()

