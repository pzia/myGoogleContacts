#!/usr/bin/python3
# -*- coding: utf-8 -*-

import googlePeopleApi
import re

#some docs
#https://developers.google.com/resources/api-libraries/documentation/people/v1/python/latest/index.html

#match (NOM) (Prenom) (<departement>)
rethund = re.compile(r'([A-Z-]+(?:-[a-zA-Z]+)?)\s([a-zA-Z]+(?:-[a-zA-Z]+)?)\s\(\d+\)')
#match (foo[-bar]).(tic[-tac])@something
repnom = re.compile(r'(^[a-zA-Z]+(?:-[a-zA-Z]+)?)\.([a-zA-Z]+(?:-[a-zA-Z]+)?)@.*')
emailStore = []

#Commands
def commandImportThund(fname):
    s = googlePeopleApi.iterConnexions(emailstore)
    with open(fname) as f :
        for line in f.readlines():
            fields = line.split(',')
            email = fields[4].lower()
            if '@' not in email :
                continue
            if email in emailStore:
                continue
            print("CREATE %s" % email)
            p = s.people().createContact(body={'emailAddresses':[{'value' : email}]}).execute()
            p = match_void(p, s)

def commandGeneric(*func):
    return googlePeopleApi.iterConnexions(*func)

#helpers (iter)
def emailstore(p, people_service):
    if 'emailAddresses' in p :
        for e in p['emailAddresses']:
            emailStore.append(e['value'].lower())
    return p

def test(p, people_service):
    if 'names' in p :
        print(p['names'][0]['displayName'])
    return p

def match_brackets(p, people_service):
    if 'names' in p :
        name = None
        if len(p['names']) > 1 :
            return p
        for n in p['names']:
            if n['metadata']['source']['type'] == "CONTACT" :
                name = n
                break
        if name == None :
            return p

        m = rethund.search(name['displayName'])
        if m is not None :
            family = m.groups()[0]
            given = m.groups()[1]
            if family == "CONSULTANT":
                return p
            print(name['displayName'], "=>", given, family)
            p['names'] = [
                {
                  'displayName' : "%s %s" % (given, family),
                  'givenName' : given,
                  'familyName' : family
                }
            ]
            return people_service.people().updateContact(resourceName=p['resourceName'], body=p, updatePersonFields='names').execute()
    return p

def match_void(p, people_service):
    if 'names' not in p and 'emailAddresses' in p :
        if len(p['emailAddresses']) > 1 :
            print("Too many addresses for NO NAME")
            return p
        m = repnom.search(p['emailAddresses'][0]['value'])
        if m is not None :
            given = m.groups()[0].title()
            family = m.groups()[1].title()
            p['names'] = [
                {
                  'displayName' : "%s %s" % (given, family),
                  'givenName' : given,
                  'familyName' : family
                }
            ]
            print("%s %s for %s" % (given, family, p['emailAddresses'][0]['value']))
            return people_service.people().updateContact(resourceName=p['resourceName'], body=p, updatePersonFields='names').execute()
        else: 
            print("NO MATCH for %s" % p['emailAddresses'][0]['value'])
    return p
