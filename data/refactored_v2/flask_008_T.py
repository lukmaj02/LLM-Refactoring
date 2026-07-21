# === ARP Faza 4C - refactored code ===
# sample_id: flask_008
# condition: T
# timestamp: 2026-06-04T14:09:30
# original_cc: 10, original_mi: None
# changed_pct: 0.1905
# === END HEADER ===
def _validate_key(
        ctx: click.Context,
        param: click.Parameter,
        value: t.Any) -> t.Any:
    """The ``--key`` option must be specified when ``--cert`` is a file.
    Modifies the ``cert`` param to be a ``(cert, key)`` pair if needed.
    """
    cert = ctx.params.get("cert")
    is_adhoc = cert == "adhoc"

    try:
        import ssl
    except ImportError:
        is_context = False
    else:
        is_context = isinstance(cert, ssl.SSLContext)

    if value is not None:
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
            raise click.BadParameter(
                '"--cert" must also be specified.', ctx, param)

        ctx.params["cert"] = cert, value

    else:
        if cert and not (is_adhoc or is_context):
            raise click.BadParameter(
                'Required when using "--cert".', ctx, param)

    return value
