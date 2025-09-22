use mimetype_detector::detect as internal_detect;
use pyo3::prelude::*;

/// Detects the mime type of a byte array.
#[pyfunction]
fn detect_mime(bytes: &[u8]) -> PyResult<String> {
    Ok(internal_detect(bytes).mime().to_string())
}

/// Detects the extension of a byte array.
#[pyfunction]
fn detect_type(bytes: &[u8]) -> PyResult<String> {
    Ok(internal_detect(bytes).extension().to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn mimey(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(detect_mime, m)?)?;
    m.add_function(wrap_pyfunction!(detect_type, m)?)?;
    Ok(())
}
