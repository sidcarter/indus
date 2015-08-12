#!/usr/bin/env python

import sys
import mechanize
from bs4 import BeautifulSoup

def browse_schwab():
    # set some constants
    schwab_url = "https://www.schwab.com/public/schwab/client_home"
    username = ""
    password = ""

    br = mechanize.Browser()
    br.addheaders = [('User-agent', 'Mozilla/Firefox Plan-9 11.34')]

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(False)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    print("-> Logging in...")
    br.open(schwab_url)
    br.select_form("SignonForm")
    br.find_control("SignonAccountNumber").value = username
    br.find_control("SignonPassword").value = password

    br.submit()
    redirect_url= br.geturl()

    if 'Error' in redirect_url:
        sys.exit("-> Incorrect login")
        
    br.open(redirect_url)
    print("-> Success")

    res_html = br.response().read()

    soup = BeautifulSoup(res_html, 'html.parser')

    account_name = soup.find(id='ctl00_wpm_ac_ac_rba_ctl00_lnkBankAccountName').get_text()
    account_id = soup.find(id='ctl00_wpm_ac_ac_rba_ctl00_lnkBankAccountId').get_text()
    account_bal = soup.find(id='ctl00_wpm_ac_ac_rba_ctl00_dsv').get_text()

    print("Your %s account with id %s has a balance of %s" % (account_name, account_id, account_bal))
    print("-> Logging out")
    br.follow_link(text='Log Out')

if __name__ == "__main__":
    browse_schwab()