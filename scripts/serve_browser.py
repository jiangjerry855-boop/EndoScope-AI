"""Reassemble the bundled WASM runtime, then serve the browser demo locally."""
from pathlib import Path
from functools import partial
import argparse, hashlib, http.server, json, os

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / 'web/assets/vendor'

def ensure_runtime(destination=None):
    manifest = json.loads((VENDOR / 'wasm-runtime.json').read_text())
    target = Path(destination) if destination is not None else VENDOR / manifest['filename']
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == manifest['sha256']:
        return target
    chunks = []
    for part in manifest['parts']:
        data = (VENDOR / part['path']).read_bytes()
        if len(data) != part['size'] or hashlib.sha256(data).hexdigest() != part['sha256']:
            raise ValueError(f'Runtime part is incomplete: {part["path"]}. Extract the repository again.')
        chunks.append(data)
    data = b''.join(chunks)
    if len(data) != manifest['size'] or hashlib.sha256(data).hexdigest() != manifest['sha256']:
        raise ValueError('Runtime checksum mismatch. Extract the repository again.')
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + '.tmp')
    temporary.write_bytes(data)
    os.replace(temporary, target)
    return target

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--bind', default='127.0.0.1')
    args = parser.parse_args()
    ensure_runtime()
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / 'web'))
    with http.server.ThreadingHTTPServer((args.bind, args.port), handler) as server:
        print(f'Open http://{args.bind}:{args.port}/try/ (Ctrl+C to stop)', flush=True)
        try: server.serve_forever()
        except KeyboardInterrupt: pass
