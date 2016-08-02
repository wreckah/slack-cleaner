from collections import defaultdict
from datetime import datetime
from optparse import OptionParser
from os import mkdir, path
from time import time
import logging
import requests
import sys

_url = None
_path = None
_token = None
_user_id = None
_days = None
_is_admin = False

_cache = {}

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler())
_logger.level = logging.INFO


def req(method, params=None):
    params = params or {}
    params['token'] = _token
    resp = requests.post(
        (_url or 'https://slack.com/') + 'api/' + method, data=params
    )
    if resp.status_code != 200:
        raise Exception(resp.content)
    return resp.json()


def download(url):
    headers = {'Authorization': 'Bearer ' + _token}
    resp = requests.post(url, headers=headers)
    return resp.content


def delete(file_id, filename):
    resp = req('files.delete', {'file': file_id})
    if not resp['ok']:
        _logger.warning('Cannot delete file %s: %s', filename, resp)
    else:
        _logger.info('Delete file %s', filename)
    return resp


def get_channel(channel_id, create_dir=True):
    if channel_id not in _cache:
        params = {'channel': channel_id}
        _cache[channel_id] = req('channels.info', params)['channel']
        if create_dir:
            mkdir(_cache[channel_id]['name'])
    return _cache[channel_id]


def get_group(group_id, create_dir=True):
    if group_id not in _cache:
        params = {'channel': group_id}
        _cache[group_id] = req('groups.info', params)['group']
        if create_dir:
            mkdir(_cache[group_id]['name'])
    return _cache[group_id]


def get_user(user_id, create_dir=True):
    if user_id not in _cache:
        params = {'user': user_id}
        _cache[user_id] = req('users.info', params)['user']
        if create_dir:
            mkdir(_cache[user_id]['name'])
    return _cache[user_id]


def mkdir(name):
    if not _path or path.isdir(_path + name):
        return
    mkdir(_path + name)


def store(body, filename, directory):
    if not _path:
        return
    _logger.info('Store to %s', directory)
    with open(_path + directory + '/' + filename, 'wb') as f:
        f.write(body)


def process_file(f):
    created = datetime.fromtimestamp(f['created']).strftime('%Y-%m-%d %H:%M:%S')
    _logger.info('Process file %s, created %s', f['name'], created)
    body = download(f['url_private_download'])
    if f.get('channels'):
        for channel in f['channels']:
            name = get_channel(channel)['name']
            store(body, f['name'], name)

    if f.get('groups'):
        for group in f['groups']:
            name = get_group(group)['name']
            store(body, f['name'], name)

    if not f.get('channels') and not f.get('groups'):
        name = get_user(f['user'])['name']
        store(body, f['name'], name)


def get_stat():
    page = 1
    pages = None
    total = 0
    cnt = 0
    stat = defaultdict(int)
    top10 = []
    while pages is None or page <= pages:
        resp = req('files.list', {})
        pages = resp['paging']['pages']
        for f in resp['files']:
            if f['channels']:
                who = '#' + get_channel(f['channels'][0], False)['name']
            elif f['groups']:
                who = '#' + get_group(f['groups'][0], False)['name']
            else:
                who = '@' + get_user(f['user'], False)['name']
            stat[who] += f['size']
            total += f['size']
            cnt += 1
        page += 1
    sys.stdout.write('Total files: %s\n' % cnt)
    sys.stdout.write('Total bytes: %s\n' % total)
    for item in sorted(stat.items(), key=lambda x: x[1]):
        sys.stdout.write('  %s: %s bytes\n' % item)


def process():
    ts_to = time() - _days * 3600 * 24
    params = {'ts_to': ts_to, 'count': 100}
    if not _is_admin:
        params['user'] = _user_id
    size = 0
    cnt = 0

    while True:
        files = req('files.list', params)['files']
        if not files:
            break
        for f in files:
            if not f['is_external']:
                process_file(f)
            delete(f['id'], f['name'])
            cnt += 1
            size += f['size']

    _logger.info(
        'Deleted %s files older than %s days, cleaned up %s bytes',
        cnt, _days, size
    )


def main():
    global _token, _url, _path, _user_id, _days, _is_admin
    parser = OptionParser()

    parser.add_option(
        '-s', '--store', dest='store', help='Store deleted files to this path'
    )
    parser.add_option(
        '-d', '--days',
        dest='days', default=365, type='int',
        help='Skip (do not delete) files newer than this number of days'
    )

    options, args = parser.parse_args()
    l = len(args)
    if not l:
        sys.stderr.write('\nAccess token is required as the first argument\n')
        sys.exit(1)
    _token = args[0]
    _path = options.store
    _days = options.days
    if _path:
        _path = _path.rstrip('/') + '/'

    auth = req('auth.test')
    if not auth['ok']:
        sys.stderr.write('Bad token:\n%s\n' % auth)
        sys.exit(1)

    _url = auth['url']
    _user_id = auth['user_id']
    _logger.info('Clean up files of user %s', auth['user'])

    user = req('users.info', {'user': _user_id})
    _is_admin = user['user']['is_admin']

    process()


if __name__ == '__main__':
    main()
