from urllib.request import pathname2url
import requests
import sys


def generate_auth_hash(url, token, private):
    from hashlib import sha1
    from hashlib import sha256
    from urllib.parse import urlparse
    import hmac
    import random

    nonce = sha1(str(random.random()).encode("utf-8")).hexdigest()
    uri = urlparse(url).path.rstrip('/')
    msg = uri + ':' + nonce + ':' + private
    the_hash = hmac.new(bytes(token.encode("utf-8")), msg.encode("utf-8"), sha256)
    auth_hash = nonce + ':' + the_hash.hexdigest()

    return auth_hash


def get_installation_file_url(base_url, sugar_flavor, sugar_version, token, private):
    sugar_path = pathname2url('/{}/{}/Installers'.format(sugar_flavor, sugar_version).encode('utf-8'))
    url = base_url + '/ls' + sugar_path

    data = {}
    data['options'] = 'al'
    data['auth_token'] = token
    data['auth_hash'] = generate_auth_hash(url, token, private)
    resp = requests.post(url=url, data=data, stream=False, headers=None)
    # print('URL: {}'.format(url))
    # print('STATUS CODE: {}'.format(resp.status_code))
    # print('RESPONSE: {}'.format(resp.text))
    # print('HEADERS: {}'.format(resp.headers))

    if resp.status_code is not 200:
        raise Exception("Couldn't connect to Pydio, code was: {}".format(resp.status_code))

    xml_tree = parse_xml_response(resp.text)

    return find_installable_zip(xml_tree, sugar_path)


def get_raw_file(base_url, file_path, token, private, output_file):
    url = base_url + '/download' + pathname2url(file_path.encode('utf-8'))
    data = {}
    data['auth_token'] = token
    data['auth_hash'] = generate_auth_hash(url, token, private)
    resp = requests.post(url=url, data=data, stream=True, headers=None)
    if resp.status_code is not 200:
        raise Exception("Couldn't connect to Pydio, code was: {}".format(resp.status_code))

    with open(output_file, 'wb') as fd:
        for chunk in resp.iter_content(1024 * 8):
            fd.write(chunk)


def parse_xml_response(raw_xml):
    import xml.etree.ElementTree

    try:
        return xml.etree.ElementTree.fromstring(raw_xml)
    except xml.etree.ElementTree.ParseError as e:
        print("Can't parse the XML: {}".format(e))
        print('RESPONSE: {}'.format(raw_xml))
        sys.exit(1)


def find_installable_zip(xml_tree, sugar_path):
    file_name = None
    for files in xml_tree:
        attributes = files.attrib
        if 'type' in attributes.keys() and attributes['type'] == 'ERROR':
            raise IOError("Couldn't open the folder {}".format(sugar_path))

        # check how many files I have
        if len(xml_tree) is 1 or attributes['filename'][-4:] == '.zip':
            file_name = attributes['filename']
            break

    if file_name is None:
        raise IOError("Couldn't find an installable ZIP")
        exit(1)

    return file_name
