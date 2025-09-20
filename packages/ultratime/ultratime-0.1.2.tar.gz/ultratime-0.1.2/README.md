# ultratime

**Super fast datetime alternative powered by Rust + PyO3.**

`ultratime` provides a blazing fast datetime implementation by leveraging Rust's performance and safety through [PyO3](https://pyo3.rs/).  
It is designed as a drop-in alternative for Python's built-in `datetime` module when speed matters.

---

## Features
- Written in **Rust** for maximum performance
- Seamless integration with Python via **PyO3**
- Drop-in replacement for common `datetime` usage
- Python 3.8+ support

---

## Installation

You can install from PyPI:

```bash
pip install ultratime
```

## Usage

```python
from ultratime import UltraDateTime, UltraDelta, now_utc, parse_iso8601, parse_format

now = UltraDateTime.now_utc()
print("Now:", now)

dt = UltraDateTime.from_iso8601("2025-09-19T17:30:00+00:00")
print("Parsed ISO8601:", dt)

dt_jakarta = UltraDateTime.from_format("2025-09-19 17:30", "%Y-%m-%d %H:%M", tz="Asia/Jakarta")
print("Jakarta time -> UTC:", dt_jakarta)

dt_ts = UltraDateTime.from_timestamp(1758297000.123456)
print("From timestamp:", dt_ts)

print("Formatted:", dt_ts.format("%Y-%m-%d %H:%M:%S"))

print("As Jakarta:", dt_ts.astimezone("Asia/Jakarta"))

delta = UltraDelta(days=2, seconds=3600, microseconds=500)
print("Delta:", delta, "total_seconds:", delta.total_seconds())

future = dt + delta
past = dt - delta
diff = future - dt
print("Future:", future)
print("Past:", past)
print("Diff in days:", diff.days())
```

---

## LICENSE
This project is licensed under the MIT License.

---

## Youtube & Videos overview

Coming soon