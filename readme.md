# @subito_crypto_bot

--- 

### Descrizione 

Bot per la gestione della chat, dal funzionamento molto semplice, in attesa del bot "grosso" che renderà il canale una webapp. Si vogliono inoltrare in un canale vetrina tutti gli annunci ("vendo", "cerco" e servizi), in modo da averli tutti in ordine in un unica fonte. Idem per i feedback, che vanno però in una chat diversa. Il bot legge lo stream di messaggi del gruppo e, tramite gli hashtag nel testo del messaggio, esegue di conseguenza. I messaggi originali sul gruppo vengono immediatamente eliminati, così da non avere doppioni. Il messaggio che finisce nei canali non è un forward diretto, ma un ex novo che all'annuncio aggiunge il tad dell'autore.

---

### src e funzionamento
Il bot è il file `/src/BOT.py`, `Deamonize.c`serve per creare un altro processo slegato dalla shell di partenza e far girare il bot in background. I/O (comprese le eccezioni non gestite) vengono dirottati a /dev/null.
```shell
pip install python-telegram-bot
gcc ./Deamonize.c -o deamonize
./deamonize python3 python-telegram-bot
```
in questo modo, dal momento che il bot gira su un raspberry a cui mi collego con ssh, il bot rimane attivo alla chiusura della connessione.

### Problemi Noti

1. Il bot ovviamento non fa controllo sul messaggio, ma guarda solo gli hashtag, c'è bisogno quindi di moderazione manuale sul contenuto.
2. Annunci mal formattati vengono ignorati
3. Mala gestione delle immagini (vedasi sezione TODOs)

---

### TODOs

 - [ ] Quando un annuncio contiene più immagini raggruppate, il bot gestisce solo la prima (o comunque quella che ha la didascalia), ignorando le altre. ciò significa che se un utente fa un annuncio con tre foto + testo, la prima viene inviata nel canale, le altre due si ritrovano orfane e senza didascalia nel gruppo, e vanno aggiunte manualmente in risposta al messaggio in canale. Non sono stato in grado di usare correttamente il metodo send_media_group(), se qualcuno è in grado apra PR (con commenti), grazie
 - [x] Utile sarebbe che l'autore dell'annuncio potesse rispondere allo stesso con "#trovato" o "#venduto" e che l'annuncio si eliminasse da solo di conseguenza.
       Funzionalità in parte implementata
 - [ ] Per altro, issues o pull request o gruppo brainstorming su telegram.

---

### DATABASE

Non potendo recuperare messaggi vecchi a partire dall'ID, è necessario un database che contenga quantomeno l'ID del messaggio, l'autore, il testo e la data di pubblicazione.
Questo per esempio è utile nel punto 2 dei TODOs: recuperando l'autore, ognuno può eliminarsi i suoi annunci, ora invece è comunque un admin che deve farlo
