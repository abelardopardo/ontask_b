from django.core.management.base import BaseCommand
from ontask.agent.utils.predictive_course import agent
import logging

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.__agent__ = agent()
        #self.__agent__.create_course()
        self.__agent__.get_quizes()
