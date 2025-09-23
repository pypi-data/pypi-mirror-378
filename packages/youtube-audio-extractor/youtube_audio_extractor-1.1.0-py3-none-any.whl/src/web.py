"""Minimal Flask web UI for YouTube Audio Extractor."""

import threading
from typing import List

try:
    from flask import Flask, request, render_template_string, redirect, url_for
except Exception as e:  # pragma: no cover - optional dependency
    Flask = None  # type: ignore

from .main import main as cli_main
from .analytics import generate_report
from .errors import ConversionError
from .main import validate_dependencies
from .history import DownloadHistory
import base64
from datetime import datetime
import os


_JOBS = []

HTML = """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>YouTube Audio Extractor</title>
    <script src=\"https://cdn.tailwindcss.com\"></script>
  </head>
  <body class=\"bg-gray-50\">
    <div class=\"max-w-5xl mx-auto px-4 py-6\">
      <h1 class=\"text-3xl font-bold mb-4\">YouTube Audio Extractor</h1>

      <form method=\"post\" action=\"/start\" enctype=\"multipart/form-data\" class=\"bg-white shadow p-4 rounded mb-4\">
        <label class=\"block text-sm font-medium text-gray-700\">URL or Search Query</label>
        <input class=\"mt-1 w-full border rounded px-3 py-2\" type=\"text\" name=\"url\" placeholder=\"https://www.youtube.com/watch?v=... or search terms\" required />

        <div class=\"grid grid-cols-1 md:grid-cols-3 gap-4 mt-4\">
          <div>
            <label class=\"block text-sm font-medium text-gray-700\">Output Directory</label>
            <input class=\"mt-1 w-full border rounded px-3 py-2\" type=\"text\" name=\"output\" value=\"downloads\" />
          </div>
          <div>
            <label class=\"block text-sm font-medium text-gray-700\">Quality</label>
            <select class=\"mt-1 w-full border rounded px-3 py-2\" name=\"quality\">
              <option value=\"128\">128</option>
              <option value=\"192\">192</option>
              <option value=\"320\" selected>320</option>
            </select>
          </div>
          <div>
            <label class=\"block text-sm font-medium text-gray-700\">Format</label>
            <select class=\"mt-1 w-full border rounded px-3 py-2\" name=\"format\">
              <option value=\"mp3\" selected>mp3</option>
              <option value=\"m4a\">m4a</option>
              <option value=\"opus\">opus</option>
              <option value=\"flac\">flac</option>
            </select>
          </div>
        </div>

        <div class=\"grid grid-cols-1 md:grid-cols-3 gap-4 mt-3\">
          <div>
            <label class=\"block text-sm font-medium text-gray-700\">Min Duration (s)</label>
            <input class=\"mt-1 w-full border rounded px-3 py-2\" type=\"number\" name=\"min\" placeholder=\"e.g. 120\" />
          </div>
          <div>
            <label class=\"block text-sm font-medium text-gray-700\">Max Duration (s)</label>
            <input class=\"mt-1 w-full border rounded px-3 py-2\" type=\"number\" name=\"max\" placeholder=\"e.g. 600\" />
          </div>
          <div>
            <label class=\"block text-sm font-medium text-gray-700\">Search Limit</label>
            <input class=\"mt-1 w-full border rounded px-3 py-2\" type=\"number\" name=\"search_limit\" value=\"5\" />
          </div>
        </div>

        <div class=\"grid grid-cols-1 md:grid-cols-3 gap-4 mt-3\">
          <div>
            <label class=\"block text-sm font-medium text-gray-700\">Include keywords</label>
            <input class=\"mt-1 w-full border rounded px-3 py-2\" type=\"text\" name=\"include\" placeholder=\"comma separated\" />
          </div>
          <div>
            <label class=\"block text-sm font-medium text-gray-700\">Exclude keywords</label>
            <input class=\"mt-1 w-full border rounded px-3 py-2\" type=\"text\" name=\"exclude\" placeholder=\"comma separated\" />
          </div>
          <div>
            <label class=\"block text-sm font-medium text-gray-700\">Cookies (cookies.txt)</label>
            <input class=\"mt-1 w-full border rounded px-3 py-2\" type=\"file\" name=\"cookies\" accept=\".txt\" />
            <p class=\"mt-1 text-xs text-gray-500\">Upload a Netscape-format cookies.txt. Tip: use a browser exporter extension. Or click “Import Cookies (Chrome)” to try automatic import when supported.</p>
          </div>
        </div>

        <div class=\"flex items-center gap-6 mt-3\">
          <label class=\"inline-flex items-center\"><input class=\"mr-2\" type=\"checkbox\" name=\"search\"/> Treat as search query</label>
          <label class=\"inline-flex items-center\"><input class=\"mr-2\" type=\"checkbox\" name=\"resume\"/> Resume (skip downloaded)</label>
          <label class=\"inline-flex items-center\"><input class=\"mr-2\" type=\"checkbox\" name=\"verbose\"/> Verbose</label>
        </div>

        <div class=\"mt-4\">
          <button class=\"bg-blue-600 text-white px-4 py-2 rounded\" type=\"submit\">Start</button>
          <button class=\"ml-2 bg-emerald-600 text-white px-3 py-2 rounded\" type=\"button\" onclick=\"runHealth()\">Run Health</button>
          <button class=\"ml-2 bg-gray-800 text-white px-3 py-2 rounded\" type=\"button\" onclick=\"showStats()\">Show Stats</button>
          <button class=\"ml-2 bg-indigo-700 text-white px-3 py-2 rounded\" type=\"button\" onclick=\"showHistory()\">Show History</button>
        </div>
        <div id=\"msg\" class=\"mt-3 text-sm text-gray-700\"></div>
        <div id=\"panel\" class=\"mt-3 text-sm text-gray-800\"></div>
      </form>

      <div class=\"flex items-center justify-between\">
        <h2 class=\"text-xl font-semibold mb-2\">Jobs</h2>
        <form method=\"post\" action=\"/upload-urls\" enctype=\"multipart/form-data\" class=\"flex items-center gap-2\">
          <input class=\"text-sm\" type=\"file\" name=\"urls\" accept=\".txt\" />
          <button class=\"bg-indigo-600 text-white px-3 py-1 rounded\" type=\"submit\">Upload .txt</button>
        </form>
      </div>
      <div id=\"jobs\" class=\"space-y-3\"></div>

      <div class=\"mt-8 text-xs text-gray-600\">
        <div class=\"bg-yellow-50 border border-yellow-200 rounded p-3\">
          <strong>Legal & Educational Notice:</strong>
          This tool is provided for educational and personal use only. Ensure your use complies with all applicable laws and YouTube's Terms of Service. Only download content you own, have permission to download, or that is in the public domain. The authors assume no liability for misuse.
        </div>
        <div class=\"mt-2\">
          Built by <a class=\"text-blue-600 underline\" href=\"https://github.com/ketchalegend\" target=\"_blank\" rel=\"noopener\">KetchaLegend</a>.
        </div>
      </div>
    </div>

    <script>
      function setMsg(text, ok=true){
        const el = document.getElementById('msg');
        el.textContent = text;
        el.className = 'mt-3 text-sm ' + (ok ? 'text-emerald-700' : 'text-red-700');
      }

      async function fetchJobs(){
        try{
          const r = await fetch('/jobs');
          if(!r.ok){ setMsg('Failed to fetch jobs', false); return; }
          const data = await r.json();
          const el = document.getElementById('jobs');
          el.innerHTML = '';
          if(!data.jobs || !data.jobs.length){ el.innerHTML = '<em class="text-gray-500">No jobs yet</em>'; return; }
          for(const j of data.jobs){
            const div = document.createElement('div');
            div.className = 'bg-white border rounded p-3 shadow-sm';
            const safe = (j.tail||'').replace(/[&<>]/g,s=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[s]));
            const btn = j.status==='running' ? `<button class=\"ml-2 bg-red-600 text-white px-2 py-1 rounded text-xs\" onclick=\"cancelJob('${j.id}')\">Stop</button>` : '';
            div.innerHTML = `<div class=\"flex justify-between items-center\"><div><strong>#${j.id}</strong><span class=\"ml-2 text-sm text-gray-500\">${j.status}</span></div><div>${btn}</div></div>`+
              `<pre class=\"mt-2 whitespace-pre-wrap text-sm text-gray-800\">${safe}</pre>`;
            el.appendChild(div);
          }
        }catch(e){ setMsg('Error updating jobs: '+e, false); }
      }
      setInterval(fetchJobs, 1000);

      async function runHealth(){
        try{
          const r = await fetch('/health', {method:'POST'});
          const t = await r.text();
          setMsg(t, r.ok);
        }catch(e){ setMsg('Health failed: '+e, false); }
      }
      async function showStats(){
        try{
          const r = await fetch('/stats');
          if(!r.ok){ setMsg('Stats failed', false); return; }
          const j = await r.json();
          setMsg('Stats loaded', true);
          const panel = document.getElementById('panel');
          const formats = j.formats ? Object.entries(j.formats).map(([k,v])=>`${k}: ${v}`).join(', ') : '';
          panel.innerHTML = `<div class=\"bg-white border rounded p-3\">`+
            `<div>Total downloads: <strong>${j.total}</strong></div>`+
            `<div>Last download: <strong>${j.pretty_last||j.last||'N/A'}</strong></div>`+
            `<div class=\"mt-1\">Formats: ${formats||'N/A'}</div>`+
            `</div>`;
        }catch(e){ setMsg('Stats failed: '+e, false); }
      }

      async function showHistory(){
        try{
          const r = await fetch('/history');
          if(!r.ok){ setMsg('History failed', false); return; }
          const j = await r.json();
          setMsg('History loaded', true);
          const panel = document.getElementById('panel');
          const rows = j.items.map(it=>`<tr>`+
            `<td class=\"px-2 py-1\">${it.downloaded_at_pretty}</td>`+
            `<td class=\"px-2 py-1\">${it.title}</td>`+
            `<td class=\"px-2 py-1\"><a class=\"text-blue-600 underline\" href=\"${it.download_url}\">Download</a></td>`+
          `</tr>`).join('');
          panel.innerHTML = `<div class=\"bg-white border rounded\">`+
            `<table class=\"w-full text-sm\"><thead><tr class=\"bg-gray-100\"><th class=\"text-left px-2 py-1\">When (UTC)</th><th class=\"text-left px-2 py-1\">Title</th><th class=\"text-left px-2 py-1\">File</th></tr></thead>`+
            `<tbody>${rows}</tbody></table></div>`;
        }catch(e){ setMsg('History failed: '+e, false); }
      }

      async function cancelJob(id){
        try{
          const r = await fetch(`/jobs/${id}/cancel`, {method:'POST'});
          const t = await r.text();
          setMsg(t, r.ok);
        }catch(e){ setMsg('Cancel failed: '+e, false); }
      }

    </script>
  </body>
  </html>
"""


import sys
import threading as _threading
import subprocess


def _run_cli(args: List[str], job: dict | None = None) -> None:
    """Run CLI in a subprocess so we can cancel reliably and stream output."""
    if job is None:
        # Fallback to in-process execution
        try:
            cli_main.main(standalone_mode=True, args=args)  # type: ignore
        except SystemExit:
            pass
        return

    # Build subprocess command using current python
    cmd = [sys.executable, "-m", "src.main", *args]
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
        )
        job['pid'] = proc.pid
        # Stream stdout lines
        assert proc.stdout is not None
        for line in proc.stdout:
            job['tail'] = (job.get('tail', '') + line)[-6000:]
        proc.wait()
        # Final status
        if job.get('status') != 'cancelled':
            job['status'] = 'done' if proc.returncode == 0 else f"error({proc.returncode})"
    except Exception as e:
        job['status'] = 'error'
        job['tail'] = (job.get('tail','') + f"\n{e}")[-6000:]


def create_app():
    if Flask is None:
        raise RuntimeError("Flask is not installed. Install with: pip install Flask")
    app = Flask(__name__)

    @app.get("/")
    def index():  # type: ignore
        return render_template_string(HTML)

    @app.post("/start")
    def start():  # type: ignore
        url = request.form.get("url", "").strip()
        output = request.form.get("output", "downloads").strip() or "downloads"
        quality = request.form.get("quality", "320")
        fmt = request.form.get("format", "mp3")
        # Auto-detect non-URL queries as search even if checkbox not checked
        do_search = request.form.get("search") == "on" or not url.startswith(("http://", "https://"))
        verbose = request.form.get("verbose") == "on"
        resume = request.form.get("resume") == "on"
        min_d = request.form.get("min")
        max_d = request.form.get("max")
        include = request.form.get("include")
        exclude = request.form.get("exclude")
        search_limit = request.form.get("search_limit")

        args = [url, "--quality", quality, "--output", output, "--format", fmt]
        if do_search and not url.startswith(("http://", "https://")):
            args = ["--search"] + args
            if search_limit:
                args = ["--search-limit", str(search_limit)] + args
        if verbose:
            args.append("--verbose")
        if resume:
            args.append("--resume")
        if min_d:
            args += ["--min-duration", str(min_d)]
        if max_d:
            args += ["--max-duration", str(max_d)]
        if include:
            args += ["--include", include]
        if exclude:
            args += ["--exclude", exclude]

        # Optional cookies file upload
        cookie_path = None
        file = request.files.get('cookies')
        if file and file.filename:
            try:
                cookies_dir = os.path.expanduser('~/.youtube-extractor/cookies')
                os.makedirs(cookies_dir, exist_ok=True)
                cookie_path = os.path.join(cookies_dir, f"cookies_{int(datetime.utcnow().timestamp())}.txt")
                file.save(cookie_path)
                args += ["--cookie-path", cookie_path]
            except Exception:
                pass

        job = {'id': str(len(_JOBS)+1), 'status': 'running', 'tail': ''}
        _JOBS.append(job)
        threading.Thread(target=_run_cli, args=(args, job), daemon=True).start()
        return redirect(url_for("index"))

    @app.post('/upload-urls')
    def upload_urls():  # type: ignore
        file = request.files.get('urls')
        if not file:
            return redirect(url_for("index"))
        content = file.read().decode('utf-8', errors='ignore')
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith('#')]

        def build_args(line: str):
            # Syntax: <url> | q=192 | f=m4a | o=~/Music | min=120 | max=600 | include=remix | exclude=live | resume=1 | search=1
            parts = [p.strip() for p in line.split('|')]
            url = parts[0]
            opts = { }
            for seg in parts[1:]:
                if '=' in seg:
                    k, v = seg.split('=', 1)
                    opts[k.strip().lower()] = v.strip()
                else:
                    opts[seg.strip().lower()] = '1'
            quality = opts.get('q') or opts.get('quality') or '320'
            fmt = opts.get('f') or opts.get('format') or 'mp3'
            out = opts.get('o') or opts.get('output') or 'downloads'
            args = [url, "--quality", quality, "--output", out, "--format", fmt]
            if opts.get('resume') in ('1','true','yes'):
                args.append("--resume")
            if opts.get('search') in ('1','true','yes') and not url.startswith(("http://","https://")):
                args = ["--search"] + args
                if opts.get('search-limit'):
                    args = ["--search-limit", str(opts.get('search-limit'))] + args
            if opts.get('min'):
                args += ["--min-duration", str(opts['min'])]
            if opts.get('max'):
                args += ["--max-duration", str(opts['max'])]
            if opts.get('include'):
                args += ["--include", opts['include']]
            if opts.get('exclude'):
                args += ["--exclude", opts['exclude']]
            return args

        for line in lines:
            args = build_args(line)
            job = {'id': str(len(_JOBS)+1), 'status': 'running', 'tail': ''}
            _JOBS.append(job)
            threading.Thread(target=_run_cli, args=(args, job), daemon=True).start()
        return redirect(url_for("index"))

    @app.get('/jobs')
    def jobs():  # type: ignore
        return {'jobs': _JOBS[-20:]}

    @app.post('/jobs/<id>/cancel')
    def cancel(id):  # type: ignore
        for j in _JOBS:
            if j['id'] == id:
                # Try to kill subprocess if present
                j['status'] = 'cancelled'
                pid = j.get('pid')
                if pid:
                    try:
                        import os, signal
                        os.kill(pid, signal.SIGTERM)
                    except Exception:
                        pass
                return 'Cancelled', 200
        return 'Not found', 404

    @app.post('/health')
    def health():  # type: ignore
        try:
            validate_dependencies()
            return 'Health OK', 200
        except ConversionError as e:
            return f'Health failed: {e}', 500
        except Exception as e:
            return f'Health failed: {e}', 500

    @app.get('/stats')
    def stats():  # type: ignore
        rep = generate_report()
        # Convert Counter to plain dict for JSON
        formats = dict(rep.get('formats', {}))
        last_iso = rep.get('last_download_utc')
        pretty = None
        if last_iso:
            try:
                dt = datetime.fromisoformat(last_iso)
                pretty = dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pretty = last_iso
        return {'total': rep.get('total_downloads', 0), 'last': last_iso, 'pretty_last': pretty, 'formats': formats}

    @app.get('/history')
    def history():  # type: ignore
        h = DownloadHistory()
        items = h.recent_downloads(limit=50)
        def make_url(path: str) -> str:
            b = base64.urlsafe_b64encode(path.encode('utf-8')).decode('ascii')
            return f"/download?f={b}"
        payload = [{
            'video_id': it.video_id,
            'title': it.title,
            'file_path': it.file_path,
            'downloaded_at': it.downloaded_at.isoformat(),
            'downloaded_at_pretty': it.downloaded_at.strftime('%Y-%m-%d %H:%M:%S'),
            'download_url': make_url(it.file_path)
        } for it in items]
        return {'items': payload}

    @app.get('/download')
    def download_file():  # type: ignore
        from flask import send_file, abort
        b64 = request.args.get('f', '')
        try:
            decoded = base64.urlsafe_b64decode(b64.encode('ascii')).decode('utf-8')
        except Exception:
            return abort(400)
        # Resolve absolute path
        path = os.path.abspath(os.path.expanduser(decoded))
        if not os.path.exists(path):
            # Try relative to app root
            alt = os.path.abspath(os.path.join(os.getcwd(), decoded))
            if os.path.exists(alt):
                path = alt
            else:
                return abort(404)
        try:
            return send_file(path, as_attachment=True, download_name=os.path.basename(path), mimetype='audio/mpeg')
        except Exception:
            return abort(500)

    @app.post('/import-cookies')
    def import_cookies():  # type: ignore
        """Attempt to export cookies from Chrome into cookies.txt (macOS)."""
        # Best-effort: use macOS default Chrome profile; requires 'cookies' tool if available.
        # Fallback message guides user.
        try:
            base = os.path.expanduser('~/.youtube-extractor/cookies')
            os.makedirs(base, exist_ok=True)
            out_path = os.path.join(base, 'cookies_chrome.txt')
            # Try using 'chrome-export-cookies' if user has it
            rc = os.system(f"chrome-export-cookies > '{out_path}' 2>/dev/null")
            if rc == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                return f'Cookies imported to {out_path}', 200
            # Guidance
            return ('Automatic import not available. Please upload cookies.txt above, or install a cookies exporter extension and export Netscape format.', 501)
        except Exception as e:
            return (f'Import cookies failed: {e}', 500)

    return app


def run():
    import os
    import logging
    app = create_app()
    # Reduce werkzeug request logging noise
    app.logger.disabled = True
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    host = os.environ.get('YAE_HOST', '127.0.0.1')
    port = int(os.environ.get('YAE_PORT') or os.environ.get('PORT') or '5000')
    app.run(host=host, port=port, debug=False)


