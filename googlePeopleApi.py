#!/usr/bin/python3
# -*- coding: utf-8 -*-

#import conf (dirty but simple)
import myconf

#for quota - exponential backoff
import time

#copy from python google client tutorial
import httplib2
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools

# Set up a Flow object to be used if we need to authenticate. This
# sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
# the information it needs to authenticate. Note that it is called
# the Web Server Flow, but it can also handle the flow for
# installed applications.
#
# Go to the Google API Console, open your application's
# credentials page, and copy the client ID and client secret.
# Then paste them into the following code.

def get_google_service_api():
    FLOW = OAuth2WebServerFlow(
        client_id=myconf.client_id,
        client_secret=myconf.client_secret,
        scope=myconf.scope,
        user_agent=myconf.user_agent)

    # If the Credentials don't exist or are invalid, run through the
    # installed application flow. The Storage object will ensure that,
    # if successful, the good Credentials will get written back to a
    # file.
    storage = Storage('info.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid == True:
        credentials = tools.run_flow(FLOW, storage)

    # Create an httplib2.Http object to handle our HTTP requests and
    # authorize it with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Build a service object for interacting with the API. To get an API key for
    # your application, visit the Google API Console
    # and look at your application's credentials page.
    people_service = build(serviceName='people', version='v1', http=http)
    return(people_service)

def beNice(obj):
    """Be nice : exponential backoff when over quota"""
    wait = 1
    while wait :
        try :
            return_value = obj.execute()
            wait = 0
        except : #FIXME : we should test the type of the exception
            print("EXCEPT : Wait for %d seconds" % wait)
            time.sleep(wait)
            wait *= 2
    return(return_value)

def iterConnexions(*func):
    """basic iteration through list of connections with the *func functions
    func take a person and a people service as args, and return a person
    """
    
    people_service = get_google_service_api() #FIXME : test
    connections = beNice(people_service.people().connections().list(resourceName='people/me', personFields='names,emailAddresses'))
    #Fixme : test ?

    counter = 0

    while True :
        for p in connections['connections']: #for each connections
            counter += 1
            for f in func : #for each func
                p = f(p, people_service)
        if 'nextPageToken' in connections : #there is more
            print("==Counter==%d, go to Next Page" % counter)
            connections = beNice(people_service.people().connections().list(resourceName='people/me', personFields='names,emailAddresses', pageToken=connections['nextPageToken'])) 
        else : 
            break

    print("==Counter==%d, end of story" % counter)
    return(people_service)