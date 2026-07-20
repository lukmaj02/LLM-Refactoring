from __future__ import annotations
import ast
import difflib
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PatchValidation:
    is_valid: bool
    rejection_reason: str | None
    detail: str | None = None
    changed_lines: int = 0
    total_lines: int = 0
    changed_pct: float = 0.0


def strip_markdown_fences(text: str) -> str:
    text = text.strip()
    text = re.sub('^```(?:python|py)?\\s*\\n', '', text)
    text = re.sub('\\n```\\s*$', '', text)
    return text.strip()


def generate_patch(original: str, refactored: str, file_path: str) -> str:
    orig_lines = original.splitlines(keepends=True)
    ref_lines = refactored.splitlines(keepends=True)
    diff = difflib.unified_diff(
        orig_lines,
        ref_lines,
        fromfile=f'a/{file_path}',
        tofile=f'b/{file_path}')
    return ''.join(diff)


def validate_patch(patch: str, refactored_code: str | None = None) -> PatchValidation:
    if not patch.strip():
        return PatchValidation(is_valid=False, rejection_reason='empty_patch',
                               detail='No changes detected between original and refactored code')
    added = sum((1 for ln in patch.splitlines() if ln.startswith('+') and (not ln.startswith('+++'))))
    removed = sum((1 for ln in patch.splitlines() if ln.startswith('-')
                  and (not ln.startswith('---'))))
    context = sum((1 for ln in patch.splitlines() if ln.startswith(' ')))
    total = context + removed
    changed = added + removed
    pct = changed / total if total > 0 else 0.0
    if refactored_code is not None:
        try:
            ast.parse(refactored_code)
        except SyntaxError as exc:
            return PatchValidation(is_valid=False, rejection_reason='syntax_error', detail=str(
                exc), changed_lines=changed, total_lines=total, changed_pct=round(pct, 4))
    return PatchValidation(is_valid=True, rejection_reason=None,
                           changed_lines=changed, total_lines=total, changed_pct=round(pct, 4))


def apply_patch(refactored_code: str, target_path: str | Path) -> bool:
    try:
        Path(target_path).write_text(refactored_code, encoding='utf-8')
        return True
    except OSError:
        return False


def revert_patch(target_path: str | Path, original: str) -> None:
    Path(target_path).write_text(original, encoding='utf-8')
