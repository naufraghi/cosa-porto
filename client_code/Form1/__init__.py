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
    self._load_signups()

  def _load_signups(self):
    self._signups = server.call("get_meal_signups")
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

  @handle("submit_button", "click")
  def submit_button_click(self, **event_args):
    name = (self.name_box.text or "").strip()
    dish = (self.dish_box.text or "").strip()
    notes = (self.notes_box.text or "").strip()
    category = self.category_dropdown.selected_value

    if not name:
      self._show_message("Scrivi il tuo nome per aggiungere la portata.")
      return
    if not dish:
      self._show_message("Descrivi brevemente cosa porterai.")
      return

    self.submit_button.enabled = False
    try:
      result = server.call("save_meal_signup", name, category, dish, notes)
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
