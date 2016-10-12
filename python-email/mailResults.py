#! /usr/bin/env python

'''
Copyright 2016 Leiden University

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

'''
# Mail results of data downloads once a week.
# Jasper Ginn
# 11/10/2016
'''

import yagmail
import datetime
import pandas as pd
import os
import argparse

'''
Exceptions
'''

class filenotfound(Exception):
    pass

'''
Ingest location to metadata file and email details
TODO: write readme how to authenticate with yagmail!
'''

class mailresults:

    def __init__(self, from_email, to_email, location):
        self.from_email = from_email
        self.to_email = to_email
        self.location = location
        self.time_now = datetime.datetime.now()

    # Authenticate with yagmail
    self.yag = yagmail.SMTP(from_email)

    '''
    Read metadata.txt file
    '''

    def read_metadata(self):
        with open(self.location, 'r') as inFile:
            return pd.read_table(inFile)

'''
Call
'''

if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("from_email", help="Email account from which you'll send the updates.", type=str)
    parser.add_argument("to_email", help="Email account to which the updates will be sent.", type=str)
    parser.add_argument("location", help="Location of 'metadata.txt' file", type = str)
    args = parser.parse_args()

    # Check if file exists
    if not os.file.exist(args.location):
        raise filenotfound("File does not exists in this location.")

    # Initiate
    m = mailresults(args.from_email, args.to_email, args.location)
    # Read file
    df = m.read_metadata()
