from datetime import date
import hashlib
import hmac
import re
import secrets
import unicodedata

import anvil.server
import anvil.tables
from anvil.tables import app_tables, query


CATEGORIES = {"salato", "bibite", "dolce"}


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
  _ensure_event_slugs()
  today = date.today()
  events = list(app_tables.events.search(
    query.fetch_only("title", "event_date", "location", "description", "slug")
  ))
  upcoming = [
    event for event in events
    if event["event_date"] is None or event["event_date"] >= today
  ]
  upcoming = sorted(
    upcoming,
    key=lambda event: (
      event["event_date"] is None,
      event["event_date"] or date.max,
      event["title"].casefold(),
    ),
  )
  return [_public_event_data(event) for event in upcoming]


@anvil.server.callable
@anvil.tables.in_transaction
def get_event_by_slug(slug):
  if not isinstance(slug, str) or not slug:
    return None

  _ensure_event_slugs()
  for event in app_tables.events.search(
    query.fetch_only("title", "event_date", "location", "description", "slug"),
    slug=slug,
  ):
    return _public_event_data(event)
  return None


def _find_event(event_id):
  if not isinstance(event_id, str) or not event_id:
    return None
  return app_tables.events.get_by_id(event_id)


def _public_event_data(event):
  return {
    "id": event.get_id(),
    "title": event["title"],
    "event_date": event["event_date"],
    "location": event["location"],
    "description": event["description"],
    "slug": event["slug"],
  }


def _hash_edit_token(token):
  return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _is_valid_edit_token(event, token):
  stored_hash = event["edit_token_hash"]
  if not isinstance(token, str) or not token or not isinstance(stored_hash, str):
    return False
  return hmac.compare_digest(stored_hash, _hash_edit_token(token))


def _validate_event_fields(title, event_date, location, description):
  if not title:
    return "Inserisci il nome dell'evento."
  if len(title) > 120:
    return "Il nome può contenere al massimo 120 caratteri."
  if not isinstance(event_date, date):
    return "Scegli la data dell'evento."
  if event_date < date.today():
    return "La data deve essere oggi o successiva."
  if len(location) > 120:
    return "Il luogo può contenere al massimo 120 caratteri."
  if len(description) > 1000:
    return "La descrizione può contenere al massimo 1000 caratteri."
  return None


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

  validation_message = _validate_event_fields(
    title, event_date, location, description
  )
  if validation_message:
    return {"ok": False, "message": validation_message}

  used_slugs = _ensure_event_slugs()
  slug = _next_event_slug(title, used_slugs)
  edit_token = secrets.token_urlsafe(32)
  event = app_tables.events.add_row(
    title=title,
    event_date=event_date,
    location=location,
    description=description,
    slug=slug,
    edit_token_hash=_hash_edit_token(edit_token),
  )
  return {"ok": True, "slug": slug, "edit_token": edit_token}


@anvil.server.callable
def can_edit_meal_event(event_id, edit_token):
  event = _find_event(event_id)
  return event is not None and _is_valid_edit_token(event, edit_token)


@anvil.server.callable
@anvil.tables.in_transaction
def update_meal_event(
  event_id, edit_token, title, event_date, location="", description=""
):
  event = _find_event(event_id)
  if event is None or not _is_valid_edit_token(event, edit_token):
    return {"ok": False, "message": "Link di modifica non valido o revocato."}

  if not all(isinstance(value, str) for value in (title, location, description)):
    return {"ok": False, "message": "Controlla i dati inseriti e riprova."}

  title = title.strip()
  location = location.strip()
  description = description.strip()
  validation_message = _validate_event_fields(
    title, event_date, location, description
  )
  if validation_message:
    return {"ok": False, "message": validation_message}

  event.update(
    title=title,
    event_date=event_date,
    location=location,
    description=description,
  )
  return {"ok": True, "slug": event["slug"]}


@anvil.server.callable
@anvil.tables.in_transaction
def rotate_meal_event_edit_token(event_id, edit_token):
  event = _find_event(event_id)
  if event is None or not _is_valid_edit_token(event, edit_token):
    return {"ok": False, "message": "Link di modifica non valido o revocato."}

  new_edit_token = secrets.token_urlsafe(32)
  event["edit_token_hash"] = _hash_edit_token(new_edit_token)
  return {"ok": True, "edit_token": new_edit_token}


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
