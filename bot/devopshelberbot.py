import logging
import datetime
import configparser
import argparse
import inspect
from queue import Empty
import re
import shlex
from mwt import MWT
from dbhelper import DBHelper
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from telegram.ext import MessageHandler, Filters, CommandHandler, Updater

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

db = DBHelper()

parser = argparse.ArgumentParser(description='Bot for helping in administration in DevOps groups in TG')

parser.add_argument("-b","--bottoken", dest="bottoken", type=str,default="1231423",help="Bot token for TG API")
parser.add_argument("-e","--environment", dest="environment", type=str,default="config.ini",help="Environment for bot")

args = parser.parse_args()
bottoken = args.bottoken
environment = args.environment
config = configparser.ConfigParser()
# config.read('config.ini')
config.read(environment)

# bottoken= str(sys.argv[1])
updater = Updater(token=bottoken, use_context=True)
dispatcher = updater.dispatcher

# Get admins list
@MWT(timeout=60*60)
def get_admin_ids(context, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in context.bot.get_chat_administrators(chat_id)]

class Base:
    def __init__(self):
        self.section = None
        self.in_section = None
        self.feature_flag = False
        self.username = None
        self.user_id = None
        self.mention_user = None
        self.admin = False
        self.root_url = config.get('shared','root_url')
        self.channel_specify = None
        self.course_location = config.get('shared', 'course_folder')
        self.hrman = config.get('shared', 'hrman_filename')
        self.relocate = config.get('shared', 'relocate_filename')
        self.coc = config.get('shared', 'coc_filename')
        self.vacancy = config.get('shared', 'jobs_filename')
        self.ad = config.get('shared', 'advertising_filename')
        self.chats = config.get('shared', 'othet_chats')
        self.events = config.get('shared', 'events_list')
        self.message_text= str
        self.hour = int()
        self.day = int()
        self.duration=str()
        self.esc_map = {
        "_" : r"\_",
        "*" : r"\*",
        "[" : r"\[",
        "]" : r"\]",
        "(" : r"\(",
        ")" : r"\)",
        "~" : r"\~",
        "`" : r"\`",
        ">" : r"\>",
        "#" : r"\#",
        "+" : r"\+",
        "-" : r"\-",
        "=" : r"\=",
        "|" : r"\|",
        "{" : r"\{",
        "}" : r"\}",
        "." : r"\.",
        "!" : r"\!"
        }

    def features_state(self, update,command_name):
        self.section = str(update.message.chat.id)
        if config.has_section(self.section):
                self.in_section = True
                if config.get(self.section, command_name) == 'on':
                        self.feature_flag = True
                        return True

    def user_data(self, update):
        self.mention_user = update.message.from_user.mention_markdown_v2()
        return self.mention_user

    def is_admin(self, update, context):
        if update.message.from_user.id in get_admin_ids(context, update.message.chat_id):
            return True

    def study(self, command_name):
        self.channel_specify = config.get(self.section, 'study')
        if command_name == 'starter':
            starter = config.get(self.section, 'starter_filename')
            url = self.root_url + self.channel_specify + "/" + starter
            return url
        elif command_name == 'middle':
            middle = config.get(self.section, 'middle_filename')
            url = self.root_url + self.channel_specify + "/" + middle
            return url
        elif command_name == 'course':
            course = config.get('shared', 'course_filename')
            url = self.root_url + self.course_location + "/" + course
            return url
        elif command_name == 'cert':
            certification = config.get(self.section, 'certification_filename')
            url = self.root_url + self.channel_specify + "/" + certification
            return url
        elif command_name == 'tasks':
            url = config.get(self.section, 'github_url')
            return url

    def common(self, command_name):
        if command_name == 'hrman':
            url = self.root_url + self.hrman
            return url
        if command_name == 'relocate':
            url = self.root_url + self.relocate
            return url
        if command_name == 'coc':
            url = self.root_url + self.coc
            return url
        if command_name == 'work':
            url = self.root_url + self.vacancy
            return url
        if command_name == 'ad':
            url = self.root_url + self.coc
            return url
        if command_name == 'chats':
            url = self.root_url + self.chats
            return url
        if command_name == 'events':
            url = self.root_url + self.events
            return url

    def admin_variables(self, update):
        self.section = str(update.message.chat.id)
        spam_rss = config.get(self.section, 'admin_chat')
        return spam_rss

    def summons(self,update):
        self.section = str(update.message.chat.id)
        user_list = config.get(self.section, 'summon_list')
        return user_list

    def available_commands(self,update):
        self.section = str(update.message.chat.id)
        file = open("helps/" + config.get(self.section, 'commands_list') + "/commands.txt", "r")
        return file

    def moveIDs(self, update):
        self.section = str(update.message.chat.id)
        from_id = config.get(self.section, 'move_from_id')
        to_name = config.get(self.section, 'move_to_name')
        to_id = config.get(self.section, 'move_to_id')
        return from_id, to_name, to_id

    def job_variables(self, update):
        self.section = str(update.message.chat.id)
        job_rss = config.get(self.section, 'job_rss')
        job_channels = shlex.split(job_rss)
        match_job = re.compile("#вакансия", re.IGNORECASE)
        match_work = re.compile("#резюме", re.IGNORECASE)
        matches_job = match_job.search(update.message.reply_to_message.text)
        matches_work = match_work.search(update.message.reply_to_message.text)
        rss_link = re.sub("@", "https://t.me/", job_channels[0])
        msg = str(update.message.reply_to_message.text)
        escTable= msg.maketrans(self.esc_map)
        escMsg = msg.translate(escTable)
        user_id = update.message.reply_to_message.from_user.mention_markdown_v2()
        ChatUsername = str(update.message.chat.username)
        escTable= ChatUsername.maketrans(self.esc_map)
        escChatUsername = ChatUsername.translate(escTable)
        return matches_job, matches_work, rss_link, job_channels, escMsg, user_id, escChatUsername

    def mute_variables(self, update):
        self.section = str(update.message.chat.id)
        admin_chat = config.get(self.section, 'admin_chat')
        restrict = ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
        resUser = str(update.message.reply_to_message.from_user.first_name)
        escape_resUser = re.escape(resUser)
        escTableUsername= escape_resUser.maketrans(self.esc_map)
        escUsername = escape_resUser.translate(escTableUsername)
        user_id = update.message.reply_to_message.from_user.id
        muted_user = update.message.reply_to_message.from_user.mention_markdown_v2()
        ChatUsername = str(update.message.chat.username)
        escTable= ChatUsername.maketrans(self.esc_map)
        escChatUsername = ChatUsername.translate(escTable)
        return admin_chat, restrict, escUsername, user_id, muted_user, escChatUsername

    def mute_parse_date(self, update):
        self.message_text = update.message.text
        if any(re.findall("[0-9]{1,2}h", self.message_text)):
            temp = re.findall("[0-9]{1,2}h", self.message_text)
            self.hour = int(re.sub("h", "", temp[0]))
        elif any(re.findall("[0-9]{1,3}d", self.message_text)):
            temp = re.findall("[0-9]{1,3}d", self.message_text)
            self.day = int(re.sub("d", "", temp[0]))
        elif any(re.findall("[0-9]{1,2}w", self.message_text)):
            temp = re.findall("[0-9]{1,2}w", self.message_text)
            self.day = self.day + int(re.sub("w", "", temp[0])) * 7
        if any(re.findall("inf", self.message_text)):
            self.day = 367
        if self.hour == 0 and self.day == 0:
            self.day = 1
            self.hour = 0
        return self.hour, self.day

    def mute_gen_duration_message(self):
        muteUntil = str(datetime.datetime.now() + datetime.timedelta(days=self.day, hours=self.hour))
        dateEsc = re.escape(muteUntil)
        return dateEsc

    def mute_parse_comment_message(self, update):
        self.message_text = update.message.text
        comment = self.message_text.replace("/mute", "")
        if any(re.findall("[0-9]{1,2}h", self.message_text)):
            comment = re.sub("[0-9]{1,2}h", "", comment)
        elif any(re.findall("[0-9]{1,3}d", self.message_text)):
            comment = re.sub("[0-9]{1,3}d", "", comment)
        elif any(re.findall("[0-9]{1,2}w", self.message_text)):
            comment = re.sub("[0-9]{1,2}w", "", comment)
        if not comment:
            comment = "without comment"
        elif comment == " ":
            comment = "without comment"
        return comment

# Initiallaze main class
base = Base()

# User commands

## Studies commands
### Send user starter kit
def starter(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    triggered_user = base.user_data(update)
    url = base.study(command_name)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id,text= "We have " + "[starter kit for newbies]" + "(" + url + ")" + \
                "\. Also we have test tasks for SRE and list of various courses\. You can find them in the same repository or via bot \(see man for commands\)\.", \
                parse_mode='MarkdownV2', reply_to_message_id=update.message.reply_to_message.message_id,disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=triggered_user + \
                " here is your " + "[starter kit]" + "(" + url + ")" + "\. Also we have test tasks for SRE and list of various courses\. You can find them in the same repository or via bot \(see man for commands\)\.", \
                parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

starter_handler = CommandHandler('starter', starter, run_async=True)
dispatcher.add_handler(starter_handler)

### Send user middle kit
def middle(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    triggered_user = base.user_data(update)
    url = base.study(command_name)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id,text= "We have " + "[middle kit]" + "(" + url + ")" + \
                "\. Also we have test tasks for SRE and list of various courses\. You can find them in the same repository or via bot \(see man for commands\)\.", \
                parse_mode='MarkdownV2', reply_to_message_id=update.message.reply_to_message.message_id,disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=triggered_user + \
                " here is your " + "[middle kit]" + "(" + url + ")" + "\. Also we have test tasks for SRE and list of various courses\. You can find them in the same repository or via bot \(see man for commands\)\.", \
                parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

middle_handler = CommandHandler('middle', middle, run_async=True)
dispatcher.add_handler(middle_handler)

### Send user list of various courses
def course(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    triggered_user = base.user_data(update)
    url = base.study(command_name)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id,text= "We have " + "[courses list]" + "(" + url + ")" + \
                "\.", parse_mode='MarkdownV2', reply_to_message_id=update.message.reply_to_message.message_id,disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=triggered_user + \
                " here is your " + "[courses list]" + "(" + url + ")" + "\.",parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

course_handler = CommandHandler('course', course, run_async=True)
dispatcher.add_handler(course_handler)

### Send user tips for certifications
def cert(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    triggered_user = base.user_data(update)
    url = base.study(command_name)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id,text= "We have " + "[certification tips]" + "(" + url + ")" + \
            "\.", parse_mode='MarkdownV2', reply_to_message_id=update.message.reply_to_message.message_id,disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=triggered_user + \
                " here is your " + "[certification tips]" + "(" + url + ")" + "\.", parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

cert_handler = CommandHandler('cert', cert, run_async=True)
dispatcher.add_handler(cert_handler)

### Send user test tasks
def tasks(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    triggered_user = base.user_data(update)
    url = base.study(command_name)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id, text="We have"+ "[DevOps tasks]" + "(" + url + ")" + "\." \
                ,parse_mode='MarkdownV2', reply_to_message_id=update.message.reply_to_message.message_id,disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=triggered_user + \
                " here is your " + "[DevOps tasks]" + "(" + url + ")" + "\.",parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

tasks_handler = CommandHandler('tasks', tasks, run_async=True)
dispatcher.add_handler(tasks_handler)

## Common commands

### Send to user common tasks
def hrman(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    triggered_user = base.user_data(update)
    url = base.common(command_name)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id,text= "We have " + "[HR man]" + "(" + url + ")" + \
                "\. Please read it carefully\.", \
                parse_mode='MarkdownV2', reply_to_message_id=update.message.reply_to_message.message_id, disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.message.chat_id,text= triggered_user + \
                " here is your " + "[HR man]" + "(" + url + ")" + "\. Please read it carefully\.", \
                parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

hrman_handler = CommandHandler('hrman', hrman, run_async=True)
dispatcher.add_handler(hrman_handler)

### Send user list of various relocate chats
def relocate(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    triggered_user = base.user_data(update)
    url = base.common(command_name)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id, text="We have list of " + "[relocate chats and channels]" + "(" + url + ")" + "\." \
                , parse_mode='MarkdownV2', reply_to_message_id=update.message.reply_to_message.message_id, disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=triggered_user + \
                " here is your list of " + "[relocate chats and channels]" + "(" + url + ")" + "\." \
                , parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

relocate_handler = CommandHandler('relocate', relocate, run_async=True)
dispatcher.add_handler(relocate_handler)

### Send use Code of Conduct
def coc(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    triggered_user = base.user_data(update)
    url = base.common(command_name)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id, text="We have " + "[Code of Conduct]" + "(" + url + ")" + "\. Please read it carefully\.", \
                reply_to_message_id=update.message.reply_to_message.message_id, parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=triggered_user + \
                " here is our " + "[Code of Conduct]" + "(" + url + ")" + "\." \
                , parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

coc_handler = CommandHandler('coc', coc, run_async=True)
dispatcher.add_handler(coc_handler)

### Send user job opportunity and cv publish rules
def work(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    triggered_user = base.user_data(update)
    url = base.common(command_name)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id,text= "We have " + "[job opportunities and cv publish rules]" + "(" + url + ")" + \
                "\. Please read them carefully and follow them\.", \
                parse_mode='MarkdownV2', reply_to_message_id=update.message.reply_to_message.message_id, disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.message.chat_id,text= triggered_user + " here is your "+ \
                "[job opportunities and cv publish rules]" + "(" + url + ")" + \
                "\. Please read them carefully and follow them\.", parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

work_handler = CommandHandler('work', work, run_async=True)
dispatcher.add_handler(work_handler)

### Send user advertising rules
def ad(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    triggered_user = base.user_data(update)
    url = base.common(command_name)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id, text="We have " + \
                "[advertising publish rules]" + "(" + url + ")" + "\. Please read them carefully and follow them\.", \
                reply_to_message_id=update.message.reply_to_message.message_id, parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=triggered_user + \
                " here is your " + "[advertising publish rules]" + "(" + url + ")" + "\.", parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

ad_handler = CommandHandler('ad', ad, run_async=True)
dispatcher.add_handler(ad_handler)

### Send user list of friendly chats
def chats(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    triggered_user = base.user_data(update)
    url = base.common(command_name)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id, text="We have " + \
                "[friendly chats list]" + "(" + url + ")" + "\." ,\
            reply_to_message_id=update.message.reply_to_message.message_id, parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=triggered_user + \
                " here is your " + "[friendly chats list]" + "(" + url + ")" + "\." ,\
            parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

chats_handler = CommandHandler('chats', chats, run_async=True)
dispatcher.add_handler(chats_handler)

### Send user events rules
def events(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    triggered_user = base.user_data(update)
    url = base.common(command_name)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id, text="Here is your " + "[events list]" + "(" + url + ")" + "\.", \
                reply_to_message_id=update.message.reply_to_message.message_id, parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=triggered_user + " here is your " + "[events list]" + "(" + url + ")" + "\.", \
                parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

events_handler = CommandHandler('events', events, run_async=True)
dispatcher.add_handler(events_handler)

### User send report message to admins
def report(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    admin_chats = base.admin_variables(update)
    ### ERROR!!! AttributeError: 'NoneType' object has no attribute 'from_user' if there is no reply user ID
    # chat_id = str(update.message.chat_id)
    # user_id = str(update.message.reply_to_message.from_user.id)
    # message_id = str(update.message.reply_to_message.message_id)
    # keyboard = [
    #         [InlineKeyboardButton('burn spam', callback_data='spam ' + chat_id + ' ' + user_id + ' ' + message_id)]
    #     ]
    # reply_markup = InlineKeyboardMarkup(keyboard)
    if feature_status:
        try:
            context.bot.send_message(chat_id=update.message.chat_id, text="Report on [spam message]("+ "https://t.me/" + str(update.message.chat.username) + "/" \
                + str(update.message.reply_to_message.message_id) + ")" + " was send to admins. Please be patient.", \
                disable_web_page_preview=True, parse_mode='Markdown')
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
            context.bot.forward_message(chat_id=admin_chats, from_chat_id=update.message.chat_id, message_id=update.message.reply_to_message.message_id)
            context.bot.send_message(chat_id=admin_chats, text="User think it's spam: " + "https://t.me/"+ str(update.message.chat.username)+"/" \
                + str(update.message.reply_to_message.message_id), disable_web_page_preview=True)
                # + str(update.message.reply_to_message.message_id), disable_web_page_preview=True, reply_markup=reply_markup)
        except AttributeError:
            context.bot.send_message(chat_id=update.message.chat_id, text="Report command works on replied messages only.")
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

report_handler = CommandHandler('report', report)
dispatcher.add_handler(report_handler)

### User summon some HRs in thread
def summon(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    called_upon = base.summons(update)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id, text= "I'm DevOps Bot and i summon you HR for answer: " + \
                called_upon + " and the question is: " + str(update.message.reply_to_message.text), \
                    reply_to_message_id=update.message.message_id)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
            context.bot.send_message(chat_id=update.message.chat_id, text="Summon command works on replied messages only.")
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

summon_handler = CommandHandler('summon', summon, run_async=True)
dispatcher.add_handler(summon_handler)

### Send user bots man
def man(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    triggered_user = base.user_data(update)
    help_file = base.available_commands(update)
    if feature_status:
        if update.message.reply_to_message is not None:
            context.bot.send_message(chat_id=update.message.chat_id, text="Here is the list of available commands\. " \
            + "\n" + help_file.read(), reply_to_message_id=update.message.reply_to_message.message_id, \
                parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=triggered_user + " here it is\. " \
            + "\n" + help_file.read(), parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else:
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

man_handler = CommandHandler('man', man, run_async=True)
dispatcher.add_handler(man_handler)

# Admin commands
## Get chat number
def idnumber(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    admins = base.is_admin(update, context)
    if feature_status and admins:
            # context.bot.send_message(chat_id=update.message.chat_id,text="_Italic text_ from user " + triggered_user, parse_mode='MarkdownV2')
            context.bot.send_message(chat_id=update.message.chat_id, text=update.message.chat_id)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    else: 
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

idnumber_handler = CommandHandler('idnumber', idnumber, run_async=True)
dispatcher.add_handler(idnumber_handler)

def move(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    admins = base.is_admin(update, context)
    triggered_user = base.user_data(update)
    move_data = base.moveIDs(update)
    if feature_status and admins:
        if update.message.reply_to_message.photo:
            context.bot.send_message(chat_id=move_data[0], text="Your photo " + triggered_user +  " was moved to " + move_data[1])
            context.bot.forward_message(chat_id=move_data[2], from_chat_id=update.message.chat_id, message_id=update.message.reply_to_message.message_id)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.reply_to_message.message_id)
        else:
            context.bot.send_message(chat_id=move_data[0], text="Your post " + triggered_user +  " was moved to " + move_data[1],
                parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.send_message(chat_id=move_data[2], text="Message was forwarded from: " + "@" + str(update.message.chat.username) + "\n" + \
                    "Author: " + "@" + str(update.message.reply_to_message.from_user.username) + "\n" +  \
                    "Message: " + str(update.message.reply_to_message.text), parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.reply_to_message.message_id)

move_handler = CommandHandler('move', move, run_async=True)
dispatcher.add_handler(move_handler)

## Jobs
def job(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    admins = base.is_admin(update, context)
    triggered_user = base.user_data(update)
    job_checks = base.job_variables(update)
    if job_checks[1] is not None: 
        text_to_publish = "[Резюме]" + "(https://t\.me/"+ str(update.message.chat.username) + "/" + str(update.message.reply_to_message.message_id) + ")" \
            + " было опубликована в " + "[RSS канале]" + "(" + job_checks[2] + ")"
    elif job_checks[0] is not None:
        text_to_publish = "[Вакансия]" + "(https://t\.me/"+ str(update.message.chat.username)+"/"+ str(update.message.reply_to_message.message_id) + ")" \
            + " была опубликована в " + "[RSS канале]" + "(" + job_checks[2] + ")"
    if feature_status and admins:
        if job_checks[0] is None and job_checks[1] is None:
            context.bot.send_message(chat_id=update.message.chat.id, reply_to_message_id=update.message.reply_to_message.message_id, \
                    text="В Вашем посте отсуствует тег #вакансия или #резюме. Невозможно определить тип поста.")
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            for i in job_checks[3]:
                context.bot.send_message(chat_id=i, text="Публикатор: " + job_checks[5] + "\n"+ "Обсуждение вакансии в чате @" + job_checks[6] + "\n" + job_checks[4], 
                    parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.reply_to_message.message_id, \
                    text=text_to_publish, parse_mode='MarkdownV2', disable_web_page_preview=True)
            context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

jobs_handler = CommandHandler('job', job, run_async=True)
dispatcher.add_handler(jobs_handler)

def mute(update, context):
    command_name = inspect.currentframe().f_code.co_name
    feature_status = base.features_state(update,command_name)
    admins = base.is_admin(update, context)
    hour,day = base.mute_parse_date(update)
    mute_until = base.mute_gen_duration_message()
    comment = base.mute_parse_comment_message(update)
    triggered_user = base.user_data(update)
    mute_vars = base.mute_variables(update)
    if feature_status and admins:
        context.bot.restrict_chat_member(chat_id=update.message.chat_id, user_id=update.message.reply_to_message.from_user.id, \
            until_date=datetime.datetime.now() + datetime.timedelta(days=day, hours=hour), permissions = mute_vars[1])
        context.bot.send_message(chat_id=mute_vars[0], text="User " + mute_vars[4] + " was muted by admin " + triggered_user \
            + " in chat @" + mute_vars[5] + "\n" + "Until: " + mute_until + "\nComment: " + comment, \
            parse_mode='MarkdownV2', disable_web_page_preview=True)
        context.bot.send_message(chat_id=update.message.chat_id, text="User " + mute_vars[4] + " muted\. \nReason: " + comment, \
            parse_mode='MarkdownV2', disable_web_page_preview=True, reply_to_message_id=update.message.message_id)
        context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

mute_handler = CommandHandler('mute', mute, pass_args=True, run_async=True)
dispatcher.add_handler(mute_handler)

# Automate service actions
## Delete service messages
def delete_service_message(update, context):
        section = str(update.message.chat.id)
        in_section = section in config.sections()
        command_name = inspect.currentframe().f_code.co_name
        feature_flag = config.get(section, command_name) == 'on'
        msg = update.effective_message
        if in_section and feature_flag:
            context.bot.delete_message(chat_id=msg.chat.id,message_id=msg.message_id)

dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, delete_service_message, run_async=True))
dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, delete_service_message, run_async=True))

def main():
        pass

if __name__ == '__main__':
    main()
updater.start_polling()