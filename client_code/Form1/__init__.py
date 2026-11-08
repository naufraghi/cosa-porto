from anvil import handle, server

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
    self.event_create_panel.visible = False
    self._load_events()

  def _load_events(self, selected_event_id=None):
    self._events = server.call("get_upcoming_events")
    self.events_panel.items = self._events
    self.events_empty.visible = not self._events

    if selected_event_id is None and self.selected_event is not None:
      selected_event_id = self.selected_event.get_id()

    selected_event = None
    if selected_event_id is not None:
      selected_event = next(
        (event for event in self._events if event.get_id() == selected_event_id),
        None,
      )
    if selected_event is None and self._events:
      selected_event = self._events[0]

    self._select_event(selected_event)

  def _select_event(self, event):
    self.selected_event = event
    self.event_detail.visible = event is not None
    if event is None:
      self.event_title.text = "Scegli un evento"
      self.event_description.text = "Crea un evento o seleziona una condivisione dalla lista."
      self.event_date_label.visible = False
      self.event_location_label.visible = False
      self._signups = []
      self._show_signups()
      return

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
        "get_meal_signups", self.selected_event.get_id()
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

  @handle("events_panel", "x-select-event")
  def events_panel_select_event(self, selected_event, **event_args):
    self._select_event(selected_event)

  @handle("toggle_create_event_button", "click")
  def toggle_create_event_button_click(self, **event_args):
    self.event_create_panel.visible = not self.event_create_panel.visible
    self.toggle_create_event_button.text = (
      "Annulla" if self.event_create_panel.visible else "+ Crea un evento"
    )
    self._show_event_message("")

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

      created_event_id = result["event"].get_id()
      self.event_title_box.text = ""
      self.event_date_picker.date = None
      self.event_location_box.text = ""
      self.event_description_box.text = ""
      self.event_create_panel.visible = False
      self.toggle_create_event_button.text = "+ Crea un evento"
      self._show_event_message("")
      self._load_events(selected_event_id=created_event_id)
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
        self.selected_event.get_id(),
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
