from __future__ import annotations
SYSTEM_PROMPT = 'You are an expert Python code refactoring assistant.\n\nYour task is to improve the quality of the given Python function by applying\nsafe, behaviour-preserving refactoring transformations.\n\nContext about the code:\n- File: {file_path}\n- Current Cyclomatic Complexity (CC): {cc}\n- Current Maintainability Index (MI): {mi}\n- Detected smell type: {smell_type}\n\nRules you MUST follow:\n1. Return ONLY the refactored Python code — no explanations, no markdown fences,\n   no commentary before or after the code.\n2. Preserve the original function signature (name, parameters, return type).\n3. Preserve the original behaviour — the refactored code must be semantically\n   equivalent to the original.\n4. Focus on reducing cyclomatic complexity and improving maintainability.\n5. Apply standard refactoring patterns: extract helper functions, simplify\n   conditionals, remove dead code, improve naming, use early returns.\n6. If the refactoring cannot be safely applied without risk of changing\n   behaviour, return the original code unchanged.\n7. Do NOT add type hints that were not present in the original.\n8. Do NOT add or remove imports.\n'
USER_PROMPT = 'Refactor the following Python function:\n\n```python\n{code_block}\n```\n'
FEW_SHOT_EXAMPLES: dict[str,
                        list[dict[str,
                                  str]]] = {'long_method': [{'role': 'user',
                                                             'content': "Refactor the following Python function:\n\n```python\ndef process_data(items):\n    results = []\n    for item in items:\n        if item.get('type') == 'A':\n            val = item['value'] * 2\n            if val > 100:\n                val = 100\n            results.append(val)\n        elif item.get('type') == 'B':\n            val = item['value'] + 10\n            if val < 0:\n                val = 0\n            results.append(val)\n    return results\n```"},
                                                            {'role': 'assistant',
                                                             'content': "def process_data(items):\n    results = []\n    for item in items:\n        val = _compute_value(item)\n        if val is not None:\n            results.append(val)\n    return results\n\n\ndef _compute_value(item):\n    item_type = item.get('type')\n    if item_type == 'A':\n        return min(item['value'] * 2, 100)\n    if item_type == 'B':\n        return max(item['value'] + 10, 0)\n    return None\n"}],
                                            'complex_conditional': [{'role': 'user',
                                                                     'content': "Refactor the following Python function:\n\n```python\ndef get_status(user):\n    if user.is_active:\n        if user.is_admin:\n            if user.has_2fa:\n                return 'secure_admin'\n            else:\n                return 'admin'\n        else:\n            return 'active'\n    else:\n        return 'inactive'\n```"},
                                                                    {'role': 'assistant',
                                                                     'content': "def get_status(user):\n    if not user.is_active:\n        return 'inactive'\n    if not user.is_admin:\n        return 'active'\n    if user.has_2fa:\n        return 'secure_admin'\n    return 'admin'\n"}],
                                            'duplicate_code': [{'role': 'user',
                                                                'content': "Refactor the following Python function:\n\n```python\ndef send_report(report, channel):\n    if channel == 'email':\n        data = serialize(report)\n        log('Sending via email')\n        email_client.send(data)\n        log('Sent via email')\n    elif channel == 'slack':\n        data = serialize(report)\n        log('Sending via slack')\n        slack_client.send(data)\n        log('Sent via slack')\n```"},
                                                               {'role': 'assistant',
                                                                'content': "CHANNEL_CLIENTS = {'email': email_client, 'slack': slack_client}\n\n\ndef send_report(report, channel):\n    client = CHANNEL_CLIENTS.get(channel)\n    if client is None:\n        return\n    data = serialize(report)\n    log(f'Sending via {channel}')\n    client.send(data)\n    log(f'Sent via {channel}')\n"}]}


def _classify_smell(cc: int | float) -> str:
    if cc >= 10:
        return 'long_method'
    if cc >= 7:
        return 'complex_conditional'
    return 'duplicate_code'


SYSTEM_PROMPT_WITH_CONTEXT = 'You are an expert Python code refactoring assistant.\n\nYou will be shown the FULL source file as context, then asked to refactor\nexactly ONE function from that file. The context helps you understand:\n- which helpers, classes, constants and conventions already exist in the file,\n- naming style, indentation, type-hint usage and import structure,\n- which symbols the function depends on or is referenced by.\n\nContext about the target function:\n- File: {file_path}\n- Function: {function_name}\n- Current Cyclomatic Complexity (CC): {cc}\n- Current Maintainability Index (MI): {mi}\n- Detected smell type: {smell_type}\n\nRules you MUST follow:\n1. Return ONLY the refactored Python code for the TARGET FUNCTION (and any new\n   private helpers you introduce). Do NOT return the whole file. Do NOT include\n   markdown fences, no explanations, no commentary.\n2. Preserve the original function signature (name, parameters, return type).\n3. Preserve the original behaviour - the refactored code must be semantically\n   equivalent to the original.\n4. Focus on reducing cyclomatic complexity and improving maintainability.\n5. Apply standard refactoring patterns: extract helper functions, simplify\n   conditionals, remove dead code, improve naming, use early returns.\n6. If the refactoring cannot be safely applied without risk of changing\n   behaviour, return the original function unchanged.\n7. Do NOT add type hints that were not present in the original.\n8. Do NOT add or remove top-level imports - you may rely on what is already\n   imported in the file.\n9. If you introduce module-level helper functions, place them BEFORE the target\n   function in the output; they will be inserted into the file at the same\n   point as the target function.\n'
USER_PROMPT_WITH_CONTEXT = '[FULL FILE CONTEXT]\nFile path: {file_path}\n```python\n{full_file}\n```\n\n[TARGET FUNCTION TO REFACTOR]\nFunction: {function_name} (lines {start_line}-{end_line} of the file above)\n```python\n{code_block}\n```\n\nReturn ONLY the refactored TARGET FUNCTION code (plus any new helpers).\n'
MAX_CONTEXT_CHARS = 50000


def _truncate_context(full_file: str, start_line: int, end_line: int, *,
                      max_chars: int = MAX_CONTEXT_CHARS) -> tuple[str, bool]:
    if len(full_file) <= max_chars:
        return (full_file, False)
    lines = full_file.splitlines(keepends=True)
    radius = 1000
    lo = max(0, start_line - 1 - radius)
    hi = min(len(lines), end_line + radius)
    head = '# [context truncated: file is larger than the prompt budget]\n'
    head += f'# [showing lines {lo + 1}..{hi} of {len(lines)}]\n'
    window = ''.join(lines[lo:hi])
    truncated = head + window
    if len(truncated) > max_chars:
        truncated = truncated[:max_chars] + '\n# [...truncated...]\n'
    return (truncated, True)


def build_prompt_with_context(sample_meta: dict, code_block: str,
                              full_file_content: str, *, use_few_shot: bool = True) -> list[dict[str, str]]:
    smell = sample_meta.get('smell_type') or _classify_smell(sample_meta['cc'])
    system_content = SYSTEM_PROMPT_WITH_CONTEXT.format(
        file_path=sample_meta.get(
            'file_path', 'unknown'), function_name=sample_meta.get(
            'function_name', 'unknown'), cc=sample_meta['cc'], mi=sample_meta.get(
                'mi', 'N/A'), smell_type=smell)
    messages: list[dict[str, str]] = [{'role': 'system', 'content': system_content}]
    if use_few_shot and smell in FEW_SHOT_EXAMPLES:
        messages.extend(FEW_SHOT_EXAMPLES[smell])
    truncated, _ = _truncate_context(
        full_file_content, sample_meta.get(
            'start_line', 1), sample_meta.get(
            'end_line', 1))
    messages.append(
        {
            'role': 'user', 'content': USER_PROMPT_WITH_CONTEXT.format(
                file_path=sample_meta.get(
                    'file_path', 'unknown'), function_name=sample_meta.get(
                    'function_name', 'unknown'), start_line=sample_meta.get(
                        'start_line', '?'), end_line=sample_meta.get(
                            'end_line', '?'), full_file=truncated, code_block=code_block)})
    return messages


def build_prompt(sample_meta: dict, code_block: str, *,
                 use_few_shot: bool = True) -> list[dict[str, str]]:
    smell = sample_meta.get('smell_type') or _classify_smell(sample_meta['cc'])
    system_content = SYSTEM_PROMPT.format(
        file_path=sample_meta.get(
            'file_path', 'unknown'), cc=sample_meta['cc'], mi=sample_meta.get(
            'mi', 'N/A'), smell_type=smell)
    messages: list[dict[str, str]] = [{'role': 'system', 'content': system_content}]
    if use_few_shot and smell in FEW_SHOT_EXAMPLES:
        messages.extend(FEW_SHOT_EXAMPLES[smell])
    messages.append({'role': 'user', 'content': USER_PROMPT.format(code_block=code_block)})
    return messages
