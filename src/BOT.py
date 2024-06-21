#pip install python-telegram-bot

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler,CommandHandler
from model import Utente,Feedback,Gruppo,Tag,Skin
from config import *
from lndhub import Wallet

# Stato globale per tracciare se un utente admin è in fase di aggiunta di una skin
pending_skins = {}

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

        if Utente().isAdmin(user):
            if mex.text=='/addskin':
                pending_skins[userid] = {'state': 'awaiting_photo'}
                await context.bot.send_message(chat_id=userid, text="Per favore, invia la foto della skin.")
                return

            if userid in pending_skins:
                if pending_skins[userid]['state'] == 'awaiting_photo' and mex.photo:
                    pending_skins[userid]['photo'] = mex.photo[-1].file_id
                    pending_skins[userid]['state'] = 'awaiting_description'
                    await context.bot.send_message(chat_id=userid, text="Ora, invia una descrizione per la skin.")
                
                if pending_skins[userid]['state'] == 'awaiting_description' and mex.text:
                    pending_skins[userid]['description'] = mex.text
                    pending_skins[userid]['state'] = 'awaiting_price'
                    await context.bot.send_message(chat_id=userid, text="Ora, invia il prezzo per la skin.")
                    return

                if pending_skins[userid]['state'] == 'awaiting_price' and mex.text:
                    try:
                        price = int(mex.text)
                        description = pending_skins[userid]['description']
                        file_id = pending_skins[userid]['photo']

                        Skin().add_skin(name=description, fileid=file_id, price=price)
                        await context.bot.send_message(chat_id=userid, text="Skin aggiunta con successo!")
                    except ValueError:
                        await context.bot.send_message(chat_id=userid, text="Per favore, invia un prezzo valido (numero intero).")
                    except Exception as e:
                        logging.error(f"Errore durante l'aggiunta della skin: {e}")
                        await context.bot.send_message(chat_id=userid, text="Si è verificato un errore durante l'aggiunta della skin.")
                    finally:
                        del pending_skins[userid]
                    return
                
        
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