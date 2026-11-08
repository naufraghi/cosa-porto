# Cosa porto?

Un'app per coordinare chi porta cosa durante un evento o una riunione di gruppo.

Crea un evento, condividi la lista dei contributi e lascia che i partecipanti aggiungano cosa porteranno. Così il gruppo può organizzarsi senza sovrapporre le proposte.

## A cosa serve

La puoi usare per cene tra amici o colleghi, feste, pranzi condivisi, picnic e altri eventi di gruppo.

Ogni evento ha una propria lista di adesioni, divisa per categoria:
- salato
- bibite e snack
- dolce e frutta

## Funzionalità principali

- creare eventi con titolo, data e luogo
- consultare gli eventi futuri
- aprire un evento e vedere le adesioni
- aggiungere la propria portata indicando nome, categoria e note
- aggiornare la propria scelta
- tenere traccia delle adesioni per categoria

## Come funziona

1. Apri l'app e seleziona un evento.
2. Inserisci il tuo nome e cosa porterai.
3. Scegli una categoria: salato, bibite e snack, oppure dolce e frutta.
4. Aggiungi eventuali note.
5. La lista mostra i contributi registrati; puoi aggiornarla con il pulsante dedicato.

## Esempio

Per una **Cena di primavera** organizzata il 18 maggio a **Casa di Luca**, le persone potrebbero aggiungere alla lista:
- Giulia — torta salata alle verdure (salato)
- Marco — bibite e patatine (bibite e snack)
- Sara — crostata di fragole (dolce e frutta)

I nomi e i contributi sono esempi: ogni partecipante può inserire i propri.

## Tecnologie

L'app è costruita con Anvil e usa un backend Python per gestire eventi, adesioni e aggiornamenti delle scelte.

## Aprire l'app

1. Clona questo repository in Anvil.
2. Apri il progetto nell'editor di Anvil.
3. Avvia l'app con il pulsante **Run**.
4. Crea un evento e invita i partecipanti ad aggiungere i loro contributi.

## Struttura del progetto

- `client_code/` — interfaccia e logica frontend
- `server_code/meal_signups.py` — logica backend per eventi e adesioni
- `anvil.yaml` — configurazione dell'app Anvil

## Licenza

Questo progetto è distribuito con la licenza indicata in `LICENSE.txt`.
