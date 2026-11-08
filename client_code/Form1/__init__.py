from anvil import get_url_hash, handle, server, set_url_hash
from anvil.js.window import window

from ._anvil_designer import Form1Template


class Form1(Form1Template):
  CATEGORY_GOALS = {
    "salato": 9,
    "bibite": 6,
    "dolce": 6,
  }

  def __init__(self, **properties):
    super().__init__(**properties)

    self.category_dropdown.items = [
      ("🥗  Salato", "salato"),
      ("🥤  Bibite & snack", "bibite"),
      ("🍰  Dolce / frutta", "dolce"),
    ]
    self.category_dropdown.selected_value = "salato"
    self.selected_event = None
    self._events = []
    self._signups = []
    self._edit_token = None
    self._can_edit_event = False
    self.events_board.visible = True
    self.event_hero.visible = False
    self.event_detail.visible = False
    self.event_create_panel.visible = False
    self.event_edit_panel.visible = False
    self.edit_link_panel.visible = False
    self.event_edit_access_message.visible = False
    self._load_events()
    window.addEventListener("hashchange", self._handle_hash_change)
    self._route_from_hash()

  def _load_events(self):
    self._events = server.call("get_upcoming_events")
    self.events_panel.items = self._events
    self.events_empty.visible = not self._events

  def _slug_from_url_hash(self, url_hash):
    if isinstance(url_hash, dict):
      slug = url_hash.get("evento") or url_hash.get("event")
    else:
      slug = url_hash
    return slug.strip("/") if isinstance(slug, str) else ""

  def _handle_hash_change(self, event):
    self._route_from_hash()

  def _route_from_hash(self):
    url_hash = get_url_hash()
    slug = self._slug_from_url_hash(url_hash)
    edit_token = url_hash.get("modifica") if isinstance(url_hash, dict) else None
    if not slug:
      self._show_event_list()
      return

    event = server.call("get_event_by_slug", slug)
    if event is None:
      set_url_hash("")
      self._show_event_list()
      return

    can_edit = bool(
      edit_token
      and server.call("can_edit_meal_event", event["id"], edit_token)
    )
    self._edit_token = edit_token if can_edit else None
    self._select_event(
      event,
      can_edit=can_edit,
      invalid_edit_link=bool(edit_token) and not can_edit,
    )

  def _show_event_list(self):
    self.selected_event = None
    self._edit_token = None
    self._can_edit_event = False
    self.events_board.visible = True
    self.event_hero.visible = False
    self.event_detail.visible = False
    self.event_edit_panel.visible = False
    self.edit_link_panel.visible = False
    self.event_edit_access_message.visible = False
    self._show_message("")

  def _select_event(self, event, can_edit=False, invalid_edit_link=False):
    self.selected_event = event
    if event is None:
      self._signups = []
      self._show_signups()
      self._show_event_list()
      return

    self._can_edit_event = can_edit
    self.events_board.visible = False
    self.event_hero.visible = True
    self.event_detail.visible = True
    self.event_edit_panel.visible = False
    self.edit_event_button.visible = can_edit
    self.rotate_edit_link_button.visible = can_edit
    self.edit_link_panel.visible = can_edit
    self.event_edit_access_message.visible = invalid_edit_link
    if can_edit:
      self.event_edit_link_box.text = str(window.location.href)
    elif invalid_edit_link:
      self.event_edit_access_message.text = (
        "Link di modifica non valido o revocato. Puoi comunque consultare l'evento."
      )
    else:
      self.event_edit_link_box.text = ""

    self.event_title.text = event["title"]
    description = event["description"] or ""
    self.event_description.text = description or "Ogni evento ha la sua lista di portate condivise."
    event_date = event["event_date"]
    self.event_date_label.text = (
      "Data da definire" if event_date is None else event_date.strftime("%d/%m/%Y")
    )
    self.event_date_label.visible = True
    location = event["location"] or ""
    self.event_location_label.text = "📍 " + location
    self.event_location_label.visible = bool(location)
    self._load_signups()

  def _load_signups(self):
    if self.selected_event is None:
      self._signups = []
    else:
      self._signups = server.call(
        "get_meal_signups", self.selected_event["id"]
      )
    self._show_signups()

  def _show_signups(self):
    category_panels = {
      "salato": (self.salato_panel, self.salato_empty, self.salato_count),
      "bibite": (self.bibite_panel, self.bibite_empty, self.bibite_count),
      "dolce": (self.dolce_panel, self.dolce_empty, self.dolce_count),
    }

    for category, (panel, empty_label, count_label) in category_panels.items():
      rows = [row for row in self._signups if row["category"] == category]
      goal = self.CATEGORY_GOALS[category]
      panel.items = rows
      empty_label.visible = not rows
      count_label.text = "{} / {} adesioni".format(len(rows), goal)

    self.total_count.text = str(len(self._signups))

  def _show_message(self, message):
    self.form_message.text = message
    self.form_message.visible = bool(message)

  def _show_event_message(self, message):
    self.event_form_message.text = message
    self.event_form_message.visible = bool(message)

  def _show_event_edit_message(self, message):
    self.event_edit_message.text = message
    self.event_edit_message.visible = bool(message)

  @handle("events_panel", "x-select-event")
  def events_panel_select_event(self, selected_event, **event_args):
    set_url_hash("/" + selected_event["slug"])

  @handle("back_to_events_button", "click")
  def back_to_events_button_click(self, **event_args):
    set_url_hash("")

  @handle("toggle_create_event_button", "click")
  def toggle_create_event_button_click(self, **event_args):
    self.event_create_panel.visible = not self.event_create_panel.visible
    self.toggle_create_event_button.text = (
      "Annulla" if self.event_create_panel.visible else "+ Crea un evento"
    )
    self._show_event_message("")

  @handle("edit_event_button", "click")
  def edit_event_button_click(self, **event_args):
    if self.selected_event is None or not self._can_edit_event:
      return

    self.edit_event_title_box.text = self.selected_event["title"] or ""
    self.edit_event_date_picker.date = self.selected_event["event_date"]
    self.edit_event_location_box.text = self.selected_event["location"] or ""
    self.edit_event_description_box.text = self.selected_event["description"] or ""
    self._show_event_edit_message("")
    self.event_edit_panel.visible = True

  @handle("cancel_event_edit_button", "click")
  def cancel_event_edit_button_click(self, **event_args):
    self.event_edit_panel.visible = False
    self._show_event_edit_message("")

  @handle("save_event_changes_button", "click")
  def save_event_changes_button_click(self, **event_args):
    if self.selected_event is None or not self._can_edit_event:
      self._show_event_edit_message("Apri il link privato di modifica per continuare.")
      return

    title = (self.edit_event_title_box.text or "").strip()
    event_date = self.edit_event_date_picker.date
    location = (self.edit_event_location_box.text or "").strip()
    description = (self.edit_event_description_box.text or "").strip()

    if not title:
      self._show_event_edit_message("Scrivi il nome dell'evento.")
      return
    if event_date is None:
      self._show_event_edit_message("Scegli la data dell'evento.")
      return

    self.save_event_changes_button.enabled = False
    try:
      result = server.call(
        "update_meal_event",
        self.selected_event["id"],
        self._edit_token,
        title,
        event_date,
        location,
        description,
      )
      if not result["ok"]:
        self._show_event_edit_message(result["message"])
        return

      updated_event = server.call("get_event_by_slug", result["slug"])
      self._load_events()
      self._select_event(updated_event, can_edit=True)
    finally:
      self.save_event_changes_button.enabled = True

  @handle("rotate_edit_link_button", "click")
  def rotate_edit_link_button_click(self, **event_args):
    if self.selected_event is None or not self._can_edit_event or not self._edit_token:
      return
    if not window.confirm(
      "Il link attuale smetterà di funzionare. Vuoi generarne uno nuovo?"
    ):
      return

    self.rotate_edit_link_button.enabled = False
    try:
      result = server.call(
        "rotate_meal_event_edit_token",
        self.selected_event["id"],
        self._edit_token,
      )
      if not result["ok"]:
        self.event_edit_access_message.text = result["message"]
        self.event_edit_access_message.visible = True
        return

      set_url_hash(
        {
          "evento": self.selected_event["slug"],
          "modifica": result["edit_token"],
        }
      )
    finally:
      self.rotate_edit_link_button.enabled = True

  @handle("create_event_button", "click")
  def create_event_button_click(self, **event_args):
    title = (self.event_title_box.text or "").strip()
    event_date = self.event_date_picker.date
    location = (self.event_location_box.text or "").strip()
    description = (self.event_description_box.text or "").strip()

    if not title:
      self._show_event_message("Scrivi il nome dell'evento.")
      return
    if event_date is None:
      self._show_event_message("Scegli la data dell'evento.")
      return

    self.create_event_button.enabled = False
    try:
      result = server.call(
        "create_meal_event", title, event_date, location, description
      )
      if not result["ok"]:
        self._show_event_message(result["message"])
        return

      self.event_title_box.text = ""
      self.event_date_picker.date = None
      self.event_location_box.text = ""
      self.event_description_box.text = ""
      self.event_create_panel.visible = False
      self.toggle_create_event_button.text = "+ Crea un evento"
      self._show_event_message("")
      set_url_hash(
        {"evento": result["slug"], "modifica": result["edit_token"]}
      )
      self._load_events()
    finally:
      self.create_event_button.enabled = True

  @handle("submit_button", "click")
  def submit_button_click(self, **event_args):
    name = (self.name_box.text or "").strip()
    dish = (self.dish_box.text or "").strip()
    notes = (self.notes_box.text or "").strip()
    category = self.category_dropdown.selected_value

    if self.selected_event is None:
      self._show_message("Seleziona prima un evento.")
      return

    if not name:
      self._show_message("Scrivi il tuo nome per aggiungere la portata.")
      return
    if not dish:
      self._show_message("Descrivi brevemente cosa porterai.")
      return

    self.submit_button.enabled = False
    try:
      result = server.call(
        "save_meal_signup",
        self.selected_event["id"],
        name,
        category,
        dish,
        notes,
      )
      if not result["ok"]:
        self._show_message(result["message"])
        return

      self.name_box.text = ""
      self.dish_box.text = ""
      self.notes_box.text = ""
      self._load_signups()
      if result["updated"]:
        self._show_message("La tua scelta è stata aggiornata. Grazie!")
      else:
        self._show_message("Fatto! La tua portata è in lista. Grazie!")
    finally:
      self.submit_button.enabled = True

  @handle("refresh_button", "click")
  def refresh_button_click(self, **event_args):
    self._load_signups()
    self._show_message("Lista aggiornata.")
