use pyo3::prelude::*;
use chrono::{Utc, DateTime, NaiveDateTime};

#[pyfunction]
fn now_utc() -> String {
    Utc::now().to_rfc3339()
}

#[pyfunction]
fn parse_iso8601(s: &str) -> PyResult<String> {
    match DateTime::parse_from_rfc3339(s) {
        Ok(dt) => Ok(dt.to_rfc3339()),
        Err(_) => Err(pyo3::exceptions::PyValueError::new_err("Invalid ISO8601 string")),
    }
}

#[pyfunction]
fn parse_simple(s: &str) -> PyResult<String> {
    match NaiveDateTime::parse_from_str(s, "%Y-%m-%d %H:%M:%S") {
        Ok(dt) => Ok(dt.to_string()),
        Err(_) => Err(pyo3::exceptions::PyValueError::new_err("Invalid simple datetime string")),
    }
}

#[pyfunction]
fn format_now(fmt: &str) -> String {
    Utc::now().format(fmt).to_string()
}

#[pymodule]
fn ultratime(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(now_utc, m)?)?;
    m.add_function(wrap_pyfunction!(parse_iso8601, m)?)?;
    m.add_function(wrap_pyfunction!(parse_simple, m)?)?;
    m.add_function(wrap_pyfunction!(format_now, m)?)?;
    Ok(())
}
