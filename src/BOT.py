#pip install python-telegram-bot

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CHAT_ID_GRUPPO = -1001397315169    # subito_crypto
CHAT_ID_VETRINA = -1001872734100    # subito_crypto_vetrina
CHAT_ID_FEEDBACK = -1001956565384   # subito_crypto_feedbacks

TOKEN_DEL_BOT = "Nascosto su github"

async def gestione_messaggi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat.id     # chat di provenienza dell'annuncio (si suppone sia il mercatino)
    if chat == CHAT_ID_GRUPPO or chat == CHAT_ID_FEEDBACK or chat == CHAT_ID_VETRINA:
        mex = update.effective_message  # messaggio con l'annuncio
        user = mex.from_user.name       # autore dell'annuncio

        # in tutte le seguenti casistiche, nel messaggio da inviare si piò aggiungere il metodo .split(" ", 1)[1], 
        # che serve a eliminare le parole #vendo etc, ma ho pensato di toglierlo perché è bene distinguere vendo da cerco

        if user != "Telegram":
            if mex.photo and "#vendo" in str(mex.caption).lower():
                # annunci contenenti un immagine: solo la prima viene inviata.
                # questi annunci vanno inviati in vetrina, poi eliminati gli originali
                description = str(mex.caption).lower() #estrazione dell'annuncio dalla didascalia
                text_to_be_sent = description + "\n\nANNUNCIO DI:\n" + user
                photo = mex.photo[-1]           # estrazione della foto dal messaggio
                photo_file_id = photo.file_id   # id della foto, presente direttamente sui server telegram
                await context.bot.send_photo(chat_id=CHAT_ID_VETRINA, photo=photo_file_id, caption=text_to_be_sent)
                await mex.delete()

            elif ("#vendo" in mex.text) or ("#cerco" in mex.text) or ("#servizio" in mex.text):
                # annunci da inviare in vetrina, funzionamento analogo alle immagini
                sale_advertisement = mex.text
                attached_message = sale_advertisement + "\n\nANNUNCIO DI:\n" + user
                await context.bot.send_message(CHAT_ID_VETRINA, attached_message)
                await mex.delete()
            
            elif "#feedback" in mex.text:
                # feedback da inviare nell'omonimo canale, funzionamento analogo alle immagini
                feedback_text = mex.text
                feedback_message = feedback_text + "\n\nFEEDBACK DA PARTE DI:\n" + user
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
