from datetime import date
import re
import unicodedata

import anvil.server
import anvil.tables
from anvil.tables import app_tables, query


CATEGORIES = {"salato", "bibite", "dolce"}
LEGACY_EVENT_TITLE = "Bivacco percorso senior 2026"


def _attach_legacy_signups():
  unassigned = [
    row for row in app_tables.meal_signups.search(query.fetch_only("event"))
    if row["event"] is None
  ]
  if not unassigned:
    return

  legacy_events = list(app_tables.events.search(
    query.fetch_only("title", "event_date", "location", "description"),
    title=LEGACY_EVENT_TITLE,
  ))
  if legacy_events:
    legacy_event = legacy_events[0]
  else:
    legacy_event = app_tables.events.add_row(
      title=LEGACY_EVENT_TITLE,
      event_date=None,
      location="",
      description="Evento preesistente, migrato dalla lista condivisa.",
    )

  for row in unassigned:
    row["event"] = legacy_event


def _slug_base(title):
  normalized = unicodedata.normalize("NFKD", title)
  ascii_title = normalized.encode("ascii", "ignore").decode("ascii").lower()
  return re.sub(r"[^a-z0-9]+", "-", ascii_title).strip("-") or "evento"


def _ensure_event_slugs():
  used_slugs = set()
  events = app_tables.events.search(query.fetch_only("title", "slug"))

  for event in events:
    slug = event["slug"]
    if isinstance(slug, str) and slug and slug not in used_slugs:
      used_slugs.add(slug)
      continue

    base = _slug_base(event["title"] or "")
    slug = base
    suffix = 2
    while slug in used_slugs:
      slug = "{}-{}".format(base, suffix)
      suffix += 1
    event["slug"] = slug
    used_slugs.add(slug)

  return used_slugs


def _next_event_slug(title, used_slugs):
  base = _slug_base(title)
  slug = base
  suffix = 2
  while slug in used_slugs:
    slug = "{}-{}".format(base, suffix)
    suffix += 1
  return slug


@anvil.server.callable
@anvil.tables.in_transaction
def get_upcoming_events():
  _attach_legacy_signups()
  _ensure_event_slugs()
  today = date.today()
  events = list(app_tables.events.search(
    query.fetch_only("title", "event_date", "location", "description", "slug")
  ))
  upcoming = [
    event for event in events
    if event["event_date"] is None or event["event_date"] >= today
  ]
  return sorted(
    upcoming,
    key=lambda event: (
      event["event_date"] is None,
      event["event_date"] or date.max,
      event["title"].casefold(),
    ),
  )


@anvil.server.callable
@anvil.tables.in_transaction
def get_event_by_slug(slug):
  if not isinstance(slug, str) or not slug:
    return None

  _attach_legacy_signups()
  _ensure_event_slugs()
  for event in app_tables.events.search(slug=slug):
    return event
  return None


def _find_event(event_id):
  if not isinstance(event_id, str) or not event_id:
    return None
  return app_tables.events.get_by_id(event_id)


@anvil.server.callable
def get_meal_signups(event_id):
  event = _find_event(event_id)
  if event is None:
    return []
  return list(app_tables.meal_signups.search(
    query.fetch_only("name", "category", "dish", "notes"),
    event=event,
  ))


@anvil.server.callable
@anvil.tables.in_transaction
def create_meal_event(title, event_date, location="", description=""):
  if not all(isinstance(value, str) for value in (title, location, description)):
    return {"ok": False, "message": "Controlla i dati inseriti e riprova."}

  title = title.strip()
  location = location.strip()
  description = description.strip()

  if not title:
    return {"ok": False, "message": "Inserisci il nome dell'evento."}
  if len(title) > 120:
    return {"ok": False, "message": "Il nome può contenere al massimo 120 caratteri."}
  if not isinstance(event_date, date):
    return {"ok": False, "message": "Scegli la data dell'evento."}
  if event_date < date.today():
    return {"ok": False, "message": "La data deve essere oggi o successiva."}
  if len(location) > 120:
    return {"ok": False, "message": "Il luogo può contenere al massimo 120 caratteri."}
  if len(description) > 1000:
    return {"ok": False, "message": "La descrizione può contenere al massimo 1000 caratteri."}

  used_slugs = _ensure_event_slugs()
  slug = _next_event_slug(title, used_slugs)
  event = app_tables.events.add_row(
    title=title,
    event_date=event_date,
    location=location,
    description=description,
    slug=slug,
  )
  return {"ok": True, "event": event}


@anvil.server.callable
@anvil.tables.in_transaction
def save_meal_signup(event_id, name, category, dish, notes=""):
  if not all(isinstance(value, str) for value in (name, category, dish, notes)):
    return {"ok": False, "message": "Controlla i dati inseriti e riprova."}

  event = _find_event(event_id)
  if event is None:
    return {"ok": False, "message": "Seleziona un evento valido."}

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

  for row in app_tables.meal_signups.search(
    query.fetch_only("name"),
    event=event,
  ):
    if row["name"].strip().casefold() == name.casefold():
      row.update(event=event, category=category, dish=dish, notes=notes)
      return {"ok": True, "updated": True}

  app_tables.meal_signups.add_row(
    name=name,
    category=category,
    dish=dish,
    notes=notes,
    event=event,
  )
  return {"ok": True, "updated": False}
