// Cargo.toml dependencies (example):
// [dependencies]
// pyo3 = { version = "0.19", features = ["extension-module", "auto-initialize"] }
// chrono = { version = "0.4", features = ["serde"] }
// chrono-tz = "0.6"

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::class::basic::CompareOp;
use chrono::{DateTime, Utc, NaiveDateTime, TimeZone, Duration, Datelike, Timelike};
use chrono_tz::Tz;

/// Module name tetap "ultratime"
#[pyclass]
#[derive(Clone)]
pub struct UltraDateTime {
    dt: DateTime<Utc>,
}

#[pyclass]
#[derive(Clone)]
pub struct UltraDelta {
    delta: Duration,
}

#[pymethods]
impl UltraDelta {
    /// UltraDelta(days=0, seconds=0, microseconds=0)
    #[new]
    fn new(days: i64, seconds: i64, microseconds: i64) -> Self {
        let total = Duration::days(days) + Duration::seconds(seconds) + Duration::microseconds(microseconds);
        UltraDelta { delta: total }
    }

    #[staticmethod]
    fn from_seconds(seconds: f64) -> Self {
        let secs = seconds.trunc() as i64;
        let micros = ((seconds.fract() * 1e6).round()) as i64;
        UltraDelta { delta: Duration::seconds(secs) + Duration::microseconds(micros) }
    }

    fn total_seconds(&self) -> f64 {
        self.delta.num_seconds() as f64 + (self.delta.num_microseconds().unwrap_or(0) as f64 % 1e6) / 1e6
    }

    fn days(&self) -> i64 { self.delta.num_days() }
    fn seconds(&self) -> i64 { self.delta.num_seconds() % 86400 }
    fn microseconds(&self) -> i64 { self.delta.num_microseconds().unwrap_or(0) % 1_000_000 }

    fn __repr__(&self) -> String {
        format!("<UltraDelta {:?}>", self.delta)
    }
}

#[pymethods]
impl UltraDateTime {
    /// Basic constructors
    #[new]
    fn new() -> Self {
        UltraDateTime { dt: Utc::now() }
    }

    #[staticmethod]
    fn now_utc() -> Self {
        UltraDateTime { dt: Utc::now() }
    }

    #[staticmethod]
    fn now_local() -> Self {
        // chrono doesn't expose local timezone in wasm-free way; use Utc::now() as baseline
        UltraDateTime { dt: Utc::now() }
    }

    /// Parse ISO8601 (RFC3339). Returns UltraDateTime UTC.
    #[staticmethod]
    fn from_iso8601(s: &str) -> PyResult<Self> {
        match DateTime::parse_from_rfc3339(s) {
            Ok(dt) => Ok(UltraDateTime { dt: dt.with_timezone(&Utc) }),
            Err(e) => Err(PyValueError::new_err(format!("Invalid ISO8601 string: {} ({})", s, e))),
        }
    }

    /// Parse with custom format. If tz is provided (like "UTC" or "Asia/Jakarta"), convert to that tz then to UTC.
    #[staticmethod]
    fn from_format(s: &str, fmt: &str, tz: Option<&str>) -> PyResult<Self> {
        match NaiveDateTime::parse_from_str(s, fmt) {
            Ok(naive) => {
                let dt_utc = match tz {
                    Some(tzname) => match tzname.parse::<Tz>() {
                        Ok(tz_parsed) => tz_parsed.from_local_datetime(&naive).single()
                            .map(|localized| localized.with_timezone(&Utc))
                            .ok_or_else(|| PyValueError::new_err(format!("Ambiguous/invalid local time for tz {}", tzname)))?,
                        Err(_) => return Err(PyValueError::new_err(format!("Invalid timezone: {}", tzname))),
                    },
                    None => Utc.from_local_datetime(&naive).single()
                        .unwrap_or_else(|| Utc.from_utc_datetime(&naive)), // assume naive is UTC if no tz
                };
                Ok(UltraDateTime { dt: dt_utc })
            }
            Err(e) => Err(PyValueError::new_err(format!("Failed to parse with format '{}': {} ({})", fmt, s, e))),
        }
    }

    /// From Unix timestamp seconds (can be fractional)
    #[staticmethod]
    fn from_timestamp(ts: f64) -> Self {
        let secs = ts.trunc() as i64;
        let micros = ((ts.fract() * 1e6).round()) as i64;
        UltraDateTime { dt: DateTime::<Utc>::from_utc(NaiveDateTime::from_timestamp(secs, (micros as u32) * 1000), Utc) }
    }

    /// Format like strftime
    fn format(&self, fmt: &str) -> PyResult<String> {
        // chrono::format uses the same patterns as strftime
        Ok(self.dt.format(fmt).to_string())
    }

    /// ISO 8601 string
    fn to_iso8601(&self) -> String {
        self.dt.to_rfc3339()
    }

    /// alias
    fn isoformat(&self) -> String {
        self.to_iso8601()
    }

    /// Return unix timestamp (fractional)
    fn timestamp(&self) -> f64 {
        let secs = self.dt.timestamp();
        let micros = self.dt.timestamp_subsec_micros() as f64;
        secs as f64 + micros / 1e6
    }

    /// Replace components (like datetime.replace)
    fn replace(&self, year: Option<i32>, month: Option<u32>, day: Option<u32>,
            hour: Option<u32>, minute: Option<u32>, second: Option<u32>, microsecond: Option<u32>) -> PyResult<Self> {
        let dt = self.dt;
        let new_naive = NaiveDateTime::new(
            chrono::NaiveDate::from_ymd_opt(
                year.unwrap_or(dt.year()),
                month.unwrap_or(dt.month()),
                day.unwrap_or(dt.day()),
            ).ok_or_else(|| PyValueError::new_err("Invalid date in replace"))?,
            chrono::NaiveTime::from_hms_micro_opt(
                hour.unwrap_or(dt.hour()),
                minute.unwrap_or(dt.minute()),
                second.unwrap_or(dt.second()),
                microsecond.unwrap_or(dt.timestamp_subsec_micros()),
            ).ok_or_else(|| PyValueError::new_err("Invalid time in replace"))?,
        );
        Ok(UltraDateTime { dt: Utc.from_utc_datetime(&new_naive) })
    }

    /// Convert to given timezone string, returns RFC3339 with offset in that tz.
    fn astimezone(&self, tz: &str) -> PyResult<String> {
        match tz.parse::<Tz>() {
            Ok(tz_parsed) => Ok(self.dt.with_timezone(&tz_parsed).to_rfc3339()),
            Err(_) => Err(PyValueError::new_err(format!("Invalid timezone: {}", tz))),
        }
    }

    /// Add timedelta: accept UltraDelta or seconds as float
    fn add(&self, other: &PyAny) -> PyResult<Self> {
        if let Ok(delta) = other.extract::<UltraDelta>() {
            Ok(UltraDateTime { dt: self.dt + delta.delta })
        } else if let Ok(secs) = other.extract::<f64>() {
            let secs_i = secs.trunc() as i64;
            let micros = ((secs.fract() * 1e6).round()) as i64;
            Ok(UltraDateTime { dt: self.dt + Duration::seconds(secs_i) + Duration::microseconds(micros) })
        } else {
            Err(PyValueError::new_err("Unsupported type for add: expected UltraDelta or seconds (float)"))
        }
    }

    /// Subtract either datetime -> returns UltraDelta, or timedelta -> returns UltraDateTime
    fn subtract(&self, other: &PyAny) -> PyResult<PyObject> {
        let py = other.py();
        if let Ok(other_dt) = other.extract::<UltraDateTime>() {
            let diff = self.dt - other_dt.dt;
            Ok(Py::new(py, UltraDelta { delta: diff }).unwrap().into_py(py))
        } else if let Ok(delta) = other.extract::<UltraDelta>() {
            Ok(Py::new(py, UltraDateTime { dt: self.dt - delta.delta }).unwrap().into_py(py))
        } else {
            Err(PyValueError::new_err("Unsupported type for subtract: expected UltraDateTime or UltraDelta"))
        }
    }

    /// Python repr
    fn __repr__(&self) -> String {
        format!("<UltraDateTime {}>", self.dt.to_rfc3339())
    }

    /// Rich compare
    fn __richcmp__(&self, other: PyRef<UltraDateTime>, op: CompareOp) -> PyObject {
        let py = unsafe { Python::assume_gil_acquired() };
        let res = match op {
            CompareOp::Lt => self.dt < other.dt,
            CompareOp::Le => self.dt <= other.dt,
            CompareOp::Eq => self.dt == other.dt,
            CompareOp::Ne => self.dt != other.dt,
            CompareOp::Gt => self.dt > other.dt,
            CompareOp::Ge => self.dt >= other.dt,
        };
        res.into_py(py)
    }

    /// Support + and - via magic methods mapping to add/subtract
    fn __add__(&self, other: &PyAny) -> PyResult<Self> { self.add(other) }
    fn __sub__(&self, other: &PyAny) -> PyResult<PyObject> { self.subtract(other) }
}

#[pymodule]
fn ultratime(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<UltraDateTime>()?;
    m.add_class::<UltraDelta>()?;

    // Tambah fungsi langsung:
    #[pyfunction]
    fn now_utc_py() -> UltraDateTime {
        UltraDateTime::now_utc()
    }
    m.add_function(wrap_pyfunction!(now_utc_py, m)?)?;

    #[pyfunction]
    fn parse_iso8601_py(s: &str) -> PyResult<UltraDateTime> {
        UltraDateTime::from_iso8601(s)
    }
    m.add_function(wrap_pyfunction!(parse_iso8601_py, m)?)?;

    #[pyfunction]
    fn parse_format_py(s: &str, fmt: &str, tz: Option<&str>) -> PyResult<UltraDateTime> {
        UltraDateTime::from_format(s, fmt, tz)
    }
    m.add_function(wrap_pyfunction!(parse_format_py, m)?)?;

    Ok(())
}