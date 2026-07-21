# === ARP Faza 4C - refactored code ===
# sample_id: flask_008
# condition: A
# timestamp: 2026-06-04T14:12:18
# original_cc: 10, original_mi: None
# changed_pct: 0.6522
# === END HEADER ===
def _validate_key(ctx: click.Context, param: click.Parameter, value: t.Any) -> t.Any:
    """The ``--key`` option must be specified when ``--cert`` is a file.
    Modifies the ``cert`` param to be a ``(cert, key)`` pair if needed.
    """
    cert = ctx.params.get("cert")
    is_adhoc = cert == "adhoc"
    is_context = _is_ssl_context(cert)

    if value is not None:
        _validate_key_with_value(ctx, param, value, cert, is_adhoc, is_context)
    else:
        _validate_key_without_value(ctx, param, cert, is_adhoc, is_context)

    return value


def _is_ssl_context(cert: t.Any) -> bool:
    try:
        import ssl
        return isinstance(cert, ssl.SSLContext)
    except ImportError:
        return False


def _validate_key_with_value(ctx, param, value, cert, is_adhoc, is_context):
    if is_adhoc:
        raise click.BadParameter(
            'When "--cert" is "adhoc", "--key" is not used.', ctx, param
        )

    if is_context:
        raise click.BadParameter(
            'When "--cert" is an SSLContext object, "--key" is not used.',
            ctx,
            param,
        )

    if not cert:
        raise click.BadParameter('"--cert" must also be specified.', ctx, param)

    ctx.params["cert"] = cert, value


def _validate_key_without_value(ctx, param, cert, is_adhoc, is_context):
    if cert and not (is_adhoc or is_context):
        raise click.BadParameter('Required when using "--cert".', ctx, param)