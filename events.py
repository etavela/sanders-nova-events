#!/usr/bin/python

import csv
from datetime import datetime
import json
import logging
import requests

NOVA_ZIP_CODE_RANGES = [
    range(22301, 22315),    # Alexandria City
    range(22320, 22336),    # Alexandria City
    range(22200, 22299),    # Arlington County
    range(22030, 22032),    # Fairfax City
    range(22401, 22405),    # Fredericksburg City
]

NOVA_ZIP_CODES = set([
    22611, 20135, 22620, 22646, 20135, 22611, 20130, 22663,  # Clarke County
    22714, 22713, 22718, 22724, 22726, 22729, 22733, 22735, 22737, 22736, 22741, 22701, # Culpeper county
    22303, 22307, 22306, 22309, 22308, 22311, 22310, 22312, 22315, 22003, 20120, 22015, # Fairfax county
    22027, 20121, 22031, 22030, 20124, 22033, 22032, 22035, 22039, 22041, 22043, 22042, # Fairfax county
    22046, 22044, 22060, 22066, 20151, 22079, 22082, 22101, 22102, 22116, 20171, 20170, # Fairfax county
    22122, 22124, 22151, 22150, 22153, 22152, 20191, 20190, 22181, 20192, 22180, 22182, 20194, # Fairfax county
    22040, 22042, 22044, 22046, # Falls Church city
    20144, 22639, 22642, 22643, 22712, 20187, 20186, 20106, 20188, 22720, 20115, 20119, 20198, # Fauquier county
    22728, 20128, 20130, 22734, 22739, 20139, 20138, 22742, 20140, # Fauquier county
    22622, 22624, 22625, 22637, 22645, 22654, 22656, 22655, 22602, 22663, 22603, # Frederick county
    20148, 20147, 20152, 20159, 20158, 20160, 20165, 20164, 20166, 20175, 20177, # Loudon county
    20176, 20180, 20178, 20105, 20184, 20197, 20117, 20129, 20132, 20135, 20134, 20141, 20142, # Loudon county
    22748, 22715, 22719, 22723, 22722, 22725, 22727, 22731, 22730, 22732, 22738, 22948, 22743, # Madison county
    22709, 22711, # Madison county
    20108, 20110, # Manassas city
    20111, # Manassas Park city
    20156, 20155, 20169, 22125, 22134, 20181, 20109, 22172, 20111, 20110, 20112, 22192, 22025, # Prince William county
    22191, 22026, 22193, 22195, 20137, 20136, 20143, # Prince William county
    22749, 22716, 22623, 22627, 22640, 22740, 22747, # Rappahannock county
    22551, 22553, 22407, 22408, 22508, 23015, 23024, 22534, # Spotsylvania county
    22471, 22554, 22405, 22556, 22555, 22406, 22412, # Stafford county
    22649, 22630, 22610, # Warren county
    22601 # Winchester city
])


def is_nova_event(event):
    zip_code_str = event.get('properties').get('zip')
    if len(zip_code_str) == 5:
        zip_code = int(zip_code_str)
        if zip_code in NOVA_ZIP_CODES:
            return True
        for zip_range in NOVA_ZIP_CODE_RANGES:
            if zip_code in zip_range:
                return True
    return False


def get_nova_events(all_events):
    nova_events = []
    for event in all_events:
        if is_nova_event(event):
            nova_events.append(event)
    return nova_events


def to_export(event):
    properties = event.get('properties')
    starts_at = properties.get('starts_at')
    starts_at_datetime = datetime.fromisoformat(starts_at.strip('Z'))
    return {
        'id': properties.get('id'),
        'title': properties.get('title'),
        'date': starts_at_datetime.strftime('%Y-%m-%d'),
        'time': starts_at_datetime.strftime('%I:%M %p'),
        'address1': properties.get('address1'),
        'address2': properties.get('address2'),
        'city': properties.get('city'),
        'state': properties.get('state'),
        'zip': properties.get('zip'),
        'attendee_count': properties.get('attendee_count'),
        'max_attendees': properties.get('max_attendees'),
        'link_url': properties.get('link_url'),
    }


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger('sanders-nova-events')

try:
    logger.info("Starting event extraction")
    response = requests.get('https://map.berniesanders.com/static/data/events.geojson.gz')
    response_dict = json.loads(response.content)
    all_events = response_dict.get('features')
    nova_events = get_nova_events(all_events)
    with open('nova-events.csv', 'w', newline='') as csv_file:
        fieldnames = ['id', 'title', 'date', 'time', 'address1', 'address2', 'city', 'state', 'zip', 'attendee_count', 'max_attendees', 'link_url']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for event in nova_events:
            event_export = to_export(event)
            writer.writerow(event_export)
except:
    logger.exception('Service exited with exception')


