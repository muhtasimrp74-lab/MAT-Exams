#!/usr/bin/env python3
"""MD প্রশ্নব্যাংক -> data/<id>.js অধ্যায় এবং data/manifest.js আপডেট।
ব্যবহার: python3 tools/md_to_chapter.py file.md --id bio2-11 --subject জীববিজ্ঞান --paper "২য় পত্র · অধ্যায় ১১" --title "জিনতত্ত্ব"
MD ফরম্যাট: '## সেকশন N: টপিক' / '**প্রশ্ন N.** ...' / '(ক) ..' '(খ) ..' '(গ) ..' '(ঘ) ..' / '✅ **উত্তর: (খ)** — ব্যাখ্যা'"""
import re, json, argparse, os
L = 'কখগঘ'
def parse(md):
    qs, topic, cur = [], 'সাধারণ', None
    def flush():
        nonlocal cur
        if cur and len(cur['o']) == 4 and cur.get('a') is not None: qs.append(cur)
        cur = None
    for line in md.split('\n'):
        line = line.rstrip()
        m = re.match(r'##\s*(?:সেকশন[^:]*:\s*)?(.+)', line)
        if m and not line.startswith('###'):
            flush(); t = m.group(1).strip()
            topic = re.sub(r'\s*\(.*?\)\s*$', '', t) if not t.startswith('⭐') and 'উত্তরমালা' not in t else None
            if topic and ('/' in topic and 'মিশ্র' in topic): topic = 'মিশ্র ও ক্যালকুলেশন'
            continue
        m = re.match(r'\*\*প্রশ্ন\s*\d+\.\*\*\s*(.+)', line)
        if m and topic:
            flush(); text = m.group(1); p = None; l = 0
            mm = re.search(r'📌\s*(?:\[([^\]]+)\])?', text)
            if mm: p = (mm.group(1) or 'পূর্বে এসেছে').strip(); text = text.replace(mm.group(0), '')
            if '🔮' in text: l = 1; text = text.replace('🔮', '')
            cur = {'t': topic, 'q': re.sub(r'\s+', ' ', text).strip(), 'o': [], 'e': '', 'r': []}
            if p: cur['p'] = p
            if l: cur['l'] = 1
            continue
        if cur is not None:
            m = re.match(r'\(([কখগঘ])\)\s*(.+)', line)
            if m and len(cur['o']) < 4: cur['o'].append(m.group(2).strip()); continue
            m = re.match(r'✅\s*\*\*উত্তর:\s*\(([কখগঘ])\)\*\*\s*[—-]?\s*(.*)', line)
            if m: cur['a'] = L.index(m.group(1)); cur['e'] = m.group(2).strip()
    flush(); return qs
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('md'); ap.add_argument('--id', required=True); ap.add_argument('--subject', required=True)
    ap.add_argument('--paper', required=True); ap.add_argument('--title', required=True)
    a = ap.parse_args(); root = os.path.join(os.path.dirname(__file__), '..', 'data')
    qs = parse(open(a.md, encoding='utf8').read())
    ch = {'id': a.id, 'subject': a.subject, 'paper': a.paper, 'title': a.title, 'questions': qs}
    open(os.path.join(root, a.id + '.js'), 'w', encoding='utf8').write('REG(' + json.dumps(ch, ensure_ascii=False) + ');\n')
    mp = os.path.join(root, 'manifest.js'); man = []
    if os.path.exists(mp):
        man = json.loads(open(mp, encoding='utf8').read().split('=', 1)[1].rstrip().rstrip(';'))
    man = [x for x in man if x['id'] != a.id] + [{'id': a.id, 'file': 'data/' + a.id + '.js', 'count': len(qs), 'v': 1}]
    open(mp, 'w', encoding='utf8').write('window.MANIFEST = ' + json.dumps(man, ensure_ascii=False, indent=1) + ';\n')
    print(a.id, len(qs), 'প্রশ্ন যোগ হয়েছে')
