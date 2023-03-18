# @subito_crypto_bot

--- 

### Descrizione 

Bot per la gestione della chat, dal funzionamento molto semplice, in attesa del bot "grosso" che renderà il canale una webapp. Si vogliono inoltrare in un canale vetrina tutti gli annunci ("vendo", "cerco" e servizi), in modo da averli tutti in ordine in un unica fonte. Idem per i feedback, che vanno però in una chat diversa. Il bot legge lo stream di messaggi del gruppo e, tramite gli hashtag nel testo del messaggio, esegue di conseguenza. I messaggi originali sul gruppo vengono immediatamente eliminati, così da non avere doppioni. Il messaggio che finisce nei canali non è un forward diretto, ma un ex novo che all'annuncio aggiunge il tad dell'autore.

---

### Problemi Noti

1. Il bot ovviamento non fa controllo sul messaggio, ma guarda solo gli hashtag, c'è bisogno quindi di moderazione manuale sul contenuto.
2. Annunci mal formattati vengono ignorati
3. Mala gestione delle immagini (vedasi sezione TODOs)

---

### TODOs

1. Quando un annuncio contiene più immagini raggruppate, il bot gestisce solo la prima (o comunque quella che ha la didascalia), ignorando le altre. ciò significa che se un utente fa un annuncio con tre foto + testo, la prima viene inviata nel canale, le altre due si ritrovano orfane e senza didascalia nel gruppo, e vanno aggiunte manualmente in risposta al messaggio in canale. Non sono stato in grado di usare correttamente il metodo send_media_group(), se qualcuno è in grado apra PR (con commenti), grazie
2. per altro, issues o pr o brainstorming su telegram.