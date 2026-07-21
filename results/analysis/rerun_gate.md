# Przeliczenie bramki testowej w naprawionym srodowisku (Etap 9)

Rekordow w test_gate_rerun: 525; migawek z linia bazowa: 105.

## 1. Linia bazowa po naprawie srodowiska (BASE, kod niezmodyfikowany)

* migawki z czysta linia bazowa: 50/105 (47.6%)
  * flask: 17/35
  * httpie: 5/35
  * requests: 28/35
* migawki z niezaliczonymi testami bazowo (id testow):
  * httpie_001: tests/test_uploads.py::TestRequestBodyFromFilePath::test_request_body_from_file_by_path_no_field_name_allowed;tests/test_uploads.py::TestRequestBodyFromFilePath
  * flask_002: tests/test_cli.py::test_get_version
  * httpie_002: tests/test_uploads.py::TestRequestBodyFromFilePath::test_request_body_from_file_by_path_no_field_name_allowed;tests/test_uploads.py::TestRequestBodyFromFilePath
  * flask_004: tests/test_cli.py::test_get_version
  * flask_005: tests/test_cli.py::test_get_version
  * flask_006: tests/test_cli.py::test_get_version
  * flask_007: tests/test_cli.py::test_get_version
  * flask_008: tests/test_cli.py::test_get_version
  * httpie_003: tests/test_errors.py::test_error;tests/test_errors.py::test_error_traceback;tests/test_errors.py::test_error_custom_dns[11002-check;tests/test_errors.py::test_e
  * flask_011: tests/test_cli.py::test_get_version
  * flask_012: tests/test_cli.py::test_get_version
  * flask_013: tests/test_cli.py::test_get_version
  * requests_001: tests/test_lowlevel.py::test_use_proxy_from_environment[http_proxy-http];tests/test_lowlevel.py::test_use_proxy_from_environment[https_proxy-https];tests/test_l
  * flask_016: tests/test_cli.py::test_get_version
  * httpie_004: tests/test_errors.py::test_error;tests/test_errors.py::test_error_traceback;tests/test_errors.py::test_error_custom_dns[11002-check;tests/test_errors.py::test_e
  * flask_022: tests/test_cli.py::test_get_version
  * flask_023: tests/test_cli.py::test_get_version
  * flask_024: tests/test_cli.py::test_get_version
  * flask_025: tests/test_cli.py::test_get_version
  * flask_026: tests/test_cli.py::test_get_version
  * httpie_005: tests/test_downloads.py::TestDownloads::test_actual_download[http];tests/test_downloads.py::TestDownloads::test_actual_download[https]
  * flask_029: tests/test_cli.py::test_get_version
  * flask_033: tests/test_cli.py::test_get_version
  * flask_034: tests/test_cli.py::test_get_version
  * httpie_006: tests/test_sessions.py::TestSession::test_session_with_cookie_followed_by_another_header;tests/test_sessions.py::TestExpiredCookies::test_expired_cookies;tests/
  * httpie_007: tests/test_auth.py::test_missing_auth;tests/test_auth.py::test_ignore_netrc_with_auth_type_resulting_in_missing_auth;tests/test_cli.py::test_url_colon_slash_sla
  * httpie_008: tests/test_auth.py::test_missing_auth;tests/test_auth.py::test_ignore_netrc_with_auth_type_resulting_in_missing_auth;tests/test_cli.py::test_url_colon_slash_sla
  * httpie_009: tests/test_auth.py::test_missing_auth;tests/test_auth.py::test_ignore_netrc_with_auth_type_resulting_in_missing_auth;tests/test_cli.py::test_url_colon_slash_sla
  * httpie_010: tests/test_auth.py::test_missing_auth;tests/test_auth.py::test_ignore_netrc_with_auth_type_resulting_in_missing_auth;tests/test_cli.py::test_url_colon_slash_sla
  * httpie_011: tests/test_auth.py::test_missing_auth;tests/test_auth.py::test_ignore_netrc_with_auth_type_resulting_in_missing_auth;tests/test_cli.py::test_url_colon_slash_sla
  * httpie_012: tests/test_auth.py::test_missing_auth;tests/test_auth.py::test_ignore_netrc_with_auth_type_resulting_in_missing_auth;tests/test_cli.py::test_url_colon_slash_sla
  * httpie_014: tests/test_encoding.py::test_terminal_output_response_charset_detection[big5-\u5377\u9996\u5377\u9996\u5377\u9996\u5377\u9996\u5377\u5377\u9996\u5377\u9996\u537
  * httpie_016: tests/test_output.py::TestQuietFlag::test_quiet_with_check_status_non_zero;tests/test_output.py::TestQuietFlag::test_quiet_with_check_status_non_zero_pipe;tests
  * requests_004: tests/test_lowlevel.py::test_use_proxy_from_environment[http_proxy-http];tests/test_lowlevel.py::test_use_proxy_from_environment[https_proxy-https];tests/test_l
  * httpie_017: tests/test_compress.py::test_compress_form[http];tests/test_downloads.py::TestDownloads::test_actual_download[http];tests/test_errors.py::test_max_headers_limit
  * httpie_018: tests/test_compress.py::test_compress_form[http];tests/test_downloads.py::TestDownloads::test_actual_download[http];tests/test_errors.py::test_max_headers_limit
  * requests_010: tests/test_lowlevel.py::test_use_proxy_from_environment[http_proxy-http];tests/test_lowlevel.py::test_use_proxy_from_environment[https_proxy-https];tests/test_l
  * httpie_019: tests/test_update_warnings.py::test_check_updates_first_time_after_data_fetch[True-higher_build_channel]
  * httpie_020: tests/test_binary.py::TestBinaryResponseData::test_binary_suppresses_when_terminal;tests/test_binary.py::TestBinaryResponseData::test_binary_suppresses_when_not
  * httpie_021: tests/test_uploads.py::TestRequestBodyFromFilePath::test_request_body_from_file_by_path_no_field_name_allowed;tests/test_uploads.py::TestRequestBodyFromFilePath
  * httpie_022: tests/test_compress.py::test_compress_form[http];tests/test_downloads.py::TestDownloads::test_actual_download[http];tests/test_errors.py::test_max_headers_limit
  * requests_016: tests/test_lowlevel.py::test_use_proxy_from_environment[http_proxy-http];tests/test_lowlevel.py::test_use_proxy_from_environment[https_proxy-https];tests/test_l
  * requests_019: tests/test_lowlevel.py::test_use_proxy_from_environment[http_proxy-http];tests/test_lowlevel.py::test_use_proxy_from_environment[https_proxy-https];tests/test_l
  * requests_022: tests/test_lowlevel.py::test_use_proxy_from_environment[http_proxy-http];tests/test_lowlevel.py::test_use_proxy_from_environment[https_proxy-https];tests/test_l
  * httpie_023: tests/test_downloads.py::TestDownloads::test_actual_download[http];tests/test_downloads.py::TestDownloads::test_actual_download[https];tests/test_sessions.py::T
  * httpie_024: tests/test_compress.py::test_compress_form[http];tests/test_downloads.py::TestDownloads::test_actual_download[http];tests/test_errors.py::test_max_headers_limit
  * requests_028: tests/test_lowlevel.py::test_use_proxy_from_environment[http_proxy-http];tests/test_lowlevel.py::test_use_proxy_from_environment[https_proxy-https];tests/test_l
  * httpie_025: tests/test_auth.py::test_missing_auth;tests/test_auth.py::test_ignore_netrc_with_auth_type_resulting_in_missing_auth;tests/test_cli.py::test_url_colon_slash_sla
  * httpie_028: tests/test_compress.py::test_compress_form[http];tests/test_downloads.py::TestDownloads::test_actual_download[http];tests/test_errors.py::test_max_headers_limit
  * httpie_029: tests/test_sessions.py::TestSession::test_session_with_cookie_followed_by_another_header;tests/test_sessions.py::TestExpiredCookies::test_expired_cookies;tests/
  * httpie_030: tests/test_downloads.py::TestDownloads::test_actual_download[http];tests/test_downloads.py::TestDownloads::test_actual_download[https]
  * httpie_031: tests/test_auth.py::test_missing_auth;tests/test_auth.py::test_ignore_netrc_with_auth_type_resulting_in_missing_auth;tests/test_cli.py::test_url_colon_slash_sla
  * httpie_032: tests/test_output.py::TestQuietFlag::test_quiet_with_check_status_non_zero;tests/test_output.py::TestQuietFlag::test_quiet_with_check_status_non_zero_pipe;tests
  * httpie_033: tests/test_config.py::test_config_file_not_valid;tests/test_encoding.py::test_terminal_output_response_charset_detection[big5-\u5377\u9996\u5377\u9996\u5377\u99
  * httpie_035: tests/test_output.py::TestQuietFlag::test_quiet_with_check_status_non_zero;tests/test_output.py::TestQuietFlag::test_quiet_with_check_status_non_zero_pipe;tests

### Efektywna liczba testow (zielone bazowo = faktyczna bramka)

* flask: mediana 150 testow zielonych bazowo na migawke (min 1, max 489)
* httpie: mediana 70 testow zielonych bazowo na migawke (min 11, max 919)
* requests: mediana 348 testow zielonych bazowo na migawke (min 325, max 592)

## 2. Bramka testowa per warunek (artefakty z 4C, bez -x)

| Warunek | n par z BASE | testy czyste (strict) | regresje tozsamosciowe (nowe niezaliczone vs BASE) | CI Wilsona regresji |
|---|---|---|---|---|
| T | 105 | 56 | 0 | [0.0; 3.5] |
| A | 105 | 46 | 16 | [9.6; 23.3] |
| G | 105 | 62 | 11 | [6.0; 17.8] |
| C | 105 | 48 | 18 | [11.1; 25.5] |

### Regresje tozsamosciowe (szczegoly)

* A x flask_001: tests/test_basic.py::test_response_types
* A x flask_004: tests/test_cli.py::TestRoutes::test_host; tests/test_cli.py::TestRoutes::test_subdomain
* A x flask_017: tests/test_config.py::test_from_prefixed_env_nested
* A x flask_025: tes; tests/test_appctx.py::test_app_context_provides_current_app; tests/test_appctx.py::test_app_tearing_down; tests/test_appctx.py::test_app_tearing_down_with_handled_exception_by_app_handler; tests/test_appctx.py::test
* A x httpie_004: tests/te; tests/test_output.py::TestQuietFlag::test_quiet_with_explicit_output_options[-v-quiet_flags0]; tests/test_output.py::TestQuietFlag::test_quiet_with_explicit_output_options[-v-quiet_flags1]; tests/test_output.py
* A x flask_033: tests/test_basic.py::test_extended_flashing; tests/test_basic.py::test_flashes; tests/test_basic.py::test_session_accessed; tests/test_basic.py::test_session_cookie_setting; tests/test_basic.py::test_session_expiration; 
* A x flask_035: tests/test_basic.py::test_static_files; tests/test_basic.py::test_static_folder_with_pathlib_path; tests/test_basic.py::test_static_route_with_host_matching; tests/test_basic.py::test_static_url_empty_path; tests/test_ba
* A x httpie_013: tests/test_httpie_cli.py::test_cli_export[loads-extra_options0]; tests/test_httpie_cli.py::test_cli_export[loads-extra_options1]; tests/test_parser_schema.py::test_parser_serialization
* A x httpie_016: tests/test_output.py::TestColors::test_get_lexer[text/plain-True-foo-Text
* A x requests_005: tests/test_requests.py::TestRequests::test_POSTBIN_GET_POST_FILES; tests/test_requests.py::TestRequests::test_POSTBIN_GET_POST_FILES_WITH_DATA; tests/test_requests.py::TestRequests::test_can_send_file_object_with_non_str
* A x requests_007: tests/test_requests.py::TestRequests::test_json_param_post_content_type_works
* A x requests_006: tests/test_requests.py::TestRequests::test_invalid_url[MissingSchema-hiwpefhipowhefopw]; tests/test_requests.py::TestRequests::test_params_bytes_are_encoded
* A x requests_008: tests/test_requests.py::Tes; tests/test_requests.py::TestRequests::test_HTTP_200_OK_GET_ALTERNATIVE; tests/test_requests.py::TestRequests::test_HTTP_302_ALLOW_REDIRECT_GET; tests/test_requests.py::TestRequests::test_HTTP
* A x requests_009: tests/test_requests.py:; tests/test_requests.py::TestRequests::test_HTTP_302_ALLOW_REDIRECT_GET; tests/test_requests.py::TestRequests::test_HTTP_302_TOO_MANY_REDIRECTS; tests/test_requests.py::TestRequests::test_HTTP_302
* A x requests_010: tests/test_requests.py::TestRequests::test_HTTP_200_OK_GET_ALTERNATIVE; tests/test_requests.py::TestRequests::test_cookielib_cookiejar_on_redirect; tests/test_requests.py::TestRequests::test_header_and_body_removal_on_re
* A x requests_012: tests/test_requests.py::TestRequests::test_HTTP_307_ALLOW_REDIRECT_POST_WITH_SEEKABLE; tests/test_requests.py::TestRequests::test_empty_stream_with_auth_does_not_set_content_length_header; tests/test_requests.py::TestReq
* G x flask_004: tests/test_cli.py::TestRoutes::test_all_methods; tests/test_cli.py::TestRoutes::test_host; tests/test_cli.py::TestRoutes::test_simple; tests/test_cli.py::TestRoutes::test_subdomain
* G x flask_012: tests/test_cli.py::test_cli_blueprints; tests/test_cli.py::test_cli_empty
* G x httpie_014: tests/test_encoding.py::test_unicode_json_item; tests/test_encoding.py::test_unicode_json_item_verbose; tests/test_encoding.py::test_unicode_raw_json_item; tests/test_encoding.py::test_unicode_raw_json_item_verbose; test
* G x requests_004: tests/test_lowlevel.py::test_digestauth_401_count_reset_on_redirect; tests/test_lowlevel.py::test_digestauth_401_only_sent_once; tests/test_requests.py::TestRequests::test_DIGESTAUTH_QUOTES_QOP_VALUE; tests/test_requests
* G x requests_005: tests/test_requests.py::TestRequests::test_POSTBIN_GET_POST_FILES; tests/test_requests.py::TestRequests::test_POSTBIN_GET_POST_FILES_WITH_DATA; tests/test_requests.py::TestRequests::test_can_send_file_object_with_non_str
* G x requests_008: tests/test_requests.py::Tes; tests/test_requests.py::TestRequests::test_HTTP_200_OK_GET_ALTERNATIVE; tests/test_requests.py::TestRequests::test_HTTP_302_ALLOW_REDIRECT_GET; tests/test_requests.py::TestRequests::test_HTTP
* G x requests_020: tests/test_requests.py::TestRequests::test_basic_building; tests/test_requests.py::TestRequests::test_binary_put; tests/test_requests.py::TestRequests::test_empty_content_length[OPTIONS]; tests/test_requests.py::TestRequ
* G x requests_021: tests/test_requests.; tests/test_requests.py::TestRequests::test_basic_building; tests/test_requests.py::TestRequests::test_empty_content_length[OPTIONS]; tests/test_requests.py::TestRequests::test_empty_content_length[P
* G x requests_022: tests/test_lowlevel.py::test_json_decode_compatibility_for_alt_utf_encodings; tests/test_requests.py::TestPreparingURLs::test_json_decode_compatibility; tests/test_requests.py::TestPreparingURLs::test_json_decode_persist
* G x requests_030: tests/test_requests.py::TestTimeout::test_read_timeout[timeout0]; tests/test_requests.py::TestTimeout::test_read_timeout[timeout1]; tests/test_requests.py::TestTimeout::test_stream_timeout
* G x requests_035: tests/test_requests.py::TestRequests::test_HTTP_307_ALLOW_REDIRECT_POST
* C x flask_001: tests/test_basic.py::test_before_request_and_routing_errors; tests/test_basic.py::test_error_handler_after_processor_error; tests/test_basic.py::test_error_handling; tests/test_basic.py::test_error_handling_processing; t
* C x flask_002: tests/test_basic.py::test_run_defaults; tests/test_basic.py::test_run_from_config[None-None-pocoo.org:8080-pocoo.or; tests/test_basic.py::test_run_server_port; tests/test_basic.py::test_werkzeug_passthrough_errors[False-
* C x flask_003: tests/test_appctx.py::test_basic_url_generation; tests/test_appctx.py::test_url_generation_requires_server_name; tests/test_basic.py::test_build_error_handler; tests/test_basic.py::test_build_error_handler_reraise; tests
* C x flask_011: tests/test_async.py::test_async_before_after_request; tests/test_basic.py::test_app_freed_on_zero_refcount; tests/test_basic.py::test_provide_automatic_options_attr; tests/test_basic.py::test_response_type_errors; tests/
* C x flask_012: tests/test_cli.py::test_cli_blueprints; tests/test_cli.py::test_cli_empty
* C x flask_017: tests/test_config.py::test_from_prefixed_env; tests/test_config.py::test_from_prefixed_env_custom_prefix; tests/test_config.py::test_from_prefixed_env_nested
* C x flask_026: tests/test_basic.py::test_enctype_debug_helper; tests/test_basic.py::test_no_setup_after_first_request; tests/test_basic.py::test_route_decorator_custom_endpo; tests/test_basic.py::test_werkzeug_passthrough_errors[False-
* C x httpie_007: tests/test_auth.py::test_auth_plugin_netrc_parse[basic-/basic-auth/httpie/password]; tests/test_auth.py::test_auth_plugin_netrc_parse[digest-/digest-auth/auth/httpie/password]; tests/test_auth.py::test_credentials_in_url
* C x requests_001: tests/test_lowlevel.py::test_chunked_encoding_error; tests/test_lowlevel.py::test_chunked_upload; tests/test_lowlevel.py::test_chunked_upload_doesnt_skip_host_header; tests/test_lowlevel.py::test_chunked_upload_uses_only
* C x httpie_013: tests/test_httpie_cli.py::test_cli_export[loads-extra_options0]; tests/test_httpie_cli.py::test_cli_export[loads-extra_options1]; tests/test_parser_schema.py::test_parser_serialization
* C x requests_004: tests/test_lowlevel.py::test_digestauth_401_count_reset_on_redirect; tests/test_lowlevel.py::test_digestauth_401_only_sent_once; tests/test_requests.py::TestRequests::test_DIGESTAUTH_QUOTES_QOP_VALUE; tests/test_requests
* C x requests_005: tests/test_requests.py::TestRequests::test_POSTBIN_GET_POST_FILES; tests/test_requests.py::TestRequests::test_POSTBIN_GET_POST_FILES_WITH_DATA; tests/test_requests.py::TestRequests::test_can_send_file_object_with_non_str
* C x requests_006: tests/test_requests.; tests/test_requests.py::TestRequests::test_basic_building; tests/test_requests.py::TestRequests::test_empty_content_length[OPTIONS]; tests/test_requests.py::TestRequests::test_empty_content_length[P
* C x requests_008: tests/test_requests.py::Tes; tests/test_requests.py::TestRequests::test_HTTP_200_OK_GET_ALTERNATIVE; tests/test_requests.py::TestRequests::test_HTTP_302_ALLOW_REDIRECT_GET; tests/test_requests.py::TestRequests::test_HTTP
* C x requests_011: tests/test_requests.py::TestRequests::test_auth_is_retained_for_redirect_on_host; tests/test_requests.py::TestRequests::test_auth_is_stripped_on_http_downgrade; tests/test_requests.py::TestRequests::test_should_strip_aut
* C x httpie_020: tests/test_stream.py::test_auto_streaming[extras0-3]; tests/test_stream.py::test_auto_streaming[extras1-3]; tests/test_stream.py::test_auto_streaming[extras2-1]; tests/test_stream.py::test_encoded_stream; tests/test_stre
* C x requests_022: tests/test_lowlevel.py::test_json_decode_compatibility_for_alt_utf_encodings
* C x requests_034: tests/test_requests.py::TestRequests::test_POSTBIN_GET_POST_FILES; tests/test_requests.py::TestRequests::test_POSTBIN_GET_POST_FILES_WITH_DATA; tests/test_requests.py::TestRequests::test_request_ok_set; tests/test_reques

## 3. Nowa kaskada: akceptacja koncowa (bramki strukturalne z 4C + bramka testowa po naprawie)

| Warunek | strict (testy czyste) | wzgledem linii bazowej (brak nowych niezaliczonych) |
|---|---|---|
| T | 48/105 = 45.7% [36.5; 55.2] | 97/105 = 92.4% [85.7; 96.1] |
| A | 44/105 = 41.9% [32.9; 51.5] | 87/105 = 82.9% [74.5; 88.9] |
| G | 30/105 = 28.6% [20.8; 37.8] | 62/105 = 59.0% [49.5; 68.0] |
| C | 45/105 = 42.9% [33.8; 52.4] | 84/105 = 80.0% [71.4; 86.5] |

## 4. Werdykty weryfikacji celowanej (izolowane przebiegi oflagowanych testow)

| Warunek | oflagowane | potwierdzone | niereprodukowalne | niestabilne srodowiskowo | potwierdzone /105 | CI Wilsona |
|---|---|---|---|---|---|---|
| T | 0 | 0 | 0 | 0 | 0.0% | [0.0; 3.5] |
| A | 16 | 13 | 3 | 0 | 12.4% | [7.4; 20.0] |
| G | 11 | 7 | 4 | 0 | 6.7% | [3.3; 13.1] |
| C | 18 | 12 | 6 | 0 | 11.4% | [6.7; 18.9] |

## 5. OSTATECZNA akceptacja: bramki strukturalne + brak potwierdzonej regresji wzgledem linii bazowej

| Warunek | akceptacja | CI Wilsona |
|---|---|---|
| T | 97/105 = 92.4% | [85.7; 96.1] |
| A | 90/105 = 85.7% | [77.8; 91.1] |
| G | 66/105 = 62.9% | [53.3; 71.5] |
| C | 90/105 = 85.7% | [77.8; 91.1] |

### Potwierdzone regresje per para (do tabeli/aneksu)

* A x flask_001: 1 test(y); np. tests/test_basic.py::test_response_types
* A x flask_004: 2 test(y); np. tests/test_cli.py::TestRoutes::test_host
* A x flask_017: 1 test(y); np. tests/test_config.py::test_from_prefixed_env_nested
* A x flask_025: 39 test(y); np. tests/test_appctx.py::test_app_context_provides_current_app
* A x flask_033: 19 test(y); np. tests/test_basic.py::test_extended_flashing
* A x flask_035: 13 test(y); np. tests/test_basic.py::test_static_files
* A x httpie_004: 9 test(y); np. tests/test_output.py::TestQuietFlag::test_quiet_with_explicit_output_options[-v-quiet_flags0]
* A x httpie_013: 3 test(y); np. tests/test_httpie_cli.py::test_cli_export[loads-extra_options0]
* A x requests_005: 17 test(y); np. tests/test_requests.py::TestRequests::test_POSTBIN_GET_POST_FILES
* A x requests_006: 2 test(y); np. tests/test_requests.py::TestRequests::test_invalid_url[MissingSchema-hiwpefhipowhefopw]
* A x requests_007: 1 test(y); np. tests/test_requests.py::TestRequests::test_json_param_post_content_type_works
* A x requests_009: 27 test(y); np. tests/test_requests.py::TestRequests::test_HTTP_302_ALLOW_REDIRECT_GET
* A x requests_012: 11 test(y); np. tests/test_requests.py::TestRequests::test_HTTP_307_ALLOW_REDIRECT_POST_WITH_SEEKABLE
* C x flask_003: 27 test(y); np. tests/test_appctx.py::test_basic_url_generation
* C x flask_012: 2 test(y); np. tests/test_cli.py::test_cli_blueprints
* C x flask_017: 3 test(y); np. tests/test_config.py::test_from_prefixed_env
* C x httpie_007: 6 test(y); np. tests/test_auth.py::test_auth_plugin_netrc_parse[basic-/basic-auth/httpie/password]
* C x httpie_013: 3 test(y); np. tests/test_httpie_cli.py::test_cli_export[loads-extra_options0]
* C x httpie_020: 14 test(y); np. tests/test_stream.py::test_auto_streaming[extras0-3]
* C x requests_004: 8 test(y); np. tests/test_lowlevel.py::test_digestauth_401_count_reset_on_redirect
* C x requests_005: 17 test(y); np. tests/test_requests.py::TestRequests::test_POSTBIN_GET_POST_FILES
* C x requests_006: 24 test(y); np. tests/test_requests.py::TestRequests::test_basic_building
* C x requests_011: 9 test(y); np. tests/test_requests.py::TestRequests::test_auth_is_retained_for_redirect_on_host
* C x requests_022: 1 test(y); np. tests/test_lowlevel.py::test_json_decode_compatibility_for_alt_utf_encodings
* C x requests_034: 7 test(y); np. tests/test_requests.py::TestRequests::test_POSTBIN_GET_POST_FILES
* G x flask_004: 4 test(y); np. tests/test_cli.py::TestRoutes::test_all_methods
* G x flask_012: 2 test(y); np. tests/test_cli.py::test_cli_blueprints
* G x requests_004: 8 test(y); np. tests/test_lowlevel.py::test_digestauth_401_count_reset_on_redirect
* G x requests_005: 18 test(y); np. tests/test_requests.py::TestRequests::test_POSTBIN_GET_POST_FILES
* G x requests_021: 24 test(y); np. tests/test_requests.py::TestRequests::test_basic_building
* G x requests_022: 16 test(y); np. tests/test_lowlevel.py::test_json_decode_compatibility_for_alt_utf_encodings
* G x requests_030: 3 test(y); np. tests/test_requests.py::TestTimeout::test_read_timeout[timeout0]
