from transitions.extensions import GraphMachine
from linebot.models import *
from linebot import (
    LineBotApi, WebhookHandler
)
import pandas as pd
# from utils import send_text_message, send_carousel_message, send_button_message, send_image_message
from utils import *
import random
from datetime import datetime
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
line_bot_api = LineBotApi(channel_access_token)
MOVIE_TITLE = " "
GENRE = " "
RECOMMEND_LIST=" "
MOVIE_ID = 999
class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_functions(self, event): #要推薦電影or讓用戶查詢
        text = event.message.text
        if text == "開始測試" or text == "回到首頁":
            return True
        else:
            return False
    def on_enter_functions(self, event):
        title = '請先選擇操作內容'
        text = '您是要『我推薦電影』還是『查詢電影評價』呢？'
        btn = [
            MessageTemplateAction(
                label = '電影推薦',
                text ='電影推薦'
            ),
            MessageTemplateAction(
                label = '電影查詢',
                text = '電影查詢'
            ),
        ]
        url = 'https://i.imgur.com/y6yIoJz.jpg'
        send_button_message(event.reply_token, title, text, btn, url)

    def is_going_to_suggestions(self, event):
        text = event.message.text
        return text == "電影推薦"
    def on_enter_suggestions(self, event):
        image_carousel_template_message = TemplateSendMessage(
             alt_text='免費教學影片',
             template=ImageCarouselTemplate(
                 columns=[
                     ImageCarouselColumn(
                         image_url= movieGenre_link[0],
                         action = MessageTemplateAction(
                            label = movieGenre[0],
                            text =movieGenre[0]
                        )
                     ),
                     ImageCarouselColumn(
                         image_url= movieGenre_link[1],
                         action = MessageTemplateAction(
                            label = movieGenre[1],
                            text =movieGenre[1]
                        )
                     ),
                     ImageCarouselColumn(
                         image_url= movieGenre_link[2],
                         action = MessageTemplateAction(
                            label = movieGenre[2],
                            text =movieGenre[2]
                        )
                     ),
                     ImageCarouselColumn(
                         image_url= movieGenre_link[3],
                         action = MessageTemplateAction(
                            label = movieGenre[3],
                            text =movieGenre[3]
                        )
                     ),
                     ImageCarouselColumn(
                         image_url= movieGenre_link[4],
                         action = MessageTemplateAction(
                            label = movieGenre[4],
                            text =movieGenre[4]
                        )
                     ),
                     ImageCarouselColumn(
                         image_url= movieGenre_link[5],
                         action = MessageTemplateAction(
                            label = movieGenre[5],
                            text =movieGenre[5]
                        )
                     ),
                     ImageCarouselColumn(
                         image_url= movieGenre_link[6],
                         action = MessageTemplateAction(
                            label = movieGenre[6],
                            text =movieGenre[6]
                         )
                    ),
                     ImageCarouselColumn(
                         image_url= movieGenre_link[7],
                         action = MessageTemplateAction(
                            label = movieGenre[7],
                            text =movieGenre[7]
                        )
                     ),
                     ImageCarouselColumn(
                         image_url= movieGenre_link[8],
                         action = MessageTemplateAction(
                            label = movieGenre[8],
                            text =movieGenre[8]
                        )
                     )
                ]
             )
         )
        line_bot_api.reply_message(event.reply_token, image_carousel_template_message)

    def is_going_to_search(self, event):
        text = event.message.text
        return text == "電影查詢"
    def on_enter_search(self, event):
        token = event.reply_token
        send_text_message(token, '請輸入『幫我掃雷』 + 『電影名稱\nex: 幫我掃雷 『鋒迴路轉』')
        # send_text_message(token, 'ex: 幫我掃雷 鋒迴路轉')

    def is_going_to_searchCal(self, event):
        global MOVIE_TITLE
        text = event.message.text
        if "幫我掃雷" in text:
            MOVIE_TITLE = text[5:]
            print(MOVIE_TITLE)
            return True
        else:
            return False
    def on_enter_searchCal(self, event):
        token = event.reply_token
        global MOVIE_TITLE
        return_text = "電影 "+  MOVIE_TITLE + "完成搜尋\n"
        negative = 0
        positive = 0
        common = 0
        # send_text_message(token, return_text)
        search_endpoint_url = 'https://www.ptt.cc/bbs/movie/search'
        for i in range(10):
            p = i + 1
            resp = requests.get(search_endpoint_url, params={'q': MOVIE_TITLE, 'page' : p})
            post_entries = parse_article_entries(resp.text)  # [沿用]
            metadata = [parse_article_meta(entry) for entry in post_entries]  # [沿用]
            for entry in post_entries:
                meta = parse_article_meta(entry)
                if "負雷" in meta['title'] and "Re:" not in meta['title'] or "負無雷" in meta['title'] and "Re:" not in meta['title']:
                    negative += 1
                elif "好雷" in meta['title'] and "Re:" not in meta['title'] or "好無雷" in meta['title'] and "Re:" not in meta['title']:
                    positive += 1
                elif "普雷" in meta['title'] and "Re:" not in meta['title'] or "普無雷" in meta['title'] and "Re:" not in meta['title']:
                    common += 1
        total = positive + negative + common
        if total != 0:
            return_text = return_text+ "[好雷]有" + str(positive) + "篇" + "共佔" + str(float(positive)/total * 100)[:5] + "%\n"
            return_text = return_text+ "[普雷]有" + str(common) + "篇" + "共佔" + str(float(common)/total * 100)[:5] + "%\n"
            return_text = return_text+ "[負雷]有" + str(negative) + "篇" + "共佔" + str(float(negative)/total * 100)[:5] + "%\n"
        else:
            return_text = return_text + "沒有搜尋到 可以換換關鍵字\n"
        return_text += "輸入『繼續查詢』查詢下一部電影\n輸入『回到首頁』重新開始"
        send_text_message(token, return_text)
    def is_going_to_suggestionGenre(self, event):
        global GENRE
        text = event.message.text
        for genre in movieGenre:
            if text == genre:
                GENRE = text
                return True
        if text == "都看過了":
            return True
        else:
            return False
    def on_enter_suggestionGenre(self, event):
        random.seed(datetime.now())
        global GENRE
        global RECOMMEND_LIST
        movie_list = pd.read_csv('imdb_top_250.csv')
        movie_list.rename(columns={'Unnamed: 0': 'ID'}, inplace=True)
        return_text = "幫您推薦:\n"
        count = 0
        for j in range(100):
            i = random.randint(0,249)
            if count >= 5:
                break
            if GENRE in movie_list['Genre'][i]:
                if movie_list['Title'][i] in return_text:
                    continue
                return_text = return_text + movie_list['Title'][i]
                return_text = return_text + "\n"
                count += 1
        return_text = return_text + "輸入『都看過了』重新搜尋\n"
        return_text = return_text + "輸入『我想看 電影名稱』查看細節"
        return_text = return_text + "\n輸入『回到電影推薦』查看其他電影推薦"
        RECOMMEND_LIST = return_text
        send_text_message(event.reply_token, return_text)
    def is_going_to_suggestionDetail(sefl, event):
        global MOVIE_TITLE
        text = event.message.text
        if "我想看" in text:
            MOVIE_TITLE = text[4:]
            return True
        else:
            return False
    def on_enter_suggestionDetail(self, event):
        global MOVIE_TITLE
        global RECOMMEND_LIST
        movie_list = pd.read_csv('imdb_top_250.csv')
        movie_list.rename(columns={'Unnamed: 0': 'ID'}, inplace=True)
        return_text = " "
        flag = 0
        for i in range(250):
            if MOVIE_TITLE == movie_list['Title'][i]:
                return_text = "年份: " + str(movie_list['Year'][i])
                return_text = return_text + "\n片長: " + str(movie_list['Duration'][i])
                return_text = return_text + "\n導演: " + str(movie_list['Director'][i])
                return_text = return_text + "\n評分: " + str(movie_list['IMDB rating'][i])
                return_text = return_text + "\n連結: " + str(movie_list['IMDB link'][i])
                flag = 1
                break
        if flag == 0:
            return_text = return_text + "沒有搜尋到 可以換換關鍵字"
        else:
            return_text = return_text + "\n輸入『回到推薦清單』查看其他電影內容"
            return_text = return_text + "\n輸入『回到電影推薦』查看其他電影推薦"
        send_text_message(event.reply_token, return_text)
    def is_going_to_recommendList(self, event):
        text = event.message.text
        return text=="回到推薦清單"
    def on_enter_recommendList(self, event):
        global RECOMMEND_LIST
        send_text_message(event.reply_token, RECOMMEND_LIST)
    def is_going_back_to_suggestions(sefl, event):
        text = event.message.text
        return text=="回到電影推薦"
    def is_going_back_from_searchCal(self, event):
        text = event.message.text
        return text=="繼續查詢"
    def is_going_to_fsm(self, event):
        text = event.message.text
        return text == "fsm"
    def on_enter_fsm(self, event):
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url='https://i.imgur.com/ZFTbSUm.png', preview_image_url='https://i.imgur.com/ZFTbSUm.png'))
    # def on_enter_state1(self, event):
    #     print("I'm entering state1")

    #     reply_token = event.reply_token
    #     send_text_message(reply_token, "Trigger state1")
    #     self.go_back()
    def on_exit_state1(self):
        print("Leaving state1")

    def on_enter_state2(self, event):
        print("I'm entering state2")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state2")
        self.go_back()

    def on_exit_state2(self):
        print("Leaving state2")
