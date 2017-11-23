# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from contextlib import contextmanager

import pandas as pd
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import reverse
from django.test import TestCase, LiveServerTestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APITransactionTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.ui import WebDriverWait

from dataops import pandas_db
from ontask.permissions import group_names

# email, [groups], Superuser?
user_info = [
    ('Student One', 'student1@bogus.com', [group_names[0]], False),
    ('Student Two', 'student2@bogus.com', [group_names[0]], False),
    ('Student Three', 'student3@bogus.com', [group_names[0]], False),
    ('Instructor One', 'instructor1@bogus.com', [group_names[1]], False),
    ('Instructor Two', 'instructor2@bogus.com', [group_names[1]], False),
    ('Ainstructor One', 'ainstructor1@bogus.com', [group_names[2]], False),
    ('Ainstructor Two', 'ainstructor2@bogus.com', [group_names[2]], False),
    ('Idesigner One', 'idesigner1@bogus.com', [group_names[3]], False),
    ('Idesigner Two', 'idesigner2@bogus.com', [group_names[3]], False),
    ('Aidesigner One', 'aidesigner1@bogus.com', [group_names[4]], False),
    ('Aidesigner Two', 'aidesigner2@bogus.com', [group_names[4]], False),
    ('Super User', 'superuser@bogus.com', group_names, True)]

boguspwd = 'boguspwd'

# Workflow elements used in various tests
wflow_name = 'wflow1'
wflow_desc = 'description text for workflow 1'
wflow_empty = 'The workflow does not have data'


def create_groups():
    """
    Create the user groups for OnTask
    :return:
    """

    for gname in group_names:
        Group.objects.get_or_create(name=gname)


def create_users():
    """
    Create all the users based in the user_info
    :return:
    """

    # Create the groups first
    create_groups()

    for uname, uemail, glist, suser in user_info:
        try:
            uobj = get_user_model().objects.get(email=uemail)
        except ObjectDoesNotExist:
            uobj = get_user_model().objects.create_user(
                name=uname,
                email=uemail,
                password=boguspwd)

        for gname in glist:
            gobj = Group.objects.get(name=gname)
            uobj.groups.add(gobj)
            uobj.save()

    # Create the tokens for all the users
    for usr in get_user_model().objects.all():
        Token.objects.create(user=usr)


class OntaskTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)
        super(OntaskTestCase, cls).tearDownClass()


class OntaskApiTestCase(APITransactionTestCase):
    @classmethod
    def tearDownClass(cls):
        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)
        super(OntaskApiTestCase, cls).tearDownClass()

    def compare_wflows(self, jwflow, workflow):
        # Name and description match the one in the db
        self.assertEqual(jwflow['name'], workflow.name)
        self.assertEqual(jwflow['description_text'],
                         workflow.description_text)

        jattr = jwflow['attributes']
        dattr = workflow.attributes
        self.assertEqual(set(jattr.items()),
                         set(dattr.items()))

    def compare_matrices(self, m1, m2):
        """
        Compares two pandas data frames
        :param m1: Pandas data frame
        :param m2: Pandas data frame
        :return:
        """

        # If both are empty, done.
        if m2 is None and m1 is None:
            return

        # Assert that the number of columns are identical
        self.assertEqual(len(list(m1.columns)),
                         len(list(m2.columns)))

        # The names of the columns have to be identical
        self.assertEqual(set(list(m1.columns)),
                         set(list(m2.columns)))

        # Check the values of every column
        for cname in list(m1.columns):
            jvals = m1[cname].values
            dfvals = m2[cname].values

            # Compare removing the NaN, otherwise, the comparison breaks.
            self.assertEqual(
                [x for x in list(jvals) if not pd.isnull(x)],
                [x for x in list(dfvals) if not pd.isnull(x)]
            )


class OntaskLiveTestCase(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(OntaskLiveTestCase, cls).setUpClass()
        fp = webdriver.FirefoxProfile()
        fp.set_preference("dom.file.createInChild", True)
        cls.selenium = webdriver.Firefox(firefox_profile=fp)
        # cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        pandas_db.destroy_db_engine(pandas_db.engine)
        super(OntaskLiveTestCase, cls).tearDownClass()

    def open(self, url):
        self.selenium.get("%s%s" % (self.live_server_url, url))

    def login(self, uemail):
        self.open(reverse('accounts:login'))
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_username')))
        self.selenium.find_element_by_id('id_username').send_keys(uemail)
        self.selenium.find_element_by_id('id_password').send_keys(boguspwd)
        self.selenium.find_element_by_id('submit-id-sign_in').click()

        self.assertIn('Edit Profile', self.selenium.page_source)

    def logout(self):
        self.open(reverse('accounts:logout'))

    @contextmanager
    def wait_for_page_load(self, timeout=30):
        # Hack taken from
        # http://www.obeythetestinggoat.com/
        # how-to-get-selenium-to-wait-for-page-load-after-a-click.html
        old_page = self.selenium.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.selenium, timeout).until(
            staleness_of(old_page)
        )
