"""Progress events: one JSON object per line on stdout for the window and tests, and readable lines in a log file.

Every event has "type" and "t" (seconds since the start). Types:

    start     release, dest, log, steps ([{id, title}] in order)
    step      step, state: started | done (seconds) | skipped (reason)
    progress  step, text, and done/total/unit (bytes, chunks, objects) when the amount is known
    warning   text
    error     text, step (absent outside a step)
    end       result: ok | failed | cancelled, seconds

After TotK Recomp installer/events.py @ v0.4.0 (MIT), with the English text in the events (one language for now).
"""
import json
import sys
import threading
import time
from pathlib import Path

PROGRESS_EVERY = 0.4   # seconds between two progress events of one step, unless it is the last


class Reporter:
    def __init__(self, out=None, log_path=None):
        self.out = out or sys.stdout
        self.t0 = time.monotonic()
        self.lock = threading.Lock()
        self.log_file = None
        self.last_progress = {}
        self.log_path = log_path
        if log_path:
            Path(log_path).parent.mkdir(parents=True, exist_ok=True)
            self.log_file = open(log_path, 'a', encoding='utf-8', buffering=1)

    def elapsed(self):
        return time.monotonic() - self.t0

    def log(self, text):
        """A line for the log file only."""
        if self.log_file:
            with self.lock:
                self.log_file.write(f'[{self.elapsed():8.1f}] {text}\n')

    def emit(self, type, **fields):
        event = {'type': type, 't': round(self.elapsed(), 2), **fields}
        with self.lock:
            self.out.write(json.dumps(event, ensure_ascii=False) + '\n')
            self.out.flush()
        if type == 'progress':
            if 'total' in fields:
                self.log(f'{fields.get("text", "")} {fields.get("done")}/{fields["total"]} {fields.get("unit", "")}')
            else:
                self.log(fields.get('text', ''))
        else:
            self.log(json.dumps(event, ensure_ascii=False))
        return event

    def step(self, step, state, **fields):
        return self.emit('step', step=step, state=state, **fields)

    def progress(self, step, text, done=None, total=None, unit=None, force=False):
        """At most one progress event per PROGRESS_EVERY per step, except the first, the last and forced ones."""
        now = time.monotonic()
        last = self.last_progress.get(step)
        final = total is not None and done is not None and done >= total
        if last is not None and not final and not force and now - last < PROGRESS_EVERY:
            return None
        self.last_progress[step] = now
        fields = {'step': step, 'text': text}
        if done is not None and total:
            fields.update(done=done, total=total, unit=unit or '')
        return self.emit('progress', **fields)

    def warning(self, text):
        return self.emit('warning', text=text)

    def error(self, text, step=None):
        return self.emit('error', text=text, **({'step': step} if step else {}))

    def close(self):
        if self.log_file:
            self.log_file.close()
            self.log_file = None


# ---- RecompLauncher: progress lines instead of the events (cli.py --launcher) --------------------------------------
# RecompLauncher (recomplauncher.com) installs and updates the port from the GitHub releases; recomplauncher.json at the
# repository root, copied into each release (tools/make_release.py), tells it how. It runs the setup without a window
# with the game in {install}/MLBTS, a folder no release has, so an update never unpacks over it; after an update it runs
# the setup again, which skips the extraction and rebuilds mlb.exe. It reads the setup's stdout only: the number is its
# progress bar and the text is shown under it, and a failure is the exit code plus the last line, so the error is
# written as a progress line too. ProgressLines is the `out` of Reporter: it reads each JSON event line and writes one
# `progress <0..1> <text>` line. Each step has a share of the bar (WEIGHTS, roughly its part of a first install); a step
# with a known amount moves inside its share. The bar never goes back, and reaches 1 only when the setup ends well.
WEIGHTS = {'check': 2, 'exefs': 3, 'romfs': 55, 'build': 35, 'finish': 5}
OTHER_WEIGHT = 2
BEFORE_END = 0.99


class ProgressLines:
    def __init__(self, stream):
        self.stream = stream
        self.steps = []       # [(id, title)] from the start event
        self.state = {}       # step id -> started | done | skipped
        self.within = 0.0     # 0..1 of the running step, when its amount is known
        self.current = None
        self.best = 0.0
        self.text = ''
        self.last = ''

    # the file interface events.Reporter writes to
    def write(self, text):
        for line in text.splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if isinstance(e, dict):
                self.event(e)
        return len(text)

    def flush(self):
        self.stream.flush()

    def fraction(self):
        weights = {s: WEIGHTS.get(s, OTHER_WEIGHT) for s, _ in self.steps} or {'all': 1}
        done = 0.0
        for s, w in weights.items():
            st = self.state.get(s)
            if st in ('done', 'skipped'):
                done += w
            elif st == 'started' and s == self.current:
                done += w * self.within
        return done / sum(weights.values())

    def event(self, e):
        kind, limit = e.get('type'), BEFORE_END
        if kind == 'start':
            self.steps = [(s.get('id'), s.get('title', '')) for s in e.get('steps', [])]
            return
        if kind == 'step':
            sid, st = e.get('step'), e.get('state')
            self.state[sid] = st
            if st == 'started':
                self.current, self.within = sid, 0.0
                self.text = dict(self.steps).get(sid, sid)
            elif st == 'skipped':
                return
        elif kind == 'progress':
            if e.get('total'):
                self.within = max(self.within, min(1.0, e.get('done', 0) / e['total']))
            self.text = e.get('text') or self.text
        elif kind == 'error':
            self.text = e.get('text', 'The setup failed.')
        elif kind == 'end':
            result = e.get('result')
            if result == 'ok':
                limit = self.best = 1.0
                self.text = 'The game is ready.'
            elif result == 'cancelled':
                self.text = 'The setup was cancelled.'
            elif not self.text:
                self.text = 'The setup failed. The log in the logs folder says why.'
        else:
            return   # warnings stay in the log
        self.best = max(self.best, min(limit, self.fraction()))
        line = f'progress {self.best:.3f} {" ".join(str(self.text).split())}\n'
        if self.text and line != self.last:   # a failure's error and end events say the same thing
            self.last = line
            self.stream.write(line)
            self.stream.flush()
