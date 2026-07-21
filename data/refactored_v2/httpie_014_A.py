# === ARP Faza 4C - refactored code ===
# sample_id: httpie_014
# condition: A
# timestamp: 2026-06-04T14:03:57
# original_cc: 11, original_mi: None
# changed_pct: 0.8478
# === END HEADER ===
def interpret(context: Any, key: str, value: Any) -> Any:
    cursor = context
    paths = list(parse(key))
    paths.append(Path(PathAction.SET, value))

    for index, (path, next_path) in enumerate(zip(paths, paths[1:])):
        if cursor is None:
            context = cursor = _object_for(path.kind)
        if path.kind is PathAction.KEY:
            _handle_key_path(cursor, index, path, next_path, key, paths)
        elif path.kind is PathAction.INDEX:
            _handle_index_path(cursor, index, path, next_path, key, paths)
        elif path.kind is PathAction.APPEND:
            _handle_append_path(cursor, index, path, next_path, key, paths)
        else:
            assert_cant_happen()

    return context


def _type_check(cursor, index, path, expected_type, key, paths):
    if not isinstance(cursor, expected_type):
        pseudo_token = _create_pseudo_token(path)
        cursor_type = JSON_TYPE_MAPPING.get(type(cursor), type(cursor).__name__)
        required_type = JSON_TYPE_MAPPING[expected_type]
        message = (
            f'Cannot perform {path.kind.to_string()!r} based access on '
            f"{repr(''.join(path.reconstruct() for path in paths[:index]))} "
            f'which has a type of {cursor_type!r} but this operation '
            f'requires a type of {required_type!r}.'
        )
        raise NestedJSONSyntaxError(
            source=key,
            token=pseudo_token,
            message=message,
            message_kind='Type',
        )


def _create_pseudo_token(path):
    if path.tokens:
        return Token(
            kind=TokenKind.PSEUDO,
            value='',
            start=path.tokens[0].start,
            end=path.tokens[-1].end,
        )
    return None


def _object_for(kind: PathAction) -> Any:
    if kind is PathAction.KEY:
        return {}
    elif kind in {PathAction.INDEX, PathAction.APPEND}:
        return []
    else:
        assert_cant_happen()


def _handle_key_path(cursor, index, path, next_path, key, paths):
    _type_check(cursor, index, path, dict, key, paths)
    if next_path.kind is PathAction.SET:
        cursor[path.accessor] = next_path.accessor
    else:
        cursor = cursor.setdefault(path.accessor, _object_for(next_path.kind))


def _handle_index_path(cursor, index, path, next_path, key, paths):
    _type_check(cursor, index, path, list, key, paths)
    if path.accessor < 0:
        raise NestedJSONSyntaxError(
            source=key,
            token=path.tokens[1],
            message='Negative indexes are not supported.',
            message_kind='Value',
        )
    cursor.extend([None] * (path.accessor - len(cursor) + 1))
    if next_path.kind is PathAction.SET:
        cursor[path.accessor] = next_path.accessor
    else:
        if cursor[path.accessor] is None:
            cursor[path.accessor] = _object_for(next_path.kind)
        cursor = cursor[path.accessor]


def _handle_append_path(cursor, index, path, next_path, key, paths):
    _type_check(cursor, index, path, list, key, paths)
    if next_path.kind is PathAction.SET:
        cursor.append(next_path.accessor)
    else:
        cursor.append(_object_for(next_path.kind))
        cursor = cursor[-1]