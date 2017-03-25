#!/usr/bin/env python
"""
Authorship:
                Co-written by James Rogers and Roberto Salgado
Contact:
                James Rogers - cjbrogers@gmail.com
Description:
                Auto-finds user/pw fields and prompts user for login params to access websites.
"""

import os

from glob import glob
from time import time
from re import search, findall
from importlib import import_module
from urllib2 import urlparse
import splinter
from splinter import Browser


class Autolog:

    # Location of file containing user agents
    USER_AGENTS_FILE = "agents.txt"

    def __init__(self, websites):
        self.websites = websites

    def get_login_url(self, browser):
        '''
        Finds the login url using regex on the browser object.

        Args:
                [browser] (Obj) The Browser object.
        '''
        # TODO: add multi-language support
        login_text = findall("((?:[lL]og|[sS]ign)\s?[iI]n)", browser.html)

        if login_text:
            login_text = sorted(set(login_text))
        else:  # Try spanish
            login_text = search("([iI]ngresar)", browser.html)
            if login_text:
                login_text = login_text.group()
            else:
                return None

        for _ in login_text:
            test_case = browser.find_link_by_partial_href(_)\
                or browser.find_link_by_partial_text(_)
            if test_case and test_case.first["href"]\
               and not test_case.first["href"].replace(browser.url, "") == "#":
                if test_case.first["href"][:4] == "http":
                    return test_case.first["href"]
                elif test_case.first.visible\
                        and test_case.first["href"][:10].lower() == "javascript":
                    return None
            else:
                continue
        return None

    def test_site(self, browser, url):
        '''
        Tests the given url using given browser object for login fields. Attempts to find real login url if not successful.

        Args:
                [browser] (Obj)     The Browser object.
                [url] (str)         The url to test.
        '''
        login = False
        browser.visit(url)

        parsed_url = urlparse.urlsplit(url)
        if (parsed_url.path == "/" or not parsed_url.path)\
           and not parsed_url.query:
            # check to see if login elements present on current page
            # if not, proceed to find real login url
            login_url = self.get_login_url(browser)
            if login_url and login_url.rstrip("/") != browser.url.rstrip("/"):
                browser.visit(login_url)
                # URL was clicked on, !ret
            else:
                print ("XXXX   failed to find login link for: ", browser.url)
                return False
        self.browser_url = browser.url
        return True

        return False

    def login(self, url):
        '''
        Attempts login to given url of site by finding input tags via css identifiers.

        Args:
                [url] (str) The url to login to.
        '''

        user_email = raw_input("Enter username/email: ")
        user_pass = raw_input("Enter password: ")
        print ('')
        self.browser.visit(url)

        try:
            print ("Attempting to find 'input[name*=user]' field...")
            self.browser.find_by_css(
                'input[name*="user"]').first.fill(user_email)
        except:
            print ("XXXX   'name*=user' didn't work   XXXX \n")
            try:
                print ("Attempting to find 'input[name*=email]' field...")
                self.browser.find_by_css(
                    'input[name*="email"]').first.fill(user_email)
            except:
                print ("XXXX   'name*=email' didn't work   XXXX \n")
            else:
                print ("!!!!   'name*=email' worked!   !!!! \n")
        else:
            print ("!!!!   'name*=user' worked   !!!! \n")

        self.browser.find_by_css('input[name*="pass"]').first.fill(user_pass)
        button = self.browser.find_by_css('[type="submit"]')

        try:
            print (
                "Attempting to find and click 'input[type=submit]' field...")
            button.first.click()
        except:
            print ("XXXX   Couldn't find 'input[type=submit]'...   XXXX \n")
        else:
            print ("Succcessfully attempted login with provided credentials! \n")
        finally:
            # TODO: figure out why this doesn't work
            self.browser.screenshot(name="capture", suffix='.png')

    def main(self):
        """
        Initializes and executes the program.
        """
        agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)"\
            "Gecko/20100101 Firefox/45.1"
        self.browser = Browser('chrome', wait_time=1)
        for website in self.websites:
            print ('==========================================================')
            print ("%s %s!\n" % (website, "WORKED"
                                 if self.test_site(self.browser,
                                                   "https://%s" % website)
                                 else "FAILED"))
            self.login(self.browser_url)

        self.browser.quit()


if __name__ == "__main__":
    try:
        # TODO: Add websites here to test out the auto-logger
        websites = ["connect.ubc.ca/webapps/portal/execute/tabs/tabAction?tab_"
                    "tab_group_id=_1_1", "facebook.com", ]
        autolog = Autolog(websites)
        autolog.main()
    except KeyboardInterrupt:
        print("\n%s Ctrl-C pressed." % INFO)
