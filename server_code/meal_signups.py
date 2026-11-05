import anvil.server
import anvil.tables
from anvil.tables import app_tables, query


CATEGORIES = {"salato", "bibite", "dolce"}


@anvil.server.callable
def get_meal_signups():
  return list(app_tables.meal_signups.search(
    query.fetch_only("name", "category", "dish", "notes")
  ))


@anvil.server.callable
@anvil.tables.in_transaction
def save_meal_signup(name, category, dish, notes=""):
  if not all(isinstance(value, str) for value in (name, category, dish, notes)):
    return {"ok": False, "message": "Controlla i dati inseriti e riprova."}

  name = name.strip()
  dish = dish.strip()
  notes = notes.strip()

  if not name:
    return {"ok": False, "message": "Inserisci il tuo nome."}
  if len(name) > 80:
    return {"ok": False, "message": "Il nome può contenere al massimo 80 caratteri."}
  if category not in CATEGORIES:
    return {"ok": False, "message": "Scegli una delle tre categorie."}
  if not dish:
    return {"ok": False, "message": "Descrivi brevemente il piatto."}
  if len(dish) > 120:
    return {"ok": False, "message": "La descrizione del piatto può contenere al massimo 120 caratteri."}
  if len(notes) > 300:
    return {"ok": False, "message": "Le note possono contenere al massimo 300 caratteri."}

  for row in app_tables.meal_signups.search(query.fetch_only("name")):
    if row["name"].strip().casefold() == name.casefold():
      row.update(category=category, dish=dish, notes=notes)
      return {"ok": True, "updated": True}

  app_tables.meal_signups.add_row(
    name=name,
    category=category,
    dish=dish,
    notes=notes,
  )
  return {"ok": True, "updated": False}
