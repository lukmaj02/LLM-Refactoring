# === ARP Faza 4C - refactored code ===
# sample_id: httpie_013
# condition: A
# timestamp: 2026-06-04T14:03:32
# original_cc: 11, original_mi: None
# changed_pct: 0.3077
# === END HEADER ===
def serialize(self, *, isolation_mode: bool = False) -> Dict[str, Any]:
    configuration = self.configuration.copy()
    self._handle_lazy_choices(configuration, isolation_mode)

    result = self._initialize_result(configuration)
    self._add_qualifiers(result, configuration)
    self._add_descriptions(result, configuration)
    self._add_nested_options(result, configuration)
    self._add_python_type(result, configuration)
    self._add_direct_mirror_options(result, configuration)

    return result

def _handle_lazy_choices(self, configuration, isolation_mode):
    action = configuration.pop('action', None)
    if action == 'lazy_choices':
        choices = LazyChoices(
            self.aliases,
            **{'dest': None, **configuration},
            isolation_mode=isolation_mode
        )
        configuration['choices'] = list(choices.load())
        configuration['help'] = choices.help

def _initialize_result(self, configuration):
    result = {}
    if self.aliases:
        result['options'] = self.aliases.copy()
    else:
        result['options'] = [configuration['metavar']]
        result['is_positional'] = True
    return result

def _add_qualifiers(self, result, configuration):
    qualifiers = JSON_QUALIFIER_TO_OPTIONS[configuration.get('nargs', Qualifiers.SUPPRESS)]
    result.update(qualifiers)

def _add_descriptions(self, result, configuration):
    short_help = configuration.pop('short_help', None)
    description = configuration.get('help')
    if description and description is not Qualifiers.SUPPRESS:
        result['short_description'] = short_help
        result['description'] = description

def _add_nested_options(self, result, configuration):
    nested_options = configuration.pop('nested_options', None)
    if nested_options:
        result['nested_options'] = nested_options

def _add_python_type(self, result, configuration):
    python_type = configuration.get('type')
    if python_type is not None:
        if hasattr(python_type, '__name__'):
            type_name = python_type.__name__
        else:
            type_name = type(python_type).__name__
        result['python_type_name'] = type_name

def _add_direct_mirror_options(self, result, configuration):
    result.update({
        key: value
        for key, value in configuration.items()
        if key in JSON_DIRECT_MIRROR_OPTIONS
        if value is not Qualifiers.SUPPRESS
    })