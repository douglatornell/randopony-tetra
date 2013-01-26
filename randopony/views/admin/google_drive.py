# -*- coding: utf-8 -*-
"""Google Drive interface functions for RandoPony.
"""
import gdata.acl.data


def google_drive_login(service, username, password):
    client = service()
    client.ssl = True
    client.ClientLogin(username, password, 'randopony')
    return client


def get_rider_list_template(template_name, client):
    docs = client.get_resources()
    for doc in docs.entry:
        if doc.title.text == template_name:
            template = doc
            break
    return template


def share_rider_list_publicly(doc, client):
    scope = gdata.acl.data.AclScope(type='default')
    role = gdata.acl.data.AclRole(value='reader')
    acl_entry = gdata.acl.data.AclEntry(scope=scope, role=role)
    client.Post(acl_entry, doc.get_acl_feed_link().href)
