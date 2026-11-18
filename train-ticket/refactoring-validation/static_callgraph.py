#!/usr/bin/env python3
"""
Static synchronous call-graph extractor for the Train-Ticket Spring Boot services.

For a given entry endpoint (service, HTTP method, path) it resolves
  controller method -> service method -> private helpers -> RestTemplate calls -> callee endpoint
recursively and reports the synchronous call tree, its maximum depth, fan-out per service, and
asynchronous (RabbitMQ) sends. Conditional branches are not evaluated, so the tree is the static
upper bound of the calls that a request can trigger. The same extractor is applied unchanged to the
original and the refactored code base.
"""
import json, os, re, sys
from collections import defaultdict

MAP_RE = re.compile(r'@(Get|Post|Put|Delete|Patch|Request)Mapping\s*(\(([^)]*)\))?')
STR_RE = re.compile(r'"([^"]*)"')
SIG_RE = re.compile(r'(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?[\w<>\[\], ?.]+\s+(\w+)\s*\(((?:[^()]|\([^()]*\))*)\)\s*(?:throws [\w., ]+)?\s*\{')


def strip_comments(src):
    """Remove // and /* */ comments outside string and char literals."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c in '"\'':
            q = c; out.append(c); i += 1
            while i < n and src[i] != q:
                if src[i] == '\\':
                    out.append(src[i:i + 2]); i += 2; continue
                out.append(src[i]); i += 1
            if i < n:
                out.append(src[i]); i += 1
        elif src.startswith('//', i):
            while i < n and src[i] != '\n':
                i += 1
        elif src.startswith('/*', i):
            k = src.find('*/', i + 2); i = n if k < 0 else k + 2
        else:
            out.append(c); i += 1
    return ''.join(out)


def methods_of(src):
    """Return {name: [(body, annotations_text)]} using brace matching."""
    out = defaultdict(list)
    for m in SIG_RE.finditer(src):
        name, start = m.group(1), m.end()
        depth, i = 1, start
        while i < len(src) and depth:
            c = src[i]
            if c == '"':
                i += 1
                while i < len(src) and src[i] != '"':
                    i += 2 if src[i] == '\\' else 1
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            i += 1
        ann = src[max(0, m.start() - 400):m.start()]
        cut = max(ann.rfind(';'), max((mm.end() for mm in re.finditer(r'\}\s*\n', ann)), default=-1) - 1)
        ann = ann[cut + 1:] if cut >= 0 else ann
        out[name].append((src[start:i - 1], ann))
    return out


def load_service(root, svc):
    javas = []
    for d, _, fs in os.walk(os.path.join(root, svc, 'src', 'main', 'java')):
        javas += [os.path.join(d, f) for f in fs if f.endswith('.java')]
    endpoints, impl_methods = [], defaultdict(list)
    for jf in javas:
        src = strip_comments(open(jf, encoding='utf-8', errors='ignore').read())
        if '@RestController' in src or '@Controller' in src:
            cls = re.search(r'@RequestMapping\s*\(([^)]*)\)\s*(?:@\w+(?:\([^)]*\))?\s*)*public\s+class', src)
            prefix = (STR_RE.findall(cls.group(1)) or [''])[0] if cls else ''
            for name, defs in methods_of(src).items():
                for body, ann in defs:
                    mm = MAP_RE.search(ann)
                    if not mm:
                        continue
                    verb = mm.group(1).upper()
                    args = mm.group(3) or ''
                    if verb == 'REQUEST':
                        v = re.search(r'RequestMethod\.(\w+)', args); verb = v.group(1) if v else 'GET'
                    paths = STR_RE.findall(args) or ['']
                    calls = re.findall(r'\b\w*[sS]ervice\w*\.(\w+)\s*\(', body)
                    for p in paths:
                        endpoints.append({'verb': verb, 'path': ('/' + prefix + '/' + p).replace('//', '/').replace('//', '/').rstrip('/') or '/', 'controller': name, 'calls': calls})
        elif re.search(r'@Service\b|@Component\b', src):
            for name, defs in methods_of(src).items():
                for body, _ in defs:
                    impl_methods[name].append(body)
    return endpoints, impl_methods


def remote_calls(body):
    """RestTemplate calls in a method body: (target service, verb, literal path prefix)."""
    var_svc = {v: s for v, s in re.findall(r'(\w+)\s*=\s*getServiceUrl\(\s*"(ts-[\w-]+)"\s*\)', body)}
    var_svc.update({v: s for v, s in re.findall(r'(\w+)\s*=\s*"http://(ts-[\w-]+)[^"]*"', body)})
    res = []
    for m in re.finditer(r'restTemplate\.(exchange|getForObject|postForObject|getForEntity|postForEntity)\s*\(', body):
        seg = body[m.end():m.end() + 400]
        svc = None
        mv = re.match(r'\s*(\w+)\s*\+\s*"([^"]*)"', seg)
        if mv and mv.group(1) in var_svc:
            svc, path = var_svc[mv.group(1)], mv.group(2)
        else:
            ml = re.match(r'\s*"http://(ts-[\w-]+)(?::\d+)?([^"]*)"', seg)
            mg = re.match(r'\s*getServiceUrl\(\s*"(ts-[\w-]+)"\s*\)\s*\+\s*"([^"]*)"', seg)
            if ml: svc, path = ml.group(1), ml.group(2)
            elif mg: svc, path = mg.group(1), mg.group(2)
        if not svc:
            continue
        hv = re.search(r'HttpMethod\.(\w+)', seg)
        verb = hv.group(1) if hv else ('POST' if 'post' in m.group(1).lower() else 'GET')
        res.append((svc, verb, path, m.start()))
    return res


def async_sends(body):
    return len(re.findall(r'(?:rabbitTemplate|amqpTemplate|sendService|\w*[eE]ventPublisher)\.\w*(?:convertAndSend|send|publish\w*)\s*\(', body))


def match_endpoint(endpoints, verb, path):
    """Match a literal (possibly variable-completed) URL to a controller endpoint pattern."""
    var_completed = path.endswith('/')      # e.g. ".../stations/id/" + stationName
    lit = path.rstrip('/')
    best, best_score = None, -1
    for ep in endpoints:
        if ep['verb'] != verb:
            continue
        pat = ep['path'].rstrip('/')
        regex = '^' + re.sub(r'\\\{[^}]*\\\}', r'[^/]+', re.escape(pat)) + '$'
        if re.match(regex, lit) and not var_completed:
            score = 1000 + len(pat)
        elif pat.startswith(lit + '/') and re.fullmatch(r'(/\{[^}]+\})+', pat[len(lit):]):
            score = 500 + len(pat)        # literal prefix completed by path variables at runtime
        else:
            continue
        if score > best_score:
            best, best_score = ep, score
    return best


class Analyzer:
    def __init__(self, root):
        self.root = root
        self.cache = {}

    def svc(self, name):
        if name not in self.cache:
            self.cache[name] = load_service(self.root, name) if os.path.isdir(os.path.join(self.root, name)) else ([], {})
        return self.cache[name]

    def calls_of_method(self, svc, mname, seen):
        """Remote calls and async sends reachable from an implementation method (with private helpers)."""
        _, impl = self.svc(svc)
        calls, sends = [], 0
        for body in impl.get(mname, []):
            calls_here = remote_calls(body)
            sends += async_sends(body)
            helper_calls = []
            for h in re.finditer(r'(?<![\w.])(\w+)\s*\(', body):
                hn = h.group(1)
                if hn in impl and hn != mname and (svc, hn) not in seen:
                    helper_calls.append((h.start(), hn))
            events = [(pos, 'remote', c) for (*c, pos) in calls_here] + [(pos, 'helper', hn) for pos, hn in helper_calls]
            for pos, kind, item in sorted(events, key=lambda e: e[0]):
                if kind == 'remote':
                    calls.append(tuple(item))
                else:
                    sub, s2 = self.calls_of_method(svc, item, seen | {(svc, item)})
                    calls += sub; sends += s2
        return calls, sends

    def tree(self, svc, verb, path, depth=1, stack=()):
        eps, impl = self.svc(svc)
        ep = match_endpoint(eps, verb, path)
        node = {'service': svc, 'verb': verb, 'path': path, 'depth': depth, 'children': [], 'async_sends': 0,
                'resolved': ep is not None}
        if not ep or (svc, ep['path']) in stack:
            return node
        calls, sends = [], 0
        for cm in ep['calls']:
            if cm in impl:
                c, s = self.calls_of_method(svc, cm, {(svc, cm)})
                calls += c; sends += s
        node['async_sends'] = sends
        seen_targets = set()
        for tsvc, tverb, tpath in calls:
            if (tsvc, tverb, tpath) in seen_targets:
                continue
            seen_targets.add((tsvc, tverb, tpath))
            node['children'].append(self.tree(tsvc, tverb, tpath, depth + 1, stack + ((svc, ep['path']),)))
        return node


def summarize(node):
    depths, edges, fan, sends, unresolved, chains = [], [], defaultdict(set), 0, [], []
    def walk(n, path):
        nonlocal sends
        depths.append(n['depth']); sends += n['async_sends']
        if not n['resolved']:
            unresolved.append(f"{n['service']} {n['verb']} {n['path']}")
        if not n['children']:
            chains.append(path + [n['service']])
        for c in n['children']:
            edges.append((n['service'], c['service'])); fan[n['service']].add(c['service'])
            walk(c, path + [n['service']])
    walk(node, ['Client'])
    maxd = max(depths)
    return {'max_depth': maxd, 'sync_calls_total': len(depths),
            'deepest_chains': sorted({' -> '.join(c) for c in chains if len(c) - 1 == maxd}),
            'fan_out_distinct': {k: len(v) for k, v in sorted(fan.items())},
            'fan_out_targets': {k: sorted(v) for k, v in sorted(fan.items())},
            'async_sends': sends, 'unresolved_endpoints': unresolved}


def render(n, indent=0):
    s = '  ' * indent + f"[d{n['depth']}] {n['service']} {n['verb']} {n['path']}" + (' (async sends: %d)' % n['async_sends'] if n['async_sends'] else '') + ('' if n['resolved'] else ' [unresolved]') + '\n'
    return s + ''.join(render(c, indent + 1) for c in n['children'])


if __name__ == '__main__':
    root, out = sys.argv[1], sys.argv[2]
    a = Analyzer(root)
    t = a.tree('ts-preserve-service', 'POST', '/api/v1/preserveservice/preserve')
    res = {'root': root, 'entry': 'ts-preserve-service POST /api/v1/preserveservice/preserve', 'summary': summarize(t), 'tree': t}
    json.dump(res, open(out, 'w'), indent=1)
    print(render(t)); print(json.dumps(res['summary'], indent=1))
