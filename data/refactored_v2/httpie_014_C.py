# === ARP Faza 4C - refactored code ===
# sample_id: httpie_014
# condition: C
# timestamp: 2026-06-04T14:03:39
# original_cc: 11, original_mi: None
# changed_pct: 0.8113
# === END HEADER ===
def _make_pseudo_token(path):
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


def _make_type_check(key, paths, cursor_ref):
    def type_check(index: int, path: Path, expected_type: JSONType):
        cursor = cursor_ref[0]
        if not isinstance(cursor, expected_type):
            pseudo_token = _make_pseudo_token(path)
            cursor_type = JSON_TYPE_MAPPING.get(type(cursor), type(cursor).__name__)
            required_type = JSON_TYPE_MAPPING[expected_type]
            message = f'Cannot perform {path.kind.to_string()!r} based access on '
            message += repr(''.join(p.reconstruct() for p in paths[:index]))
            message += f' which has a type of {cursor_type!r} but this operation'
            message += f' requires a type of {required_type!r}.'
            raise NestedJSONSyntaxError(
                source=key,
                token=pseudo_token,
                message=message,
                message_kind='Type',
            )
    return type_check


def _handle_key_path(cursor, path, next_path, type_check, index):
    type_check(index, path, dict)
    if next_path.kind is PathAction.SET:
        cursor[path.accessor] = next_path.accessor
        return cursor, True
    cursor = cursor.setdefault(path.accessor, _object_for(next_path.kind))
    return cursor, False


def _handle_index_path(cursor, path, next_path, type_check, index, key):
    type_check(index, path, list)
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
        return cursor, True
    if cursor[path.accessor] is None:
        cursor[path.accessor] = _object_for(next_path.kind)
    cursor = cursor[path.accessor]
    return cursor, False


def _handle_append_path(cursor, path, next_path, type_check, index):
    type_check(index, path, list)
    if next_path.kind is PathAction.SET:
        cursor.append(next_path.accessor)
        return cursor, True
    cursor.append(_object_for(next_path.kind))
    cursor = cursor[-1]
    return cursor, False


def interpret(context: Any, key: str, value: Any) -> Any:
    cursor = context
    paths = list(parse(key))
    paths.append(Path(PathAction.SET, value))

    cursor_ref = [cursor]
    type_check = _make_type_check(key, paths, cursor_ref)

    for index, (path, next_path) in enumerate(zip(paths, paths[1:])):
        if cursor is None:
            context = cursor = _object_for(path.kind)

        cursor_ref[0] = cursor

        if path.kind is PathAction.KEY:
            cursor, done = _handle_key_path(cursor, path, next_path, type_check, index)
        elif path.kind is PathAction.INDEX:
            cursor, done = _handle_index_path(cursor, path, next_path, type_check, index, key)
        elif path.kind is PathAction.APPEND:
            cursor, done = _handle_append_path(cursor, path, next_path, type_check, index)
        else:
            assert_cant_happen()
            done = False

        if done:
            break

    return context