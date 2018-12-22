import time


ORIGIN = 'http'
PROTOCOL = 'https'

def getIP(param):
    return {
        'http': '',
        'https': '',
    }


def getIPWithoutLogin(param):
    return {
        'http': '',
        'https': '',
    }


def generate_rnd():
    # 1544778269.439094
    # 1544778516846
    # 1544605567123
    ori = time.time()
    return str(int(ori*1000))


def url_filter(url):

    return ':'.join([PROTOCOL, url]) if PROTOCOL not in url and ORIGIN not in url else url


def url_simplify(url):
    if url:
        index = url.find('?')
        if index > 0:
            return url[:index]
    return url
