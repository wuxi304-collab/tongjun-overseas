from pathlib import Path
from html.parser import HTMLParser
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
TARGET_FORMS = {
    'rfq.html': 'rfqForm',
    'supply-route.html': 'routeForm',
    'problem-order.html': 'problemOrderForm',
}


class FormSemanticsParser(HTMLParser):
    def __init__(self, target_form_id: str):
        super().__init__(convert_charrefs=True)
        self.target_form_id = target_form_id
        self.in_target_form = False
        self.form_depth = 0
        self.label_depth = 0
        self.label_for = set()
        self.controls = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs, self_closing=False)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs, self_closing=True)

    def handle_endtag(self, tag):
        if self.in_target_form:
            if tag == 'label' and self.label_depth:
                self.label_depth -= 1
            if tag == 'form':
                self.form_depth -= 1
                if self.form_depth <= 0:
                    self.in_target_form = False
                    self.form_depth = 0
        elif tag == 'form' and self.form_depth:
            self.form_depth -= 1

    def _start(self, tag, attrs, self_closing=False):
        data = dict(attrs)

        if tag == 'form':
            if self.in_target_form:
                self.form_depth += 1
            elif data.get('id') == self.target_form_id:
                self.in_target_form = True
                self.form_depth = 1
            return

        if not self.in_target_form:
            return

        element_id = data.get('id')
        if element_id:
            self.ids.append(element_id)

        if tag == 'label':
            if data.get('for'):
                self.label_for.add(data['for'])
            if not self_closing:
                self.label_depth += 1
            return

        if tag not in {'input', 'select', 'textarea'}:
            return

        input_type = (data.get('type') or '').lower()
        hidden = (
            input_type in {'hidden', 'button', 'submit', 'reset', 'image'}
            or (data.get('aria-hidden') or '').lower() == 'true'
        )
        if hidden:
            return

        self.controls.append({
            'tag': tag,
            'name': data.get('name') or '',
            'id': element_id or '',
            'aria_label': data.get('aria-label') or '',
            'aria_labelledby': data.get('aria-labelledby') or '',
            'wrapped_by_label': self.label_depth > 0,
        })


def validate_page(page: Path, form_id: str):
    if not page.is_file():
        return [f'{page.name}: file missing']

    parser = FormSemanticsParser(form_id)
    parser.feed(page.read_text(encoding='utf-8'))
    errors = []

    if not parser.controls:
        errors.append(f'{page.name}: no visible controls found in #{form_id}')
        return errors

    seen = set()
    duplicates = set()
    for element_id in parser.ids:
        if element_id in seen:
            duplicates.add(element_id)
        seen.add(element_id)
    for element_id in sorted(duplicates):
        errors.append(f'{page.name}: duplicate id {element_id!r} inside #{form_id}')

    for control in parser.controls:
        labelled = (
            control['wrapped_by_label']
            or bool(control['aria_label'])
            or bool(control['aria_labelledby'])
            or (bool(control['id']) and control['id'] in parser.label_for)
        )
        if not labelled:
            ident = control['name'] or control['id'] or control['tag']
            errors.append(
                f"{page.name}: unlabeled visible {control['tag']} {ident!r} in #{form_id}"
            )

    return errors


def main():
    errors = []
    total_controls = 0

    for filename, form_id in TARGET_FORMS.items():
        page = ROOT / filename
        parser = FormSemanticsParser(form_id)
        if page.is_file():
            parser.feed(page.read_text(encoding='utf-8'))
            total_controls += len(parser.controls)
        errors.extend(validate_page(page, form_id))

    if errors:
        for error in errors:
            print(f'ERROR: {error}')
        raise SystemExit(f'FAIL: {len(errors)} buyer-form semantic issue(s) found.')

    print(
        f'PASS: {len(TARGET_FORMS)} buyer forms / {total_controls} visible controls; '
        '0 unlabeled controls and 0 duplicate ids.'
    )


if __name__ == '__main__':
    main()
