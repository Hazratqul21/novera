"""Local QA fixtures; not part of dist or deployment."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / 'dist'

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?', 1)[0]
        mode = next((m for m in ('no-js', 'reduced') if path.startswith('/'+m+'/')), None)
        if mode: path = path[len(mode)+1:]
        file = (ROOT / path.lstrip('/')).resolve()
        if file.is_dir(): file /= 'index.html'
        if not file.is_relative_to(ROOT) or not file.is_file():
            self.send_error(404)
            return
        content = file.read_bytes()
        if file.suffix == '.html':
            text = content.decode()
            if mode == 'no-js':
                text = re.sub(r'<script\b[^>]*>.*?</script>', '', text, flags=re.S)
            elif mode == 'reduced':
                text = text.replace('<head>', '''<head><script>
                const realMatchMedia = window.matchMedia.bind(window);
                window.matchMedia = q => q.includes('prefers-reduced-motion')
                  ? {matches:true,media:q,addEventListener(){},removeEventListener(){}}
                  : realMatchMedia(q);
                </script>''')
            content = text.encode()
        if file.suffix == '.css' and mode == 'reduced':
            content = re.sub(rb'\(prefers-reduced-motion:\s*reduce\)', b'(min-width:0px)', content)
        self.send_response(200)
        self.send_header('Content-Type', self.guess_type(str(file)))
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1',8093), Handler).serve_forever()
