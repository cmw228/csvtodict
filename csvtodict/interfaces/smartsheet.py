import re
import json
import requests

from collections import OrderedDict
from ..csvtodict import convert

def _getSmartsheet(sid):
    """'sid' is a smartsheet id. Creates a http request object that
    when made, returns a json representation of the
    smartsheet with the given smartsheet id
    """
    # Authentication header.
    headers = {"Authorization": "Bearer 476bhdytlqjqx0si77ygdskitm"}
    url = 'https://api.smartsheet.com/2.0/sheets/%s' % sid

    # Restful API URI for requesting an entire smartsheet.
    return requests.get(url, headers=headers).json()

def convertSmartsheet(sid, delimiter="."):

    smartsheet = _getSmartsheet(sid)

    # Extracts headers from the first row of smartsheet.
    headers = [h['displayValue'] for h in smartsheet['rows'][0]['cells']]
    data = {}
    index = 1

    while True:
        try:
            #make list of tuples to retain order
            doc = []

            # Iterates through both the headers of the smartsheet,
            # and the cells of a row.
            first = True
            for h, cell in zip(headers, smartsheet['rows'][index]['cells']):
                if first:
                    if 'displayValue' in cell:
                        primary_key = cell['displayValue']
                    elif 'value' in cell:
                        primary_key = cell['value']

                    first = False

                # Only appends tuple (header, cell data) to
                # doc when there is a value.
                if 'displayValue' in cell and cell['displayValue'] != "null":
                    v = re.sub(u"(\u2018|\u2019)", "'", cell['displayValue'])
                    doc.append( (h, v) )
                elif 'value' in cell and cell['value'] != "null":
                    #doc[h] = re.sub(u"(\u2018|\u2019)", "'", cell['value'])
                    v = re.sub(u"(\u2018|\u2019)", "'", cell['value'])
                    doc.append( (h, v) )

            doc = OrderedDict(doc)
            doc = convert(doc, delimiter)

            data[primary_key] = doc
            index += 1

        # Breaks from the inifinte loop when there are no more
        # rows.
        except IndexError:
            break

    #with open('data/' + sid + '.json', 'w') as data_file:
    #    data_file.write(json.dumps(data))

    return data

