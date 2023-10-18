#pip install python-telegram-bot

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CHAT_ID_GRUPPO      = -1001397315169    # subito_crypto
CHAT_ID_VETRINA     = -1001872734100    # subito_crypto_vetrina
CHAT_ID_FEEDBACK    = -1001956565384    # subito_crypto_feedbacks
CHAT_ID_NOLEGGI     = -1001644892959    # chat_noleggintermediazionepostale
CHAT_ID_ASTE        = -1001880758375    # asteinbitcoin (gruppo collegato)

TOKEN_DEL_BOT = "Nascosto su github"

async def gestione_messaggi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat.id     # chat di provenienza dell'annuncio (si suppone sia il mercatino)
    
    mex = update.effective_message  # messaggio con l'annuncio
    user = mex.from_user.name       # autore dell'annuncio

    if chat == CHAT_ID_GRUPPO or chat == CHAT_ID_FEEDBACK or chat == CHAT_ID_VETRINA:

        # in tutte le seguenti casistiche, nel messaggio da inviare si piò aggiungere il metodo .split(" ", 1)[1], 
        # che serve a eliminare le parole #vendo etc, ma ho pensato di toglierlo perché è bene distinguere vendo da cerco

        if user != "Telegram":
            if mex.photo and (("#vendo" in str(mex.caption).lower()) or ("#cerco" in str(mex.caption).lower()) or ("#servizio" in str(mex.caption).lower())):
                # annunci contenenti un immagine: solo la prima viene inviata.
                # questi annunci vanno inviati in vetrina, poi eliminati gli originali
                description = str(mex.caption) #estrazione dell'annuncio dalla didascalia
                text_to_be_sent = description + "\n\nANNUNCIO DI:\n" + user
                photo = mex.photo[-1]           # estrazione della foto dal messaggio
                photo_file_id = photo.file_id   # id della foto, presente direttamente sui server telegram
                await context.bot.send_photo(chat_id=CHAT_ID_VETRINA, photo=photo_file_id, caption=text_to_be_sent)
                await mex.delete()

        elif ("#vendo" in mex.text.lower()) or ("#cerco" in mex.text.lower()) or ("#servizio" in mex.text.lower()):
            # annunci da inviare in vetrina, funzionamento analogo alle immagini
            sale_advertisement = mex.text
            attached_message = sale_advertisement + "\n\nANNUNCIO DI:\n" + user
            await context.bot.send_message(CHAT_ID_VETRINA, attached_message)
            await mex.delete()
        
        elif "#feedback" in mex.text.lower():
            # feedback da inviare nell'omonimo canale, funzionamento analogo alle immagini
            feedback_text = mex.text
            feedback_message = feedback_text + "\n\nFEEDBACK DA PARTE DI:\n" + user
            await context.bot.send_message(CHAT_ID_FEEDBACK, feedback_message)
            await mex.delete()

        elif ("#trovato" in mex.text.lower() or "#venduto" in mex.text.lower()):
                chat_admins = await update.effective_chat.get_administrators() # recupero la lista di admin della chat
                if update.effective_user in (admin.user for admin in chat_admins):
                    # Solo un admin può inviare il messaggio. Non c'è modo infatti di recuperare a posteriori 
                    # l'autore dell'annuncio -> ha senso che solo l'autore possa eliminare i suoi annunci
                    # per ovviare al problema, la funzione viene limitata agli admin, che si suppone non abbiano
                    # interesse a far danni
                    original_message_id = mex.reply_to_message.forward_from_message_id
                    try:
                        await context.bot.delete_message(chat_id = CHAT_ID_VETRINA, message_id = original_message_id)
                        # Un esempio di Eccezione è un messaggio postato più di 48h fa, che non può essere eliminato  dal bot
                    except Exception:
                        await context.bot.send_message(CHAT_ID_GRUPPO, "Message can't be deleted, please do it manually")
                    #await mex.delete() non serve, perché un mex eliminato in vetrina elimina anche tutte le risposte,questa compresa
                else:
                    await context.bot.send_message(CHAT_ID_GRUPPO, "Questo tag possono usarlo solo gli admin (per ora almeno)", reply_to_message_id=mex.id)


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
