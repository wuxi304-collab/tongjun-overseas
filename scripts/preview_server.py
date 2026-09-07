#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path=self.path.split('?',1)[0].split('#',1)[0]
        if path=='/': self.path='/index.html'
        elif '.' not in Path(path).name:
            candidate=ROOT/(path.lstrip('/')+'.html')
            if candidate.exists():
                tail=''
                if '?' in self.path: tail='?'+self.path.split('?',1)[1]
                self.path=path+'.html'+tail
        return super().do_GET()
if __name__=='__main__':
    port=8766
    print(f'Tongjun V14 preview: http://127.0.0.1:{port}')
    ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
