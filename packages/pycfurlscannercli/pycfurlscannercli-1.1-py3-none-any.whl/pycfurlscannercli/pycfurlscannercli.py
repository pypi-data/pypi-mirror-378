#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import datetime
import time
import pprint

import validators
import cloudflare

from cloudflare.types.url_scanner import (
    ScanCreateResponse,
    ScanListResponse,
    ScanBulkCreateResponse,
    ScanDOMResponse,
    ScanGetResponse,
    ScanHARResponse,
    ResponseGetResponse
)

# Globals
VERSION = '1.1'
SECRET_CF_API_KEY = 'SECRET_CF_API_KEY'
SECRET_CF_ACCOUNT_ID = 'SECRET_CF_ACCOUNT_ID'

ACTION_SCAN_SINGLE = 'scan'

# Options definition
parser = argparse.ArgumentParser(description="version: " + VERSION)
common_grp = parser.add_argument_group('Mandatory parameters')
common_grp.add_argument('-k', '--api-key', help='Cloudflare API key (could either be provided in the "%s" env var)' % SECRET_CF_API_KEY, type = str)
common_grp.add_argument('-c', '--account-id', help='Cloudflare Account ID key (could either be provided in the "%s" env var)' % SECRET_CF_ACCOUNT_ID, type = str)
common_grp.add_argument('-a', '--action', help="Action to perform (default '%s')" % ACTION_SCAN_SINGLE, choices = [ACTION_SCAN_SINGLE], type = str.lower, default = ACTION_SCAN_SINGLE)

scan_grp = parser.add_argument_group("'scan' action parameters")
scan_grp.add_argument('-i', '--input-file', help='Input file as a list of newline-separated FQDN or URL')
scan_grp.add_argument('-p', '--protocol', help = 'Protocol to use for each entry when not specified (default \'http_and_https\')', choices = ['http', 'http_and_https', 'https'], type = str.lower, default ='http_and_https')


def urlscanner_scan_single(options):
    retval = os.EX_OK
    
    malicious_urls = []
    
    if options.input_file:
        if os.path.isfile(options.input_file):
            with open(options.input_file, mode='r', encoding='utf-8') as fd_input:
                for line in fd_input:
                    line = line.strip()
                    if line.startswith(('http://', 'https://')) and validators.url(line):
                        malicious_urls.append(line)
                        
                    else:
                        if validators.domain(line):
                            if (options.protocol == 'http') or (options.protocol == 'https'):
                               malicious_urls.append('%s://%s' % (options.protocol, line))
                               
                            elif options.protocol == 'http_and_https':
                                malicious_urls.append('http://' + line)
                                malicious_urls.append('https://' + line)
            
            #pprint.pprint(malicious_urls)
            
            client = cloudflare.Cloudflare(api_token = options.api_key)
            if malicious_urls:
                for malicious_url in malicious_urls:
                    time.sleep(10.1)
                    try:
                        req = client.url_scanner.scans.create(account_id=options.account_id, url=malicious_url)
                        if 'successful' in req.message.lower():
                            print("[+] '%s' submission successful:\t'%s'" % (malicious_url, req.result))
                        else:
                            print("[!] '%s' submission failed | message '%s'" % (malicious_url, req.message))
                        
                    except Exception as e:
                        print("\n[!] '%s' submission failed | code '%s' | error '%s'\n" % (malicious_url, e.status_code, e.errors))
                        continue
                        
        else:
            retval = os.EX_NOINPUT
    
    else:
        retval = os.EX_NOINPUT
    
    return retval


def main():
    global parser
    options = parser.parse_args()
    
    api_key = options.api_key
    if not(api_key):
        if SECRET_CF_API_KEY in os.environ:
            api_key = os.environ[SECRET_CF_API_KEY]
        else:
            parser.error('[!] No Cloudflare API key has been provided, exiting.')
    options.api_key = api_key
    
    
    account_id = options.account_id
    if not(account_id):
        if SECRET_CF_ACCOUNT_ID in os.environ:
            account_id = os.environ[SECRET_CF_ACCOUNT_ID]
        else:
            parser.error('[!] No Cloudflare account ID key has been provided, exiting.')
    options.account_id = account_id
    
    
    if options.action == ACTION_SCAN_SINGLE:
        sys.exit(urlscanner_scan_single(options))
    
    return

if __name__ == "__main__" :
    main()