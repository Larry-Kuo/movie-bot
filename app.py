import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()


machine = TocMachine(
    states=["user", "functions","search","searchCal", "suggestions", "suggestionGenre","suggestionDetail", "recommendList","searchSuggestion" ,"fsm"],
    transitions=[
        {"trigger": "advance", "source": "user", "dest": "fsm", "conditions": "is_going_to_fsm",},
        {"trigger": "advance", "source": "fsm", "dest": "functions", "conditions": "is_going_to_functions",},
        {"trigger": "advance", "source": "user", "dest": "functions", "conditions": "is_going_to_functions",},
        {"trigger": "advance", "source": "user", "dest": "state2", "conditions": "is_going_to_state2",},
        {"trigger": "advance", "source": "functions", "dest": "suggestions", "conditions": "is_going_to_suggestions",},
        {"trigger": "advance", "source": "suggestions", "dest": "suggestionGenre", "conditions": "is_going_to_suggestionGenre",},
        {"trigger": "advance", "source": "suggestionGenre", "dest": "suggestionDetail", "conditions": "is_going_to_suggestionDetail",},
        {"trigger": "advance", "source": "suggestionGenre", "dest": "suggestionGenre", "conditions": "is_going_to_suggestionGenre",},
        {"trigger": "advance", "source": "suggestionDetail", "dest": "suggestions", "conditions": "is_going_back_to_suggestions",},
        {"trigger": "advance", "source": "functions", "dest": "search", "conditions": "is_going_to_search",},
        {"trigger": "advance", "source": "search", "dest": "searchCal", "conditions": "is_going_to_searchCal",},
        {"trigger": "advance", "source": "searchCal", "dest": "search", "conditions": "is_going_back_from_searchCal",},
        {"trigger": "advance", "source": "suggestionDetail", "dest": "recommendList", "conditions": "is_going_to_recommendList",},
        {"trigger": "advance", "source": "recommendList", "dest": "suggestions", "conditions": "is_going_to_suggestionGenre",},
        {"trigger": "advance", "source": "recommendList", "dest": "suggestionDetails", "conditions": "is_going_to_suggestionDetail",},

        {"trigger": "advance", "source": "searchCal", "dest": "functions", "conditions": "is_going_to_functions",},
        {"trigger": "advance", "source": "recommendList", "dest": "functions", "conditions": "is_going_to_functions",},
        {"trigger": "advance", "source": "suggestions", "dest": "functions", "conditions": "is_going_to_functions",},
        {"trigger": "advance", "source": "suggestionGenre", "dest": "functions", "conditions": "is_going_to_functions",},
        {"trigger": "advance", "source": "suggestionDetail", "dest": "functions", "conditions": "is_going_to_functions",},
        {"trigger": "advance", "source": "suggestionDetail", "dest": "recommendList", "conditions": "is_going_to_recommendList",},
        {"trigger": "advance", "source": "suggestionDetail", "dest": "suggestions", "conditions": "is_going_back_to_suggestions",},
        {"trigger": "go_back", "source": ["functions", "state2", "suggestions", "suggestionGenre","suggestionDetail", "functions", "search", "searchCal", "recommendList, searchSuggestion"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        # print(f"\nFSM STATE: {machine.state}")
        # print(f"REQUEST BODY: \n{body}")
        
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "請按照指示操作")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)