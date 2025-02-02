#!/usr/bin/python
# -*- coding: utf-8 -*-

import io
import json
import os
import random
import sys
import warnings

#  plugin import cfg
from skin_configs import skin_configs

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

warnings.filterwarnings("ignore", category=DeprecationWarning)


pythonVer = 2
if sys.version_info.major == 3:
    pythonVer = 3


if pythonVer == 2:
    from urllib2 import urlopen
else:
    from urllib.request import urlopen


MASK_PATH = '/usr/lib/enigma2/python/Plugins/Extensions/KiddaC_Skin_E2sentials/images/mask.png'
SKIN_FOLDER = '/usr/share/enigma2/'

plugin_folder = "/usr/lib/enigma2/python/Plugins/Extensions/KiddaC_Skin_E2sentials"
font_path = os.path.join(plugin_folder, "fonts", "m-plus-rounded-1c-regular.ttf")

sports_channels = [
    "sky-sports-darts",
    "sky-sports-football",
    "sky-sports-cricket",
    "sky-sports-golf",
    "sky-sports-main-event",
    "sky-sports-mix",
    "sky-sports-nfl",
    "sky-sports-premier-league",
    "sky-sports-tennis",
    "tnt-sports-1",
    "tnt-sports-2",
    "tnt-sports-3",
    "tnt-sports-4",
    "sky-sports-f1",
]

osn_hdr = {
    "accept": "*/*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "referer": "https://www.osn.com/en-sa/watch/tv-schedule",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "Host": "images.tv.osn.com"
}

sky_hdr = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate'
}

config_path = "/etc/enigma2/e2sentials/toppicks_config.json"

with open(config_path, 'r') as f:
    cfg_values = json.load(f)

toppickschoice = cfg_values.get('toppickschoice')
toppickschannellogos = cfg_values.get('toppickschannellogos')
toppicksprogrammelogos = cfg_values.get('toppicksprogrammelogos')


def get_text_size(font, text):
    # Check if getbbox() is available (Pillow 8.0.0 and above)
    if hasattr(font, 'getbbox'):
        text_bbox = font.getbbox(text)
        return text_bbox[2], text_bbox[3]  # Width, height from the bbox
    else:
        return font.getsize(text)  # Older versions (PIL or Pillow below 8.0.0)


def download_image(url):
    try:
        response = urlopen(url)
        image_file = io.BytesIO(response.read())
        response.close()
        im = Image.open(image_file)

        if ".png" not in url:
            im = im.convert('RGB')

        return im
    except Exception as e:
        print("Error downloading image: {}".format(e))

        if toppickschoice == "sky":
            if 'background' in url:
                url = url.replace('background', '16-9')
            elif 'cover' in url:
                url = url.replace('cover', '16-9')
            elif '16-9' in url:
                url = url.replace('16-9', 'cover')

            try:
                response = urlopen(url)
                image_file = io.BytesIO(response.read())
                response.close()
                im = Image.open(image_file)

                if ".png" not in url:
                    im = im.convert('RGB')

                return im
            except:
                return None

        return None


def create_background(background, backgroundsize, skin_folder, image_folder, programme_logo_url=None, programme_logo_width=None, programme_logo_x_offset=None, programme_logo_y_offset=None):
    try:
        mask = Image.open(MASK_PATH).convert('RGBA')
        mask = resize_image(mask, backgroundsize)

        plainbg = Image.open('{}{}background.jpg'.format(skin_folder, image_folder)).convert('RGBA')
        background = resize_image(background, backgroundsize)

        background_w, background_h = background.size
        plainbg_w, plainbg_h = plainbg.size

        # Paste the resized background onto the plain background
        plainbg.paste(background, (plainbg_w - background_w, 0), mask)

        # Attempt to download and add the logo, if a URL is provided
        if programme_logo_url:
            try:
                programme_logo = download_image(programme_logo_url)

                if programme_logo:
                    programme_logo = programme_logo.convert('RGBA')

                    original_width, original_height = programme_logo.size

                    if original_height > original_width:
                        new_width = int(programme_logo_width * original_width / original_height)
                        new_height = programme_logo_width
                    else:
                        new_width = programme_logo_width
                        new_height = int(programme_logo_width * original_height / original_width)

                    programme_logo = resize_image(programme_logo, (new_width, new_height))
                    programme_logo_w, programme_logo_h = programme_logo.size
                    programme_logo_x = programme_logo_x_offset
                    programme_logo_y = programme_logo_y_offset

                    # Save the programme logo to disk
                    programme_logo.save(skin_folder + image_folder + "programme_logo.png", quality=85)

                    # Paste the logo onto the background
                    plainbg.paste(programme_logo, (programme_logo_x, programme_logo_y), programme_logo)
            except Exception as e:
                print("Error processing logo: {}".format(e))

        plainbg.save(skin_folder + image_folder + "q.png", quality=85)
        plainbg = plainbg.convert('RGB')
        plainbg.save(skin_folder + image_folder + "hero.jpg", quality=85)

        # transparent background
        hero_bg = Image.new('RGBA', backgroundsize, (0, 0, 0, 0))  # Fully transparent image
        hero_bg_w, hero_bg_h = hero_bg.size

        # Paste the resized background (masked) onto the transparent hero_bg
        hero_bg.paste(background, (hero_bg_w - background_w, 0), mask)
        hero_bg.save(skin_folder + image_folder + "hero.png", quality=85)

    except Exception as e:
        print("Error creating background: {}".format(e))


def resize_image(image, size):
    try:
        return image.resize(size, Image.Resampling.LANCZOS)
    except:
        return image.resize(size, Image.ANTIALIAS)


def crop_image(im, width, height):
    ratio = float(im.size[0]) // im.size[1]

    if width // height < ratio:
        crop_width = int(height * ratio)
        crop_height = height
    elif width // height > ratio:
        crop_width = width
        crop_height = int(width // ratio)
    else:
        crop_width = width
        crop_height = height

    tl_w = (crop_width - width) // 2
    tl_h = (crop_height - height) // 2
    br_w = crop_width - tl_w
    br_h = crop_height - tl_h

    area = (tl_w, tl_h, br_w, br_h)

    im = resize_image(im, (crop_width, crop_height)).crop(area)

    return resize_image(im, (width, height))


def add_channel_logo(im, picon, channel_logo_height, channel_logo_halign, channel_logo_valign, skin_size):
    if toppickschoice == "osn":
        LOGO_SOURCE_FOLDER = "/usr/lib/enigma2/python/Plugins/Extensions/KiddaC_Skin_E2sentials/osn_channel_logos/"
    elif toppickschoice == "sky":
        LOGO_SOURCE_FOLDER = "/usr/lib/enigma2/python/Plugins/Extensions/KiddaC_Skin_E2sentials/sky_channel_logos/"

    try:
        picon = Image.open(LOGO_SOURCE_FOLDER + picon + '.png').convert('RGBA')
    except:
        return im

    hpercent = channel_logo_height / float(picon.height)
    wsize = int(picon.width * hpercent)
    picon = resize_image(picon, (wsize, channel_logo_height))

    img_w, img_h = im.size
    picon_w, picon_h = picon.size
    padding = 4 if skin_size == 1080 else 2

    posx, posy = 0, 0

    # Calculate position based on alignment
    if channel_logo_halign == "left":
        posx = padding
    elif channel_logo_halign == "right":
        posx = img_w - picon_w - padding
    else:  # center
        posx = (img_w - picon_w) // 2

    if channel_logo_valign == "top":
        posy = padding
    elif channel_logo_valign == "bottom":
        posy = img_h - picon_h - padding
    else:  # center
        posy = (img_h - picon_h) // 2

    im.paste(picon, (posx, posy), picon)
    return im


def wrap_text(title, font, max_width):
    words = title.split()
    lines = []
    current_line = []

    for word in words:
        # Test the width of the current line with the next word added
        test_line = " ".join(current_line + [word])
        width, _ = get_text_size(font, test_line)
        if width <= max_width:
            current_line.append(word)
        else:
            # Add the current line to lines and start a new one
            lines.append(" ".join(current_line))
            current_line = [word]

    # Add the last line
    if current_line:
        lines.append(" ".join(current_line))

    return lines


def create_gradient_background(width, height, color_start, color_end):
    gradient_image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(gradient_image)

    for x in range(width):
        for y in range(height):
            # Calculate the ratio for both x and y positions, combining them to form a diagonal gradient
            ratio_x = x / width
            ratio_y = y / height
            ratio = (ratio_x + ratio_y) / 2  # Averaging the ratios from x and y to make the gradient diagonal

            # Interpolate the color based on the ratio
            r = int(color_start[0] * (1 - ratio) + color_end[0] * ratio)
            g = int(color_start[1] * (1 - ratio) + color_end[1] * ratio)
            b = int(color_start[2] * (1 - ratio) + color_end[2] * ratio)

            # Set the color for the pixel at position (x, y)
            draw.point((x, y), fill=(r, g, b))

    return gradient_image


def create_combined_image(im, title, start, duration, width, height, skin_size, font_path=None, logo_height=None):
    # Convert start time to a human-readable format
    start_time = datetime.fromtimestamp(int(start)).strftime('%H:%M')

    # Convert duration to minutes
    duration_mins = int(duration) // 60

    # Append the formatted start time and duration to the title
    formatted_time_duration = "{} - {} {}".format(start_time, duration_mins, "mins")

    # Define the start and end colors for the gradient
    color_start = (11, 99, 186)  # #0b63ba
    color_end = (6, 8, 82)  # #060852

    # Create gradient background
    combined_image = create_gradient_background(width, height, color_start, color_end)

    # Divide the combined height into two halves
    top_height = height // 2
    bottom_height = height // 2

    # Resize the landscape image to fit the top half while maintaining aspect ratio
    im_aspect_ratio = im.width / im.height
    target_aspect_ratio = width / top_height

    if im_aspect_ratio > target_aspect_ratio:
        # Image is wider than the target; scale by width
        new_width = width
        new_height = int(width / im_aspect_ratio)
    else:
        # Image is taller than the target; scale by height
        new_width = int(top_height * im_aspect_ratio)
        new_height = top_height

    resized_image = resize_image(im, (new_width, new_height))

    # Move the top image down by logo_height * 2
    y_offset = logo_height + (8 if skin_size == 1080 else 4)

    # Paste the resized landscape image at the new y_offset (moved down by logo_height * 2)
    x_offset = (width - new_width) // 2
    combined_image.paste(resized_image, (x_offset, y_offset))

    # Draw left-aligned text in the bottom half
    draw = ImageDraw.Draw(combined_image)
    if font_path and os.path.exists(font_path):
        font = ImageFont.truetype(font_path, size=18 if skin_size == 1080 else 12)
    else:
        font = ImageFont.load_default()

    # Custom text-wrapping
    max_width = width - (21 if skin_size == 1080 else 14)  # Padding from the edges

    # Split title and time/duration into two separate parts for wrapping
    lines_title = wrap_text(title, font, max_width)
    lines_time_duration = wrap_text(formatted_time_duration, font, max_width)

    # Calculate vertical position for the wrapped text
    total_text_height = (len(lines_title) + len(lines_time_duration)) * get_text_size(font, "A")[1] + \
                        (len(lines_title) + len(lines_time_duration) - 1) * 5  # Line spacing (no extra space after last line)
    start_y = top_height + (bottom_height - total_text_height) // 2

    # Left-aligned text positioning
    x_offset_text = (12 if skin_size == 1080 else 8)

    # Draw each line of title text
    current_y = start_y
    for line in lines_title:
        draw.text((x_offset_text, current_y), line, fill="white", font=font)
        current_y += get_text_size(font, line)[1] + 5  # Line spacing

    # Draw each line of time/duration text
    for line in lines_time_duration:
        draw.text((x_offset_text, current_y), line, fill="white", font=font)
        current_y += get_text_size(font, line)[1] + 5  # Line spacing

    return combined_image


def main():
    print("Picking images...")
    skin = None

    with open('/etc/enigma2/settings', 'r') as settingsfile:
        for skin_entry in settingsfile:
            if 'config.skin.primary_skin=' in skin_entry:
                skin = skin_entry.replace("config.skin.primary_skin=", "").replace("/skin.xml", "").strip()
                sys.stderr.write(skin + "\n")
                sys.stderr.write("Processing...Please Wait.\n")
                break

    if not skin:
        sys.exit("Skin configuration not found")

    tfile = None

    # Load channel data
    try:
        with open('/etc/enigma2/e2sentials/all_channels_data.json') as json_data:
            tfile = json.load(json_data)
    except Exception as e:
        print("Error loading channel data: {}".format(e))
        sys.stderr.write("No Valid Scrapes. Please run /usr/script/toppicks_skyscraper.sh first. \n")
        sys.exit()

    if not tfile:
        sys.exit("No valid channel data found")

    if skin not in skin_configs:
        print("Skin '{}' not found in configuration".format(skin))
        sys.exit(1)

    config = skin_configs[skin]
    background = config["background"]
    backgroundsize = config["backgroundsize"]
    image_folder = config["image_folder"]
    image_prefix = config["image_prefix"]
    landscape_pics = config["landscape_pics"]
    landscape_size = config["landscape_size"]
    channel_logo_height = config["channel_logo_height"]
    channel_logo_halign = config["channel_logo_halign"]
    channel_logo_valign = config["channel_logo_valign"]
    number_of_images = config["number_of_images"]
    picons = config["picons"]
    portrait_pics = config["portrait_pics"]
    portrait_size = config["portrait_size"]
    skin_folder = config["skin_folder"]
    skin_size = config["skin_size"]
    programme_logo_width = config["programme_logo_width"]
    programme_logo_x_offset = config["programme_logo_x_offset"]
    programme_logo_y_offset = config["programme_logo_y_offset"]

    # Start processing images
    if toppickschoice == "sky":
        if pythonVer == 2:
            now = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        else:
            now = datetime.now().timestamp()

        if tfile == []:
            sys.stderr.write("No Valid Scrapes. Please run /usr/script/toppicks_skyscraper.sh first. \n")
            sys.exit()

        time_upper_bound = int(now) + (2 * 3600)  # 2 hours ahead initially
        tfile = [entry for entry in tfile if int(entry['Start']) + int(entry['Duration']) >= int(now) and int(entry['Start']) <= time_upper_bound]

        # If count of valid entries is less than 10, adjust the upper bound to 3 hours
        if len(tfile) < 40:
            time_upper_bound = int(now) + (5 * 3600)  # Set to 5 hours ahead
            tfile = [entry for entry in tfile if int(entry['Start']) + int(entry['Duration']) >= int(now) and int(entry['Start']) <= time_upper_bound]

    pick = random.sample(range(0, len(tfile) - 1), len(tfile) - 1)

    selectedlist = []
    y = 0
    for x in range(1, number_of_images + 1):
        if x == 1 and background:
            invalid = True
            while invalid:
                if y >= len(tfile) - 1:
                    break

                url = tfile[pick[y]]['Background']
                programme_logo_url = tfile[pick[y]].get('Logo')
                channel = tfile[pick[y]].get('Channel')

                if url:
                    try:
                        im = download_image(url)
                        im.verify()

                        if toppickschoice == "osn":
                            # Only attempt to download the programme_logo if the channel is in the specified list
                            if channel in ["om1", "omc", "opr", "ahd", "ocm", "ofm", "omk", "kdz", "ofh", "obg", "oco", "ost", "oto", "omz", "olh", "oyh", "oya", "oyc"] and toppicksprogrammelogos:
                                create_background(im, backgroundsize, skin_folder, image_folder, programme_logo_url, programme_logo_width, programme_logo_x_offset, programme_logo_y_offset)
                            else:
                                create_background(im, backgroundsize, skin_folder, image_folder)
                        else:
                            create_background(im, backgroundsize, skin_folder, image_folder)

                        invalid = False

                    except Exception as e:
                        print("Error processing background image: Using next image {}".format(e))
                        y += 1
                        if y >= len(tfile) - 1:
                            break
                else:
                    y += 1
                    if y >= len(tfile) - 1:
                        break

        if portrait_pics and x in portrait_pics:
            invalid = True
            while invalid:
                if y >= len(tfile) - 1:
                    break

                if str(tfile[pick[y]]['Title']) in selectedlist:
                    y += 1
                    if y >= len(tfile) - 1:
                        break
                    else:
                        continue

                picon = tfile[pick[y]]['Picon']
                width, height = portrait_size

                try:
                    if any(keyword in picon for keyword in sports_channels):  # Check if the Picon matches sports channels
                        url = tfile[pick[y]]['Landscape'].replace('500', str(portrait_size[1] * 2))

                        im = download_image(url)
                        if im is None:
                            y += 1
                            if y >= len(tfile) - 1:
                                break
                            continue
                        im.verify()

                        combined_image = create_combined_image(im, tfile[pick[y]]['Title'], tfile[pick[y]]['Start'], tfile[pick[y]]['Duration'], width, height, skin_size, font_path, channel_logo_height)

                        if toppickschannellogos and x in picons:
                            combined_image = add_channel_logo(combined_image, picon, channel_logo_height, channel_logo_halign, channel_logo_valign, skin_size)
                        combined_image.save(skin_folder + image_folder + image_prefix + str(x) + ".jpg", quality=100)
                        invalid = False
                        selectedlist.append(str(tfile[pick[y]]['Title']))
                    else:
                        url = tfile[pick[y]]['Cover'].replace('500', str(portrait_size[1] * 2))
                        im = download_image(url)
                        if im is None:
                            y += 1
                            if y >= len(tfile) - 1:
                                break
                            continue
                        im.verify()
                        im = crop_image(im, width, height)
                        if toppickschannellogos and x in picons:
                            im = add_channel_logo(im, picon, channel_logo_height, channel_logo_halign, channel_logo_valign, skin_size)
                        im.save(skin_folder + image_folder + image_prefix + str(x) + ".jpg", quality=100)

                        invalid = False
                        selectedlist.append(str(tfile[pick[y]]['Title']))
                except Exception as e:
                    print("Error processing portrait image: Using next one {}".format(e))
                    y += 1
                    if y >= len(tfile) - 1:
                        break

            y += 1
            if y > len(tfile) - 1:
                break

        if landscape_pics and x in landscape_pics:
            invalid = True
            while invalid:
                if y >= len(tfile) - 1:
                    break

                if str(tfile[pick[y]]['Title']) in selectedlist:
                    y += 1
                    if y >= len(tfile) - 1:
                        break
                    else:
                        continue

                picon = tfile[pick[y]]['Picon']
                width, height = landscape_size
                url = tfile[pick[y]]['Landscape'].replace('500', str(landscape_size[0] * 2))

                try:

                    im = download_image(url)
                    if im is None:
                        y += 1
                        if y >= len(tfile) - 1:
                            break
                        continue
                    im.verify()
                    im = crop_image(im, width, height)

                    if toppickschannellogos and x in picons:
                        im = add_channel_logo(im, picon, channel_logo_height, channel_logo_halign, channel_logo_valign, skin_size)
                    im.save(skin_folder + image_folder + image_prefix + str(x) + ".jpg", quality=100)

                    invalid = False
                    selectedlist.append(str(tfile[pick[y]]['Title']))

                except Exception as e:
                    print("Error processing landscape image: Using next one {}".format(e))
                    y += 1
                    if y >= len(tfile) - 1:
                        break

            y += 1
            if y > len(tfile) - 1:
                break

    return


if __name__ == "__main__":
    main()
