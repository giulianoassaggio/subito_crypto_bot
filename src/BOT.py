#pip install python-telegram-bot

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler
from model import Utente,Feedback,Gruppo,Tag
from config import *

"""
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
"""

app_config = TestConfig()
#app_config = ProdConfig()


TOKEN_DEL_BOT = "7063743485:AAGu5FoKImJ1e1oeAVikhs7KHAYHb0qEWSU"

async def gestione_messaggi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat.id     # chat di provenienza dell'annuncio (si suppone sia il mercatino)
    mex = update.effective_message  # messaggio con l'annuncio
    user = mex.from_user.name       # autore dell'annuncio

    Utente().checkUtente(mex)
    Utente().getUtente(mex)
    if Gruppo().getGruppoByChatId(chat):
        # Extract hashtags from the message
        messaggio = mex.text
        print(mex)
        hashtags = Tag().getTagsByMessage(messaggio)
        print(hashtags)
        # Add tags for each hashtag
        for hashtag in hashtags:
            Tag().addTag(hashtag, messaggio, mex.from_user.id)



        if mex.photo and (("#vendo" in str(mex.caption).lower()) or ("#cerco" in str(mex.caption).lower()) or ("#servizio" in str(mex.caption).lower())):
                # annunci contenenti un immagine: solo la prima viene inviata.
                # questi annunci vanno inviati in vetrina, poi eliminati gli originali
                description = str(mex.caption) #estrazione dell'annuncio dalla didascalia
                text_to_be_sent = description + "\n\n👤 Annuncio di:\n" + user
                photo = mex.photo[-1]           # estrazione della foto dal messaggio
                photo_file_id = photo.file_id   # id della foto, presente direttamente sui server telegram
                await context.bot.send_photo(chat_id=CHAT_ID_VETRINA, photo=photo_file_id, caption=text_to_be_sent)
                await mex.delete()

        elif ("#vendo" in mex.text.lower()) or ("#cerco" in mex.text.lower()) or ("#servizio" in mex.text.lower()):
            # annunci da inviare in vetrina, funzionamento analogo alle immagini
            sale_advertisement = mex.text
            attached_message = sale_advertisement + "\n\n👤 Annuncio di:\n" + user
            await context.bot.send_message(CHAT_ID_VETRINA, attached_message)
            await mex.delete()
        
        elif "#feedback" in mex.text.lower():
            # feedback da inviare nell'omonimo canale, funzionamento analogo alle immagini
            feedback_text = mex.text
            feedback_message = feedback_text + "\n\n👤 Feedback da aprte di:\n" + user
            await context.bot.send_message(CHAT_ID_FEEDBACK, feedback_message)
            await mex.delete()
        elif "#me" in mex.text.lower():
            u = Utente().getUtenteByMessage(mex)
            await context.bot.send_message(chat, Utente().infoUser(u), parse_mode='Markdown')
    

    elif chat == CHAT_ID_NOLEGGI:
        if user != "Telegram" and "#feedback" in mex.text.lower():
            #esattamente come i feedback sopra, solo provenienti dalla chat noleggi
            feedback_text = mex.text
            feedback_message = "(#noleggio)\n\n"+feedback_text + "\n\nFEEDBACK DA PARTE DI:\n" + user
            await context.bot.send_message(CHAT_ID_FEEDBACK, feedback_message)
            await mex.delete()

    elif chat == CHAT_ID_ASTE:
        if user != "Telegram" and "#feedback" in mex.text.lower():
            #esattamente come i feedback sopra, solo provenienti dalla chat asteinbitcoin
            feedback_text = mex.text
            feedback_message = "(#asta)\n\n"+feedback_text + "\n\nFEEDBACK DA PARTE DI:\n" + user
            await context.bot.send_message(CHAT_ID_FEEDBACK, feedback_message)
            await mex.delete()
        
    else:
        # se il messaggio arriva da una chat che non c'entra nulla col mercatino (privato compreso)
        # ad ogni messaggio viene inviato l'errore (nella speranza che il bot venga tolto ahahah)
        await context.bot.send_message(chat, "Non dovrei essere in questa chat")
    
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN_DEL_BOT).build()
    function_handler = MessageHandler(None, callback=gestione_messaggi)
    application.add_handler(function_handler)
    application.run_polling()
