from anvil import handle

from ._anvil_designer import EventItemTemplate


class EventItem(EventItemTemplate):
  def __init__(self, **properties):
    super().__init__(**properties)

    event_date = self.item["event_date"]
    self.event_date_label.text = (
      "Data da definire" if event_date is None else event_date.strftime("%d/%m/%Y")
    )
    location = self.item["location"] or ""
    self.event_location_label.text = "📍 " + location
    self.event_location_label.visible = bool(location)
    description = self.item["description"] or ""
    self.event_description_label.text = description
    self.event_description_label.visible = bool(description)

  @handle("open_event_button", "click")
  def open_event_button_click(self, **event_args):
    self.parent.raise_event("x-select-event", selected_event=self.item)
