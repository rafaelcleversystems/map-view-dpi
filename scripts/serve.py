"""Optional loopback-only server. Direct index.html opening needs no Python."""
import argparse, functools, http.server, pathlib, webbrowser
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8080);a=p.parse_args()
root=pathlib.Path(__file__).resolve().parents[1]
with http.server.ThreadingHTTPServer(('127.0.0.1',a.port),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root))) as server:
 print(f'MapView: http://127.0.0.1:{a.port} (Ctrl+C para encerrar)',flush=True)
 webbrowser.open(f'http://127.0.0.1:{a.port}')
 try:server.serve_forever()
 except KeyboardInterrupt:pass
