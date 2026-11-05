from ._anvil_designer import SignupItemTemplate


class SignupItem(SignupItemTemplate):
  def __init__(self, **properties):
    super().__init__(**properties)
