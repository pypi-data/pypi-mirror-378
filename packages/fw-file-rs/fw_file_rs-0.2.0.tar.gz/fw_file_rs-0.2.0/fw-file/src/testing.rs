use std::collections::HashMap;
use std::io::{Cursor, Error, ErrorKind, Result, Write};

use dicom_core::DataDictionary;
use dicom_core::header::{DataElement, VR};
use dicom_core::value::PrimitiveValue;
use dicom_dictionary_std::StandardDataDictionary;
use dicom_object::FileMetaTableBuilder;
use dicom_object::mem::InMemDicomObject;
use dicom_transfer_syntax_registry::entries::EXPLICIT_VR_LITTLE_ENDIAN;
use smallvec::SmallVec;

pub enum CreateValue {
    Primitive(PrimitiveValue),
    PrimitiveAndVR(PrimitiveValue, VR),
    Sequence(Vec<HashMap<&'static str, CreateValue>>),
}

macro_rules! impl_from_primitive {
    ($($t:ty),*) => {
        $(
            impl From<$t> for CreateValue {
                fn from(value: $t) -> Self {
                    CreateValue::Primitive(PrimitiveValue::from(value))
                }
            }
        )*
    };
}

impl_from_primitive!(&str, String, i64, f64);

impl From<Vec<i64>> for CreateValue {
    fn from(v: Vec<i64>) -> Self {
        CreateValue::Primitive(PrimitiveValue::I64(SmallVec::from_slice(&v)))
    }
}

impl From<Vec<f64>> for CreateValue {
    fn from(v: Vec<f64>) -> Self {
        CreateValue::Primitive(PrimitiveValue::F64(SmallVec::from_slice(&v)))
    }
}

impl From<Vec<String>> for CreateValue {
    fn from(v: Vec<String>) -> Self {
        CreateValue::Primitive(PrimitiveValue::Strs(SmallVec::from_vec(v)))
    }
}

impl From<Vec<HashMap<&'static str, CreateValue>>> for CreateValue {
    fn from(items: Vec<HashMap<&'static str, CreateValue>>) -> Self {
        CreateValue::Sequence(items)
    }
}

pub fn create_dcm_as_bytes(tags: HashMap<&str, CreateValue>) -> Result<Cursor<Vec<u8>>> {
    let mut obj = InMemDicomObject::new_empty();
    insert_tags(&mut obj, tags)?;

    let ts = EXPLICIT_VR_LITTLE_ENDIAN.erased();
    let file_meta = FileMetaTableBuilder::new()
        .media_storage_sop_class_uid("1.2.840.10008.5.1.4.1.1.2")
        .media_storage_sop_instance_uid("1.2.3.4.5.6.7.8.9")
        .transfer_syntax(EXPLICIT_VR_LITTLE_ENDIAN.uid())
        .implementation_class_uid("1.2.3.4.5.6.7.8.9.10")
        .build()
        .map_err(|e| Error::new(ErrorKind::Other, e.to_string()))?;

    let mut buffer = Cursor::new(Vec::new());
    buffer.write_all(&[0u8; 128])?;
    buffer.write_all(b"DICM")?;
    file_meta
        .write(&mut buffer)
        .map_err(|e| Error::new(ErrorKind::Other, e.to_string()))?;

    obj.write_dataset_with_ts(&mut buffer, &ts)
        .map_err(|e| Error::new(ErrorKind::Other, format!("Write error: {e}")))?;

    buffer.set_position(0);
    Ok(buffer)
}

fn insert_tags(obj: &mut InMemDicomObject, tags: HashMap<&str, CreateValue>) -> Result<()> {
    for (tag_name, value) in tags {
        let tag = StandardDataDictionary
            .parse_tag(tag_name)
            .ok_or_else(|| Error::new(ErrorKind::Other, format!("Invalid tag: {}", tag_name)))?;

        match value {
            CreateValue::Primitive(pv) => {
                let vr = StandardDataDictionary
                    .by_tag(tag)
                    .map(|entry| entry.vr)
                    .unwrap_or(dicom_core::dictionary::VirtualVr::Exact(VR::UN));
                let vr = match vr {
                    dicom_core::dictionary::VirtualVr::Exact(vr) => vr,
                    _ => VR::UN,
                };
                obj.put(DataElement::new(tag, vr, dicom_core::DicomValue::from(pv)));
            }
            CreateValue::PrimitiveAndVR(pv, vr) => {
                obj.put(DataElement::new(tag, vr, dicom_core::DicomValue::from(pv)));
            }
            CreateValue::Sequence(items) => {
                let mut seq_items = Vec::new();
                for item_map in items {
                    let mut item_obj = InMemDicomObject::new_empty();
                    insert_tags(&mut item_obj, item_map)?;
                    seq_items.push(item_obj);
                }
                obj.put(DataElement::new(
                    tag,
                    VR::SQ,
                    dicom_core::value::DataSetSequence::<InMemDicomObject>::new(
                        seq_items,
                        dicom_core::Length::UNDEFINED,
                    ),
                ));
            }
        }
    }
    Ok(())
}
