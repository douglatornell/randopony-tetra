# -*- coding: utf-8 -*-
"""Google Drive interface functions for RandoPony.
"""
# import gdata.acl.data
# from gdata.docs.client import DocsClient
# from gdata.spreadsheet.service import SpreadsheetsService


def google_drive_login(service, username, password):
    client = service()
    client.ssl = True
    client.ClientLogin(username, password, 'randopony')
    return client


def create_rider_list(event, template_name, username, password):
    flash = []
    if event.google_doc_id:
        flash.append('error')
        flash.append('Rider list spreadsheet already created')
        return flash
    google_doc_id = create_google_drive_list(
        event, template_name, username, password)
    event.google_doc_id = google_doc_id
    flash.append('success')
    flash.append('Rider list spreadsheet created')
    return flash


def create_google_drive_list(event, template_name, username, password):
    """Execute Google Drive operations to create rider list from template,
    and share it publicly.

    Returns the id of the created document that is used to construct its
    URL.
    """
    client = google_drive_login(DocsClient, username, password)
    template = get_rider_list_template(template_name, client)
    created_doc = client.copy_resource(template, str(event))
    share_rider_list_publicly(created_doc, client)
    return created_doc.resource_id.text


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


def update_rider_list_info_question(brevet, username, password):
    client = google_drive_login(SpreadsheetsService, username, password)
    key = brevet.google_doc_id.split(':')[1]
    client.UpdateCell(1, 6, brevet.info_question, key)
    return ['success', 'Rider list info question column updated']
