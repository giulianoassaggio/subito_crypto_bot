import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from model import Utente, Skin, UserSkin
from config import TOKEN_DEL_BOT

# Configurazione del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Stato globale per tracciare le skin visualizzate dagli utenti
user_skins = {}

async def gestione_messaggi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all incoming messages."""
    try:
        chat = update.effective_chat.id  # chat di provenienza dell'annuncio (si suppone sia il mercatino)
        mex = update.effective_message  # messaggio con l'annuncio
        userid = update.effective_chat.id

        Utente().checkUtente(mex)
        user = Utente().getUtente(userid)

        if mex.text == '/skins':
            skins = Skin().get_all_skins()  # Metodo da implementare per ottenere tutte le skins disponibili
            if skins:
                for skin in skins:
                    keyboard = []
                    if Utente().isAdmin(user):
                        keyboard.append([InlineKeyboardButton("Elimina", callback_data=f"delete_{skin.id}")])

                    if UserSkin().has_skin(userid, skin.id):
                        keyboard.append([InlineKeyboardButton("Usa", callback_data=f"use_{skin.id}")])
                    else:
                        keyboard.append([InlineKeyboardButton("Compra", callback_data=f"buy_{skin.id}")])

                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await context.bot.send_photo(chat_id=userid, photo=skin.fileid, caption=f"{skin.name}\nPrezzo: {skin.price} coins", reply_markup=reply_markup)

                user_skins[userid] = skins
            else:
                await context.bot.send_message(chat_id=userid, text="Nessuna skin disponibile al momento.")

        elif mex.text == '/me':
            user_skin = UserSkin().get_selected_skin(userid)
            if user_skin:
                await context.bot.send_message(chat_id=userid, text=f"Stai usando la skin: {user_skin.name}")
            else:
                await context.bot.send_message(chat_id=userid, text="Non hai selezionato nessuna skin.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Si è verificato un errore.")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries from inline keyboard."""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        query_data = query.data.split('_')
        action = query_data[0]
        skin_id = int(query_data[1])

        if action == 'buy':
            skin = Skin().get_skin_by_id(skin_id)  # Metodo da implementare per ottenere la skin dall'ID
            if skin:
                # Simulazione di un sistema di monete o punti per l'utente
                coins = Utente().get_coins(user_id)  # Metodo da implementare per ottenere le monete dell'utente
                if coins >= skin.price:
                    UserSkin().add_user_skin(user_id, skin_id)
                    await query.answer("Skin acquistata con successo!")
                else:
                    await query.answer("Non hai abbastanza coins per acquistare questa skin.")
            else:
                await query.answer("Skin non trovata.")

        elif action == 'use':
            UserSkin().select_user_skin(user_id, skin_id)
            await query.answer("Skin impostata come attuale.")

        elif action == 'delete':
            if Utente().isAdmin(user):
                Skin().delete_skin(skin_id)  # Metodo da implementare per eliminare una skin
                await query.answer("Skin eliminata con successo!")
            else:
                await query.answer("Non sei autorizzato a eliminare skin.")

    except Exception as e:
        logging.error(f"An error occurred in callback handler: {e}")
        await query.answer("Si è verificato un errore.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN_DEL_BOT).build()
    function_handler = MessageHandler(filters.ALL, gestione_messaggi)
    callback_query_handler = CallbackQueryHandler(callback_handler)
    application.add_handler(function_handler)
    application.add_handler(callback_query_handler)
    application.run_polling()
