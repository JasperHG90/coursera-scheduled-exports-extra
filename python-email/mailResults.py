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

    def __init__(self, from_email, password, to_email, location, log_location):
        self.from_email = from_email
        self.to_email = to_email
        self.location = location

        self.from_email

        # Authenticate with yagmail
        self.yag = yagmail.SMTP(from_email, password)

    '''
    Subset data
    '''

    def ss_data(self,df):
        tn = datetime.datetime.now().strftime("%Y-%m-%d")
        tt = (datetime.datetime.now() - datetime.timedelta(days=6)).strftime("%Y-%m-%d")
        self.tn = tn
        self.tt = tt
        # Add date
        df['date'] = df.ix[:,0].map(lambda x: x.split(" ")[0])
        # Index
        df = df[(df['date'] >= tt) & (df['date'] <= tn)]
        return df

    '''
    Process metadata
    '''

    def process_metadata(self, df):
        # Get stats
        lendf = len(df.index)
        successful_requests = sum(df.ix[:, 1] == "SUCCESS")
        failed_requests = lendf - successful_requests
        # Return metadata
        m = {"from":self.tt, "to":self.tn, "number_requests":lendf, "success":successful_requests, "failed":failed_requests}
        # Dump file temporary so can mail it.
        cwd = os.getcwd()
        if not os.path.exists("{}/.temp/".format(cwd)):
            os.makedirs("{}/.temp/".format(cwd))
        df.to_csv("{}/.temp/metadata.csv".format(cwd))
        return m

    '''
    Dump logfile to temp folder
    '''

    def dump_logfile(self,df):
        cwd = os.getcwd()
        if not os.path.exists("{}/.temp/".format(cwd)):
            os.makedirs("{}/.temp/".format(cwd))
        df.to_csv("{}/.temp/logfile.txt".format(cwd), sep="\t")

    '''
    Read metadata.txt file and process
    '''

    def read_metadata(self):
        with open(self.location, 'r') as inFile:
            return self.process_metadata(self.ss_data(pd.read_table(inFile, header=None)))

    '''
    Read logfile.txt and process
    '''

    def read_logfile(self, loglocation):
        with open(loglocation, 'r') as inFile:
            self.dump_logfile(self.ss_data(pd.read_table(inFile, header=None)))

    '''
    Send email
    '''

    def send_email(self, meta):
        subject = "Scheduled coursera data exports: status report for {} to {}.".format(meta["from"], meta["to"])
        content = "From {} to {}, {} requests were submitted to the coursera API. {} requests succeeded, {} requests failed. You can find an overview of the requests in the attached 'metadata.csv' file. You can trace potential errors in the attached 'log.csv' file.".format(meta["from"], meta["to"], meta["number_requests"], meta["success"], meta["failed"])
        metadatafile = "{}/.temp/metadata.csv".format(os.getcwd())
        logdatafile = "{}/.temp/logfile.txt".format(os.getcwd())

        if args.send_log != None:
            self.yag.send(to=self.to_email, subject=subject, contents=[content, metadatafile, logdatafile])
        else:
            self.yag.send(to=self.to_email, subject=subject, contents=[content, metadatafile])

'''
Call
'''

if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("from_email", help="Email account from which you'll send the updates.", type=str)
    parser.add_argument("password", help="Email account password", type=str)
    parser.add_argument("to_email", help="Email account to which the updates will be sent.", type=str)
    parser.add_argument("location", help="Location of 'metadata.txt' file", type = str)
    parser.add_argument("--send_log", help="Optional. Send log file in email. Supply location of log file", type=str)
    args = parser.parse_args()

    # Check if file exists
    if not os.path.isfile(args.location):
        raise filenotfound("File does not exists in this location.")

    # Initiate
    m = mailresults(args.from_email, args.password, args.to_email, args.location, args.send_log)
    # Read file
    df = m.read_metadata()
    # Dump log
    if args.send_log != None:
        m.read_logfile(args.send_log)
    # Send email
    m.send_email(df)

    print True
