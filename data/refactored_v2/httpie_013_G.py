# === ARP Faza 4C - refactored code ===
# sample_id: httpie_013
# condition: G
# timestamp: 2026-06-04T14:02:26
# original_cc: 11, original_mi: None
# changed_pct: 0.8485
# === END HEADER ===
def _process_lazy_choices(self, configuration: Dict[str, Any], action: Any, isolation_mode: bool) -> None:
        if action == 'lazy_choices':
            choices = LazyChoices(
                self.aliases,
                **{'dest': None, **configuration},
                isolation_mode=isolation_mode
            )
            configuration['choices'] = list(choices.load())
            configuration['help'] = choices.help

    def _set_options_and_positional(self, result: Dict[str, Any], configuration: Dict[str, Any]) -> None:
        if self.aliases:
            result['options'] = self.aliases.copy()
        else:
            result['options'] = [configuration['metavar']]
            result['is_positional'] = True

    def _update_qualifiers(self, result: Dict[str, Any], configuration: Dict[str, Any]) -> None:
        qualifiers = JSON_QUALIFIER_TO_OPTIONS[configuration.get('nargs', Qualifiers.SUPPRESS)]
        result.update(qualifiers)

    def _set_description_fields(self, result: Dict[str, Any], configuration: Dict[str, Any], short_help: Optional[str]) -> None:
        description = configuration.get('help')
        if description and description is not Qualifiers.SUPPRESS:
            result['short_description'] = short_help
            result['description'] = description

    def _set_nested_options(self, result: Dict[str, Any], nested_options: Any) -> None:
        if nested_options:
            result['nested_options'] = nested_options

    def _set_python_type_name(self, result: Dict[str, Any], configuration: Dict[str, Any]) -> None:
        python_type = configuration.get('type')
        if python_type is not None:
            if hasattr(python_type, '__name__'):
                type_name = python_type.__name__
            else:
                type_name = type(python_type).__name__
            result['python_type_name'] = type_name

    def _mirror_direct_options(self, result: Dict[str, Any], configuration: Dict[str, Any]) -> None:
        result.update({
            key: value
            for key, value in configuration.items()
            if key in JSON_DIRECT_MIRROR_OPTIONS
            if value is not Qualifiers.SUPPRESS
        })

    def serialize(self, *, isolation_mode: bool = False) -> Dict[str, Any]:
        configuration = self.configuration.copy()

        action = configuration.pop('action', None)
        short_help = configuration.pop('short_help', None)
        nested_options = configuration.pop('nested_options', None)

        self._process_lazy_choices(configuration, action, isolation_mode)

        result = {}
        self._set_options_and_positional(result, configuration)
        self._update_qualifiers(result, configuration)
        self._set_description_fields(result, configuration, short_help)
        self._set_nested_options(result, nested_options)
        self._set_python_type_name(result, configuration)
        self._mirror_direct_options(result, configuration)

        return result