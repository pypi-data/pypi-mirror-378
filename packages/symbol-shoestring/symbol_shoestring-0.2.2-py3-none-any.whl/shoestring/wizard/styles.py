from prompt_toolkit.styles import Style


def initialize():
	"""Returns wizard styles."""

	return Style([
		('titlebar', 'fg:black bg:white'),
		('navigation', 'bg:ansiblue'),

		('button', 'bg:ansiwhite fg:ansigray'),
		('button button.focused', 'bg:white fg:black bold'),

		('button button.inactive', 'bg:ansired fg:ansired'),
		('button button.focused button.focused.inactive', 'bg:ansired fg:ansired'),

		('button.arrow', 'fg:ansiblue'),

		('tab-list', 'bg:white'),
		('tab', 'bg:ansigray'),
		('tab-selected', 'bold'),
		('tab-checked', 'bg:white'),

		('scrollbar.arrow', 'bold fg:black bg:ansiwhite'),
		('scrollbar.background', 'bg:ansigray'),
		('scrollbar.background scrollbar.start', 'bg:gray'),
		('scrollbar.button scrollbar.end', 'bg:gray'),
		('scrollbar.button', 'bg:ansibrightblack'),

		('error', 'fg:ansibrightred bold'),

		('shadow', 'bg:black fg:black')  # doesn't seem to be working
	])


def to_enabled_string(value):
	"""Formats a boolean value to describe an enabled/disabled toggle."""

	return _('wizard-toggle-enabled') if value else _('wizard-toggle-disabled')
