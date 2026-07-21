# === ARP Faza 4C - refactored code ===
# sample_id: flask_008
# condition: G
# timestamp: 2026-06-04T14:14:54
# original_cc: 10, original_mi: None
# changed_pct: 0.3409
# === END HEADER ===
def _is_ssl_context(cert: t.Any) -> bool:
    """Check if the given object is an SSLContext, handling potential ImportError for ssl."""
    try:
        import ssl
    except ImportError:
        return False
    return isinstance(cert, ssl.SSLContext)


def _validate_key(ctx: click.Context, param: click.Parameter, value: t.Any) -> t.Any:
    """The ``--key`` option must be specified when ``--cert`` is a file.
    Modifies the ``cert`` param to be a ``(cert, key)`` pair if needed.
    """
    cert = ctx.params.get("cert")
    is_adhoc = cert == "adhoc"
    is_context = _is_ssl_context(cert)

    if value is not None:
        # A key file was provided. Validate its usage with the --cert option.
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
            # If --key is provided, --cert must also be provided.
            raise click.BadParameter('"--cert" must also be specified.', ctx, param)

        # If all checks pass, combine cert and key into a tuple.
        ctx.params["cert"] = cert, value
    else:
        # No key file was provided. Validate if it was required.
        # A key is required if --cert is a file path (not adhoc or SSLContext).
        if cert and not (is_adhoc or is_context):
            raise click.BadParameter('Required when using "--cert".', ctx, param)

    return value