__author__ = 'j4hangir'

import json
import re
import requests
from typing import List, Dict, Any
from csv import DictReader
from argparse import ArgumentParser
from loguru import logger


def fetch_csv(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_csv(csv_text: str) -> List[Dict[str, Any]]:
    return list(DictReader(csv_text.splitlines()))


def with_langs(data: List[Dict[str, str]]) -> Dict[str, Any]:
    keys = data[0].keys()
    langs = [key for key in keys if key not in ("key", "")]
    return {'data': data, 'langs': langs}


def build_object(content: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for element in content['data']:
        for lang in content['langs']:
            key_path = f"{lang}.{element['key']}"
            result.setdefault(lang, {})
            result[lang][element['key']] = element.get(lang, element['key'])
    return result


def to_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def to_js(obj: Any) -> str:
    return f'export default {json.dumps(obj, indent=2, ensure_ascii=False)};'


def to_ts(txt: str) -> str:
    if 'export const tr:' in txt: return txt
    data: dict[str, str] = eval(txt.replace('export default ', '', 1).strip(';'))
    assert 'en' in data, "EN not found"
    
    txt = f'import {{ref}} from "vue"\n\n{txt}'
    
    tr = [f'  get {key}() {{return tr[this._lang.value]["{key}"]}}' for key in map(lambda x: x.replace(' ', '_'), data['en'].keys())]
    tr.append('  "_id": "i18n_language"')
    tr.append('  get_lang() {return localStorage.getItem(this._id) || "en"}')
    tr.append('  _lang: ref("")')
    tr.append('  set_lang(lang: string) {this._lang.value = lang; localStorage.setItem(this._id, lang)}')
    txt = txt.replace('export default', 'const tr: Record<string, Record<string,string>> = ', 1)
    
    regex = r'("(?P<key>\w+)":\s)"(?P=key)"'
    replacement = lambda m: m.group(1) + '"%s"' % re.search('"en":\s*{.*?"%s": "(.+?)",?\n' % re.escape(m.groupdict()['key']), txt, re.DOTALL).group(1)
    txt = re.sub(regex, replacement, txt)
    
    txt += '\n\nexport const i18n_tr = {\n%s\n}' % ',\n'.join(tr)
    txt += '\ni18n_tr._lang.value = i18n_tr.get_lang()'
    return txt


def format_output(obj: Any, fmt: str) -> str:
    if fmt == 'ts': return to_ts(to_js(obj))
    else: return to_js(obj) if fmt == 'js' else to_json(obj)


def output(result: str, destination: str) -> None:
    if destination == 'stdout':
        print(result)
    else:
        logger.debug(f'Writing result to {destination}')
        with open(destination, 'w', encoding='utf-8') as file:
            file.write(result)


def main():
    parser = ArgumentParser(description='Generates vue-i18n file content from google spreadsheet.')
    parser.add_argument('spreadsheet', help='The google spreadsheet id')
    parser.add_argument('--sheet', required=False, help='The name of the spreadsheet\'s sheet')
    parser.add_argument('--format', default='json', choices=['ts', 'json', 'js'], help='The output format')
    parser.add_argument('--output', default='stdout', help='The output destination (default: stdout)')
    args = parser.parse_args()
    
    url: str = f'https://docs.google.com/spreadsheets/d/{args.spreadsheet}/gviz/tq?tqx=out:csv&sheet={args.sheet}'
    
    try:
        csv_data = fetch_csv(url)
        parsed_data = parse_csv(csv_data)
        content_with_langs = with_langs(parsed_data)
        built_object = build_object(content_with_langs)
        formatted_output = format_output(built_object, args.format)
        output(formatted_output, args.output)
    except requests.HTTPError as e:
        logger.error(f'HTTP error occurred: {e}')  # HTTP error
    except Exception as e:
        logger.error(f'An error occurred: {e}')  # Other errors


if __name__ == "__main__":
    main()
