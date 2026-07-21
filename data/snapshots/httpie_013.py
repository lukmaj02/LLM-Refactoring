# SNAPSHOT METADATA
# sample_id: httpie_013
# repo: httpie
# file: data/repos/httpie/httpie/cli/options.py
# function: Argument.serialize
# cc: 11 | mi: N/A | loc: 53
# extracted: 2026-05-01T11:47:36

def serialize(self, *, isolation_mode: bool = False) -> Dict[str, Any]:
    configuration = self.configuration.copy()

    # Unpack the dynamically computed choices, since we
    # will need to store the actual values somewhere.
    action = configuration.pop('action', None)
    short_help = configuration.pop('short_help', None)
    nested_options = configuration.pop('nested_options', None)

    if action == 'lazy_choices':
        choices = LazyChoices(
            self.aliases,
            **{'dest': None, **configuration},
            isolation_mode=isolation_mode
        )
        configuration['choices'] = list(choices.load())
        configuration['help'] = choices.help

    result = {}
    if self.aliases:
        result['options'] = self.aliases.copy()
    else:
        result['options'] = [configuration['metavar']]
        result['is_positional'] = True

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
        if hasattr(python_type, '__name__'):
            type_name = python_type.__name__
        else:
            type_name = type(python_type).__name__

        result['python_type_name'] = type_name

    result.update({
        key: value
        for key, value in configuration.items()
        if key in JSON_DIRECT_MIRROR_OPTIONS
        if value is not Qualifiers.SUPPRESS
    })

    return result
