#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import json
import re
import sys
import warnings

# from .plugin import cfg
from osn_channel_configs import osn_channel_configs
from sky_channel_configs import sky_channel_configs

from twisted.internet import reactor
from twisted.web.client import Agent, readBody
from twisted.internet.defer import DeferredList
from twisted.web.http_headers import Headers

warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    from twisted.web.client import BrowserLikePolicyForHTTPS
    contextFactory = BrowserLikePolicyForHTTPS()
except ImportError:
    from twisted.web.client import WebClientContextFactory
    contextFactory = WebClientContextFactory()

agent = Agent(reactor, contextFactory=contextFactory)

today = datetime.date.today().strftime('%Y%m%d')
tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y%m%d')

config_path = "/etc/enigma2/e2sentials/toppicks_config.json"

with open(config_path, 'r') as f:
    cfg_values = json.load(f)

toppickschoice = cfg_values.get('toppickschoice')
toppickschannellogos = cfg_values.get('toppickschannellogos')
toppicksprogrammelogos = cfg_values.get('toppicksprogrammelogos')
toppicks_osn_movies = cfg_values.get('toppicks_osn_movies')
toppicks_osn_general = cfg_values.get('toppicks_osn_general')
toppicks_osn_lifestyle = cfg_values.get('toppicks_osn_lifestyle')
toppicks_osn_arabic = cfg_values.get('toppicks_osn_arabic')
toppicks_osn_kids = cfg_values.get('toppicks_osn_kids')
toppicks_osn_sky_lifestyle = cfg_values.get('toppicks_osn_sky_lifestyle')
toppicks_osn_sky_kids = cfg_values.get('toppicks_osn_sky_kids')
toppicks_sky_documentaries = cfg_values.get('toppicks_sky_documentaries')
toppicks_sky_crime = cfg_values.get('toppicks_sky_crime')
toppicks_sky_nature = cfg_values.get('toppicks_sky_nature')
toppicks_sky_kids = cfg_values.get('toppicks_sky_kids')
toppicks_sky_cinema = cfg_values.get('toppicks_sky_cinema')
toppicks_sky_sports = cfg_values.get('toppicks_sky_sports')
toppicks_sky_entertainment = cfg_values.get('toppicks_sky_entertainment')


osn_hdr = {
    "accept": "*/*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "referer": "https://www.osn.com/en-sa/watch/tv-schedule",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}

sky_hdr = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate'
}


def main():
    global tilelist, allchannels
    tilelist = []
    allchannels = {}
    try:
        if toppickschoice == "osn":
            osn_setup()
        elif toppickschoice == "sky":
            sky_setup()
    except Exception as e:
        print(e)


def sky_setup():
    global allchannels  # Declare global to modify the global variable

    choice = []

    sky_options = [
        (toppicks_sky_documentaries, "documentaries"),
        (toppicks_sky_crime, "crime"),
        (toppicks_sky_nature, "nature"),
        (toppicks_sky_kids, "kids"),
        (toppicks_sky_cinema, "sky_cinema"),
        (toppicks_sky_sports, "sports"),
        (toppicks_sky_entertainment, "entertainment"),
    ]

    choice.extend(sky_channel_configs[key] for condition, key in sky_options if condition)

    allchannels = {key: val for d in choice for key, val in d.items()}

    urls = []

    channel_ids = list(allchannels.keys())  # Extract all channel IDs

    # Split the channel IDs into chunks of 10
    for i in range(0, len(channel_ids), 10):

        chunk = channel_ids[i:i + 10]
        ids_chunk = ",".join(chunk)

        # Append the URLs for today and tomorrow for this chunk
        urls.append('https://awk.epgsky.com/hawk/linear/schedule/{}/{}'.format(today, ids_chunk))
        urls.append('https://awk.epgsky.com/hawk/linear/schedule/{}/{}'.format(tomorrow, ids_chunk))

    scraper(urls)


def osn_setup():
    choice = []

    osn_options = [
        (toppicks_osn_movies, "osn_movies"),
        (toppicks_osn_general, "osn_general"),
        (toppicks_osn_lifestyle, "osn_lifestyle"),
        (toppicks_osn_arabic, "osn_arabic"),
        (toppicks_osn_kids, "osn_kids"),
        (toppicks_osn_sky_lifestyle, "osn_sky_lifestyle"),
        (toppicks_osn_sky_kids, "osn_sky_kids"),
    ]

    choice.extend(osn_channel_configs[key] for condition, key in osn_options if condition)

    allchannels = {key: val for d in choice for key, val in d.items()}

    urls = []

    url_template = "https://www.osn.com/api/channelsguidehighlights.ashx?channelcode={channel}&culture=en-US&country=SA"

    for channel_code in allchannels.keys():
        url = url_template.format(channel=channel_code)
        urls.append(url)

    scraper(urls)


def scraper(urls):
    sys.stderr.write("Scraping channels please wait:" + "\n")
    deferreds = [fetch_url(agent, url) for url in urls]
    dl = DeferredList(deferreds)
    dl.addCallback(all_downloads_complete)
    reactor.run()


def fetch_url(agent, url):
    if toppickschoice == "sky":
        headers = sky_hdr
    elif toppickschoice == "osn":
        headers = osn_hdr

    twisted_headers = Headers({
        key.encode(): [value.encode()] for key, value in headers.items()
    })

    d = agent.request(b'GET', url.encode(), twisted_headers)
    d.addCallback(handle_response, url)
    d.addErrback(error, url)
    return d


def handle_response(response, url):
    if response.code != 200:
        print("Error: Non-200 status code {} for URL: {}".format(response.code, url))
        return None

    d = readBody(response)
    if toppickschoice == "sky":
        d.addCallback(lambda body: process_sky_json(body, url))
    elif toppickschoice == "osn":
        d.addCallback(lambda body: process_osn_json(body, url))
    return d


def process_sky_json(body, url):
    global allchannels
    global tilelist
    try:
        try:
            json_data = json.loads(body.decode('utf-8'))
        except:
            json_data = json.loads(body)

        if 'schedule' in json_data:
            for channel in json_data['schedule']:
                sid = str(channel.get('sid', ''))
                if sid and 'events' in channel:
                    for event in channel['events']:
                        try:
                            e_start = str(event['st'])
                            e_duration = str(event['d'])
                            e_uuid = str(event['programmeuuid'])
                            e_title = str(event['t'])
                        except:
                            continue

                        if e_uuid and e_start and e_duration:
                            e_channel = allchannels.get(sid, "")

                            tilevalues = {
                                'UUID': e_uuid,
                                'Title': e_title,
                                'Picon': e_channel,
                                'Background': "https://images.metadata.sky.com/pd-image/{}/background/1280".format(e_uuid),
                                'Landscape': "https://images.metadata.sky.com/pd-image/{}/16-9/500".format(e_uuid),
                                'Cover': "https://images.metadata.sky.com/pd-image/{}/cover/500".format(e_uuid),
                                'Start': e_start,
                                'Duration': e_duration
                            }

                            tilelist.append(tilevalues.copy())

    except Exception as e:
        print("Error parsing JSON from {}: {}".format(url, e))


def process_osn_json(body, url):
    global allchannels
    global tilelist
    try:
        try:
            json_data = json.loads(body.decode('utf-8'))
        except:
            json_data = json.loads(body)

        for item in json_data:
            portrait_url = item.get("i", "")
            landscape_url = ""
            background_url = ""
            logo_url = ""

            match = re.search(r"channelcode=([^&]+)", url)
            channel = match.group(1)
            picon = channel.upper()

            # Keep the query string but replace Resize values in portrait URL
            portrait_url = re.sub(r"Resize=\([^)]*\)", "Resize=(500)", portrait_url)

            if '_pp' not in portrait_url and '_PP' not in portrait_url:

                # Replace "/portrait/" with "/landscape/" and "_PTT" with "_LC" for the landscape URL
                landscape_url = re.sub(r"_PTT\d*", "_LC", portrait_url.replace("/portrait/", "/landscape/"))

                # If the landscape URL contains 'series', adjust the Logo URL format
                logo_url = landscape_url.replace("_LC", "_TT").replace("/landscape/", "/titleimage/").replace(".jpg", ".png")
                if "series" in landscape_url:
                    parts = landscape_url.split('/')
                    series_id = parts[6]  # The ID before the extra part (like 19714)
                    logo_url = "https://images.tv.osn.com/colossus/images/series/" + series_id + "/titleimage/" + series_id + "_TT.png?im=Resize=(500)"

                # Generate the background URL based on the landscape URL with Resize=(1280)
                background_url = landscape_url.replace("Resize=(500)", "Resize=(1280)")

            entry = {
                "Title": item.get("t"),
                "Cover": portrait_url,
                "Landscape": landscape_url,
                "Background": background_url,
                "Logo": logo_url,
                "Channel": channel,
                "Picon": picon,
            }
            tilelist.append(entry)
    except Exception as e:
        print("Error parsing JSON from {}: {}".format(url, e))


def error(response, url):
    print("Error fetching {}: {}".format(url, response))


def all_downloads_complete(results):
    # print("All_downloads_complete")
    global tilelist
    filename = '/etc/enigma2/e2sentials/all_channels_data.json'
    with open(filename, 'w') as f:
        json.dump(tilelist, f, indent=4)

    reactor.stop()

    import picker
    picker.main()

    return


if __name__ == "__main__":
    main()
