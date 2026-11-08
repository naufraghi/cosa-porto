# Cosa porto?

Un'app per organizzare i pasti condivisi tra un gruppo di persone.

L'obiettivo è semplice: creare un evento, condividere la lista delle portate, e permettere a tutti di aggiungere in modo rapido la propria disponibilità senza duplicare le proposte.

## A cosa serve

Questa web app è pensata per situazioni come:
- cene tra amici o colleghi
- eventi organizzati in gruppo
- barbecue, feste, pranzi condivisi
- riunioni in cui si vuole coordinare chi porta cosa

Ogni evento ha una sua lista di adesioni, divisa per categoria:
- salato
- bibite e snack
- dolce e frutta

## Funzionalità principali

- creare nuovi eventi con titolo, data e luogo
- vedere la lista degli eventi futuri
- aprire un evento e controllare le adesioni
- aggiungere la propria portata indicando nome, categoria e note
- aggiornare la propria scelta se si cambia idea
- tenere traccia di quante persone hanno già aderito per categoria

## Come funziona

1. Apri l'app e seleziona un evento.
2. Inserisci il tuo nome e descrivi cosa porterai.
3. Scegli la categoria giusta:
   - salato
   - bibite e snack
   - dolce / frutta
4. Se necessario, aggiungi note extra.
5. La lista si aggiorna in tempo reale, così tutti possono vedere chi ha già preso parte.

## Esempio di flusso

- un evento viene creato con un nome e una data
- i partecipanti aprono la pagina dell'evento
- ognuno registra il proprio contributo
- la lista mostra subito i piatti già assegnati e le categorie ancora da riempire

## Tecnologie

L'app è costruita con Anvil e usa un backend Python per gestire:
- la creazione degli eventi
- la ricerca degli eventi futuri
- la registrazione delle adesioni
- l'aggiornamento delle scelte esistenti

## Aprire l'app

1. Clona questo repository in Anvil
2. Apri il progetto nell'editor di Anvil
3. Esegui l'applicazione con il pulsante Run
4. Inizia a creare eventi e raccogliere le adesioni

## Struttura del progetto

- `client_code/` — interfaccia utente e logica frontend
- `server_code/meal_signups.py` — logica di backend per eventi e adesioni
- `anvil.yaml` — configurazione dell'app Anvil

## Licenza

Questo progetto è distribuito con licenza disponibile in `LICENSE.txt`.

## Nota

La repo è pensata come un piccolo strumento pratico per organizzare la condivisione di cibo in gruppo, senza bisogno di registri separati o messaggi sparsi.
