import os

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ImageCarouselColumn, ImageCarouselTemplate, URITemplateAction, ButtonsTemplate, MessageTemplateAction, ImageSendMessage
import re
import requests
from requests_html import HTML
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
movieGenre = ["Drama", "Fantasy", "Adventure", "Romance", "Action", "Thriller", "Comedy", "Horror", "Animation"]
movieGenre_link = [
    "https://i.imgur.com/2qEyj2w.png",
    "https://i.imgur.com/nt14vEq.png",
    "https://i.imgur.com/tdwaNAb.png",
    "https://i.imgur.com/jEMaj0P.png",
    "https://i.imgur.com/KiMZsT9.png",
    "https://i.imgur.com/7yP4AA4.png",
    "https://i.imgur.com/oDGfphj.png",
    "https://i.imgur.com/5EFnkRe.png",
    "https://i.imgur.com/DMXCMfK.png"
]


def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

    return "OK"

def send_carousel_message(reply_token, col):
    line_bot_api = LineBotApi(channel_access_token)
    message = TemplateSendMessage(
        alt_text = 'Carousel template',
        template = ImageCarouselTemplate(columns = col)
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def send_button_message(reply_token, title, text, btn, url):
    line_bot_api = LineBotApi(channel_access_token)
    message = TemplateSendMessage(
        alt_text='button template',
        template = ButtonsTemplate(
            title = title,
            text = text,
            thumbnail_image_url = url,
            actions = btn
        )
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def send_image_message(reply_token, url):
    line_bot_api = LineBotApi(channel_access_token)
    message = ImageSendMessage(
        original_content_url = url,
        preview_image_url = url
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"
def fetch(url):
            response = requests.get(url)
            response = requests.get(url, cookies={'over18': '1'})  # ????????? server ????????? 18 ?????? !
            return response

def parse_article_entries(doc):
    html = HTML(html=doc)
    post_entries = html.find('div.r-ent')
    return post_entries
def parse_article_meta(ent):
    ''' Step-3 (revised): parse the metadata in article entry '''
    # ?????????????????????
    meta = {
        'title': ent.find('div.title', first=True).text,
        'push': ent.find('div.nrec', first=True).text,
        'date': ent.find('div.date', first=True).text,
    }

    try:
        # ????????????????????????
        meta['author'] = ent.find('div.author', first=True).text
        meta['link'] = ent.find('div.title > a', first=True).attrs['href']
    except AttributeError:
        # ????????????????????????????????????????????????????????????????????? ?????? ??? ??????
        if '(??????????????????)' in meta['title']:
            # e.g., "(??????????????????) [haudai]"
            match_author = re.search('\[(\w*)\]', meta['title'])
            if match_author:
                meta['author'] = match_author.group(1)
        elif re.search('??????\w*??????', meta['title']):
            # e.g., "(??????cappa??????) <edisonchu> op"
            match_author = re.search('\<(\w*)\>', meta['title'])
            if match_author:
                meta['author'] = match_author.group(1)
    return meta

    # ???????????????????????? dict() ?????? paired data
