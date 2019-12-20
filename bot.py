#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, CallbackContext, Filters
import numexpr
from secure import BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Привет! Я могу посчитать, например, вот это:\n'
        '`2 + 4 * 5`\n'
        '`12 / 3`\n'
        '`sqrt(4)`\n'
        'Просто напишите мне любой пример!\n',
        parse_mode='Markdown'
    )


def comp_expr(query: str):
    result = numexpr.evaluate(query).item()
    if type(result) == float and result.is_integer():
        result = int(result)
    return result


def inline_query(update: Update, context: CallbackContext):
    query = update.inline_query.query
    try:
        result = comp_expr(query)
    except Exception:
        diff_count = query.count('(') - query.count(')')
        if diff_count > 0:
            query += ')' * diff_count
            try:
                result = comp_expr(query)
            except Exception:
                result = None
        else:
            result = None
    query_results = []
    if result:
        query_results.append(
            InlineQueryResultArticle(
                id=uuid4(),
                title=f'{query} = {result}',
                input_message_content=InputTextMessageContent(f'{query} = <b>{result}</b>', parse_mode='HTML')
            )
        )
    update.inline_query.answer(query_results)


def dm_query(update: Update, context: CallbackContext):
    query = update.message.text
    try:
        result = comp_expr(query)
        update.message.reply_text(f'{query} = <b>{result}</b>', parse_mode='HTML')
    except Exception as e:
        update.message.reply_text('Error')


def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(BOT_TOKEN, use_context=True, request_kwargs={
        'proxy_url': 'socks5h://t.geekclass.ru:7777',
        'urllib3_proxy_kwargs': {
            'username': 'geek',
            'password': 'socks',
        }
    })

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(InlineQueryHandler(inline_query))
    dp.add_handler(MessageHandler(Filters.text, dm_query))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
