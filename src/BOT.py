#pip install python-telegram-bot

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler,CommandHandler
from model import Utente,Feedback,Gruppo,Tag
from config import *
from lndhub import Wallet


async def gestione_messaggi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all incoming messages."""
    try:
        chat = update.effective_chat.id  # chat di provenienza dell'annuncio (si suppone sia il mercatino)
        mex = update.effective_message  # messaggio con l'annuncio
        userid = update.effective_chat.id

        Utente().checkUtente(mex)
        user = Utente().getUtente(userid)

        if Gruppo().getGruppoByChatId(chat):  # Se il gruppo è presente nel db e quindi ammesso
            Tag().addTagsByMessage(mex.text, userid)

        if mex.text == '/me':
            await context.bot.send_message(chat_id=update.effective_chat.id, text=Utente().infoUser(user),parse_mode='markdown')

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Si è verificato un errore.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN_DEL_BOT).build()
    function_handler = MessageHandler(None, callback=gestione_messaggi)
    application.add_handler(function_handler)
    application.run_polling()