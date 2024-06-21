import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, CallbackQueryHandler,CallbackContext


from config import TOKEN_DEL_BOT, LNDHUB
from lndhub import Wallet
from model import Utente, Skin, UserSkin, Gruppo,Database
import datetime
import asyncio

wallet = Wallet(LNDHUB)

# Stato globale per tracciare se un utente admin è in fase di aggiunta di una skin
pending_skins = {}

async def controlla_stato_invoice(wallet, payment_request):
    try:
        # Otteniamo l'elenco degli invoice
        invoices = wallet.get_invoices()

        for i in invoices:
            if i['payment_request']==payment_request:
                return i['ispaid']

        return 'not_found'  # Gestisci il caso in cui l'invoice non è trovato

    except Exception as e:
        logging.error(f"Errore durante il controllo dello stato dell'invoice: {e}")
        return None

async def gestione_messaggi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all incoming messages."""
    try:
        chat = update.effective_chat.id
        message = update.effective_message
        user_id = update.effective_chat.id

        Utente().checkUtente(message)
        user = Utente().getUtente(user_id)

        if Gruppo().getGruppoByChatId(chat):
            Tag().addTagsByMessage(message.text, user_id)

        if Utente().isAdmin(user):
            if message.text == '/addskin':
                pending_skins[user_id] = {'state': 'awaiting_photo'}
                await context.bot.send_message(chat_id=user_id, text="Per favore, invia la foto della skin.")
                return

            if user_id in pending_skins:
                if pending_skins[user_id]['state'] == 'awaiting_photo' and message.photo:
                    pending_skins[user_id]['photo'] = message.photo[-1].file_id
                    pending_skins[user_id]['state'] = 'awaiting_description'
                    await context.bot.send_message(chat_id=user_id, text="Ora, invia una descrizione per la skin.")
                    return

                if pending_skins[user_id]['state'] == 'awaiting_description' and message.text:
                    pending_skins[user_id]['description'] = message.text
                    pending_skins[user_id]['state'] = 'awaiting_price'
                    await context.bot.send_message(chat_id=user_id, text="Ora, invia il prezzo per la skin.")
                    return

                if pending_skins[user_id]['state'] == 'awaiting_price' and message.text:
                    try:
                        price = int(message.text)
                        description = pending_skins[user_id]['description']
                        file_id = pending_skins[user_id]['photo']

                        Skin().add_skin(name=description, fileid=file_id, price=price)
                        await context.bot.send_message(chat_id=user_id, text="Skin aggiunta con successo!")
                    except ValueError:
                        await context.bot.send_message(chat_id=user_id, text="Per favore, invia un prezzo valido (numero intero).")
                    except Exception as e:
                        logging.error(f"Errore durante l'aggiunta della skin: {e}")
                        await context.bot.send_message(chat_id=user_id, text="Si è verificato un errore durante l'aggiunta della skin.")
                    finally:
                        del pending_skins[user_id]
                    return

        if message.text == '/me':
            await context.bot.send_message(chat_id=update.effective_chat.id, text=Utente().infoUser(user), parse_mode='markdown')

        elif message.text == '/skins':
            skins = Skin.get_all_skins()
            if skins:
                await invia_skins(update, context, skins)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Nessuna skin disponibile al momento.")

        elif Utente().isAdmin(user) and message.text == '/elimina':
            await elimina_skin(update, context)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Si è verificato un errore.")

async def invia_skins(update: Update, context: ContextTypes.DEFAULT_TYPE, skins, current_index=0, num_skins=3):
    try:
        # Preparazione per visualizzare fino a `num_skins` skin alla volta
        end_index = min(current_index + num_skins, len(skins))
        
        for i in range(current_index, end_index):
            skin = skins[i]
            # Preparazione del messaggio con immagine, descrizione, prezzo e pulsanti
            caption = f"<b>{skin.name}</b>\n\nPrezzo: {skin.price} Sats \n({skin.price / 100000000} BTC)"
            inline_keyboard = []
            
            # Verifica se l'utente ha già la skin
            if UserSkin().has_skin(update.effective_chat.id, skin.id):
                inline_keyboard.append([InlineKeyboardButton("Usa", callback_data=f"use_skin_{skin.id}")])
            else:
                inline_keyboard.append([InlineKeyboardButton("Compra", callback_data=f"buy_skin_{skin.id}")])

            # Costruzione della tastiera inline per ogni skin
            reply_markup = InlineKeyboardMarkup(inline_keyboard)

            # Invio del messaggio con foto, descrizione, prezzo e tastiera inline
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=skin.fileid, caption=caption, parse_mode='HTML', reply_markup=reply_markup)
    
        # Se ci sono più skin da visualizzare, aggiungi un pulsante "Mostra altre"
        if end_index < len(skins):
            next_index = end_index  # L'indice successivo da cui iniziare nella prossima iterazione
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Mostra altre skin", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Mostra altre", callback_data=f"show_more_{str(next_index)}")]]))
    
    except Exception as e:
        logging.error(f"Error sending skins: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Errore durante l'invio delle skin.")

# Definizione del gestore per i pulsanti inline
async def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    
    if data.startswith("show_more_"):
        try:
            # Estrai l'indice successivo da cui iniziare a visualizzare le skin
            next_index_str = data.split("_")[2]  # Ottieni la parte numerica dell'ID del callback

            next_index = int(next_index_str)  # Converti in intero
            
            # Recupera tutte le skin dal database (esempio)
            all_skins = Skin().get_all_skins()  # Implementa il metodo get_all_skins nel modello Skin
            
            # Invia le skin successive partendo da next_index
            await invia_skins(update, context, all_skins, current_index=next_index)
            
            # Acknowledge callback
            await query.answer()
   
        except Exception as e:
            logging.error(f"Error handling 'show_more_' callback: {e}")
            await query.answer("Errore durante il caricamento delle skin.")
    elif data.startswith("buy_skin_"):
        skin_id = int(data.split("_")[2])
        await crea_invoice(update, context, skin_id)
        await query.answer()

    elif data.startswith("check_invoice_"):
        try:
            
            payment_request = data.split("_")[2]
            invoices = wallet.get_invoices()

            for i in invoices:
                if i['payment_request'].startswith(payment_request):
                    invoice_status = i['ispaid']
                    break

            invoice_status = 'Pagato' if invoice_status else 'Non pagato'
            # Invia un messaggio all'utente con lo stato dell'invoice
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Stato dell'invoice: {invoice_status}")
            
            # Acknowledge callback
            await query.answer()
        except Exception as e:
            logging.error(f"Error handling 'check_invoice_' callback: {e}")
            await query.answer("Errore durante la verifica dello stato dell'invoice.")


async def elimina_skin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Gestione dell'eliminazione della skin (solo se admin)
        query = update.callback_query
        skin_id = int(query.data.split("_")[-1])
        
        session = Session()
        skin_to_delete = session.query(Skin).filter_by(id=skin_id).first()
        
        if skin_to_delete:
            session.delete(skin_to_delete)
            session.commit()
            session.close()
            
            await query.answer("Skin eliminata.")
        
        else:
            await query.answer("Skin non trovata.")

    except Exception as e:
        logging.error(f"Error deleting skin: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Errore durante l'eliminazione della skin.")

async def crea_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE, skin_id):
    try:
        session = Database().Session()
        skin = session.query(Skin).filter_by(id=skin_id).first()

        if skin:
            memo = f"Skin: {skin.name}"
            invoice_amount = skin.price

            invoice = wallet._post('addinvoice', data={'amt': invoice_amount, 'memo': memo})

            keyboard = [[InlineKeyboardButton("Controlla Stato Invoice", callback_data=f"check_invoice_{invoice['payment_request']}"[:63])]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Qui il tuo invoice per acquistare _{skin.name}_:\n```{invoice['payment_request']}```", parse_mode='markdown', reply_markup=reply_markup)

        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Skin non trovata.")

    except Exception as e:
        logging.error(f"Error creating invoice: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Errore durante la creazione dell'invoice.")

# Funzione per controllare periodicamente lo stato dell'invoice
async def controlla_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_request, skin_id):
    try:
        for _ in range(450):  # Controlla per 15 minuti (ogni 2 secondi)
            await asyncio.sleep(2)
            status = await controlla_stato_invoice(wallet, payment_request)

            if status == 'paid':
                await assegna_skin(update, context, skin_id)
                return
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Tempo scaduto per il pagamento dell'invoice.")

    except Exception as e:
        logging.error(f"Error checking invoice status: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Errore durante il controllo dello stato dell'invoice.")

async def assegna_skin(update: Update, context: ContextTypes.DEFAULT_TYPE, skin_id):
    try:
        # Assegnazione della skin all'utente dopo il pagamento
        user_id = update.effective_chat.id

        session = Session()
        existing_user_skin = session.query(UserSkin).filter_by(user_id=user_id, is_selected=True).first()

        if existing_user_skin:
            existing_user_skin.is_selected = False
        
        new_user_skin = session.query(UserSkin).filter_by(user_id=user_id, skin_id=skin_id).first()
        
        if new_user_skin:
            new_user_skin.is_selected = True
        else:
            new_user_skin = UserSkin(user_id=user_id, skin_id=skin_id, is_selected=True)
            session.add(new_user_skin)
        
        session.commit()
        session.close()

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ora stai usando la skin.")
    except Exception as e:
        logging.error(f"Error assigning skin: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Errore durante l'assegnazione della skin.")


async def usa_skin(update: Update, context: ContextTypes.DEFAULT_TYPE, skin_id):
    try:
        # Selezione della skin per l'utente
        user_id = update.effective_chat.id

        session = Session()
        existing_user_skin = session.query(UserSkin).filter_by(user_id=user_id, is_selected=True).first()

        if existing_user_skin:
            existing_user_skin.is_selected = False
        
        new_user_skin = session.query(UserSkin).filter_by(user_id=user_id, skin_id=skin_id).first()
        
        if new_user_skin:
            new_user_skin.is_selected = True
        else:
            new_user_skin = UserSkin(user_id=user_id, skin_id=skin_id, is_selected=True)
            session.add(new_user_skin)
        
        session.commit()
        session.close()

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ora stai usando la skin.")

    except Exception as e:
        logging.error(f"Error using skin: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Errore durante l'uso della skin.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN_DEL_BOT).build()
    
    function_handler = MessageHandler(None, callback=gestione_messaggi)
    application.add_handler(function_handler)

    callback_query_handler = CallbackQueryHandler(callback_handler)
    application.add_handler(callback_query_handler)

    application.run_polling()
