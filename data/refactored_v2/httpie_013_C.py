# === ARP Faza 4C - refactored code ===
# sample_id: httpie_013
# condition: C
# timestamp: 2026-06-04T14:03:17
# original_cc: 11, original_mi: None
# changed_pct: 0.4386
# === END HEADER ===
def _resolve_type_name(python_type) -> str:
    if hasattr(python_type, '__name__'):
        return python_type.__name__
    return type(python_type).__name__


def _resolve_options(aliases, configuration):
    if aliases:
        return {'options': aliases.copy()}
    return {'options': [configuration['metavar']], 'is_positional': True}


def _resolve_lazy_choices(aliases, configuration, isolation_mode):
    choices = LazyChoices(
        aliases,
        **{'dest': None, **configuration},
        isolation_mode=isolation_mode
    )
    configuration['choices'] = list(choices.load())
    configuration['help'] = choices.help


def serialize(self, *, isolation_mode: bool = False) -> Dict[str, Any]:
    configuration = self.configuration.copy()

    action = configuration.pop('action', None)
    short_help = configuration.pop('short_help', None)
    nested_options = configuration.pop('nested_options', None)

    if action == 'lazy_choices':
        _resolve_lazy_choices(self.aliases, configuration, isolation_mode)

    result = _resolve_options(self.aliases, configuration)

    qualifiers = JSON_QUALIFIER_TO_OPTIONS[configuration.get('nargs', Qualifiers.SUPPRESS)]
    result.update(qualifiers)

    description = configuration.get('help')
    if description and description is not Qualifiers.SUPPRESS:
        result['short_description'] = short_help
        result['description'] = description

    if nested_options:
        result['nested_options'] = nested_options

    python_type = configuration.get('type')
    if python_type is not None:
        result['python_type_name'] = _resolve_type_name(python_type)

    result.update({
        key: value
        for key, value in configuration.items()
        if key in JSON_DIRECT_MIRROR_OPTIONS
        if value is not Qualifiers.SUPPRESS
    })

    return result