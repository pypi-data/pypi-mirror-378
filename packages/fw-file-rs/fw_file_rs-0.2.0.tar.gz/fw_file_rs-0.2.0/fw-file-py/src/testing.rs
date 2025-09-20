use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::collections::HashMap;

use fw_file::testing::{create_dcm_as_bytes as internal_create_dcm_as_bytes, CreateValue};

use crate::PyDicomValue;

#[pyfunction]
pub fn create_dcm_as_bytes(tags: HashMap<String, PyDicomValue>) -> PyResult<Py<PyBytes>> {
    let tags_ref: HashMap<&str, CreateValue> = tags
        .iter()
        .map(|(k, v)| -> PyResult<(&str, CreateValue)> {
            let value = match v {
                PyDicomValue::Int(i) => CreateValue::from(*i),
                PyDicomValue::Float(f) => CreateValue::from(*f),
                PyDicomValue::Str(s) => CreateValue::from(s.clone()),
                PyDicomValue::Strings(v) => CreateValue::from(v.clone()),
                PyDicomValue::Ints(v) => CreateValue::from(v.clone()),
                PyDicomValue::Floats(v) => CreateValue::from(v.clone()),
                PyDicomValue::Unsupported(_) => {
                    return Err(pyo3::exceptions::PyValueError::new_err(
                        "Unsupported value type",
                    ));
                }
            };
            Ok((k.as_str(), value))
        })
        .collect::<PyResult<HashMap<_, _>>>()?;

    let cursor = internal_create_dcm_as_bytes(tags_ref).map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create DCM: {:?}", e))
    })?;

    let py = unsafe { Python::assume_gil_acquired() }; // acquire Python GIL
    Ok(PyBytes::new(py, &cursor.into_inner()).into())
}
