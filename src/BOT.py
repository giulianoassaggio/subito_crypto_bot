#pip install python-telegram-bot
#pip install python-telegram-bot

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CHAT_ID_GRUPPO      = -1001397315169    # subito_crypto
CHAT_ID_VETRINA     = -1001872734100    # subito_crypto_vetrina
CHAT_ID_FEEDBACK    = -1001956565384    # subito_crypto_feedbacks
CHAT_ID_ZIO         = [-1001611895993, -1001979086464]    # intermediazionepostale
CHAT_ID_ASTE        = -1001880758375    # asteinbitcoin (gruppo collegato)

TOKEN_DEL_BOT = "token"

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("function called")
    chat = update.effective_chat
    if chat.type == "private":
            await context.bot.send_message(
                    chat.id,
                    "inoltrami un messaggio e ti dirò l'utente che l'ha scritto"
                )
    else:
        if update.effective_message.reply_to_message is None:
            await context.bot.send_message(chat.id, "il comando deve essere lanciato in risposta a un messaggio")
        else:
            user_id = update.effective_message.reply_to_message.from_user.id
            user_name = update.effective_message.reply_to_message.from_user.username
            message = "Id di "+user_name+": "+str(user_id)
            await context.bot.send_message(chat.id, message)

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
                chat_admins = await update.effective_chat.get_administrators()
                if update.effective_user in (admin.user for admin in chat_admins):
                    original_message_id = mex.reply_to_message.forward_from_message_id
                    try:
                        await context.bot.delete_message(chat_id = CHAT_ID_VETRINA, message_id = original_message_id)
                    except Exception:
                        await context.bot.send_message(CHAT_ID_GRUPPO, "Message can't be deleted, please do it manually")

                    await mex.delete()
                else:
                    await context.bot.send_message(CHAT_ID_GRUPPO, "Questo tag possono usarlo solo gli admin (per ora almeno)", reply_to_message_id=mex.id)




    elif chat in CHAT_ID_ZIO:
        if user != "Telegram" and "#feedback" in mex.text.lower():
            #esattamente come i feedback sopra, solo provenienti dalla chat noleggi
            feedback_text = mex.text
            feedback_message = "(FEEDBACK ESTERNO: ZioSatoshi)\n\n"+feedback_text + "\n\nFEEDBACK DA PARTE DI:\n" + user
            await context.bot.send_message(CHAT_ID_FEEDBACK, feedback_message)

    elif chat == CHAT_ID_ASTE:
        if user != "Telegram" and "#feedback" in mex.text.lower():
            #esattamente come i feedback sopra, solo provenienti dalla chat asteinbitcoin
            feedback_text = mex.text
            feedback_message = "(FEEDBACK ESTERNO: aste in bitcoin)\n\n"+feedback_text + "\n\nFEEDBACK DA PARTE DI:\n" + user
            await context.bot.send_message(CHAT_ID_FEEDBACK, feedback_message)
            await mex.delete()

    else:
        # se il messaggio arriva da una chat che non c'entra nulla col mercatino
        # ad ogni messaggio viene inviato l'errore (nella speranza che il bot venga tolto ahahah)
        if (update.effective_chat.type != "private"):
            await context.bot.send_message(chat, "Non dovrei essere in questa chat")
        else:
            user = update.effective_message.forward_from
            if user is None:
                await context.bot.send_message(
                    update.effective_chat.id,
                    "inoltrami un messaggio e ti dirò l'utente che l'ha scritto"
                )
            else:
                user_id = user.id
                user_name = user.username
                message = "Id di "+user_name+": "+str(user_id)
                await context.bot.send_message(chat, message)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN_DEL_BOT).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, callback=gestione_messaggi))
    application.add_handler(CommandHandler("get_id", get_id))
    application.run_polling(allowed_updates=Update.ALL_TYPES)
