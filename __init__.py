#!/usr/bin/env python3
import argparse
import logging
import cyrtranslit
from telegram import InputTextMessageContent, InlineQueryResultArticle
from telegram.ext import Updater, CommandHandler, InlineQueryHandler


__version__ = "0.1.0"


log = logging.getLogger(__name__)


def logging_lvl(verbosity: int):
    LOG_LVL_MAP = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARN,
        3: logging.INFO,
        4: logging.DEBUG
    }
    # clamp verbosity into [0,4] range
    if verbosity < 0:
        verbosity = 0
    elif verbosity > 4:
        verbosity = 4
    return LOG_LVL_MAP[verbosity]


def translit(text):
    # Detect latin/non-latin input
    if len(text.encode()) == len(text):
        trans_func = cyrtranslit.to_cyrillic
    else:
        trans_func = cyrtranslit.to_latin

    return trans_func(text, lang_code='ru')


class RuTranslitBot:
    def __init__(self, args, log_level=logging.INFO):
        self.token = args.token

    def on_start(self, bot, update):
        "Start with facialbot"
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Send me a message in russian translit")

    def on_inline_msg(self, bot, update):
        inmsg = update.inline_query

        log.info('Inline query msg "%s" from: @%s' % (
            inmsg.query, inmsg.from_user.username))

        results = []
        if inmsg.query:
            trtxt = translit(inmsg.query)
            results.append(InlineQueryResultArticle(
                trtxt,
                title=trtxt,
                input_message_content=InputTextMessageContent(trtxt)))

        bot.answerInlineQuery(inmsg.id, results)

    def on_error(self, bot, update, tg_err):
        log.error('Got Telegram error: %s' % tg_err)

    def run(self):
        updater = Updater(self.token)
        self.bot = updater.bot

        updater.dispatcher.add_handler(
            CommandHandler('start', self.on_start))
        updater.dispatcher.add_handler(
            InlineQueryHandler(self.on_inline_msg))
        updater.dispatcher.add_error_handler(self.on_error)

        updater.start_polling()
        updater.idle()


def main():
    parser = argparse.ArgumentParser(
        description='Version: %s' % __version__)
    parser.add_argument('token',
                        help='Telegram bot token to use')
    parser.add_argument('-v', '--verbosity', type=int, default=3,
                        help='Verbosity level [0-4] (default: 3=INFO)')

    args = parser.parse_args()
    log_level = logging_lvl(args.verbosity)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s [%(name)s/%(levelname)s] %(message)s")

    bot = RuTranslitBot(args, log_level=log_level)
    bot.run()


if __name__ == '__main__':
    main()
