import pytest

from fw_file_rs import PyDeidProfile, create_dcm_as_bytes, get_dcm_meta


def test_deid_replace_with_valid_date():
    tags = {
        "PatientName": "Test^Patient",
        "StudyDate": "20000101",
    }
    dcm = create_dcm_as_bytes(tags)

    yaml = """
version: 1
name: test profile
dicom:
  fields:
    - name: StudyDate
      replace-with: "20220101"
"""
    profile = PyDeidProfile.from_yaml(yaml)
    result = profile.deid_dcm(dcm)

    meta = get_dcm_meta(result, ["PatientName", "StudyDate"])
    assert meta == {"PatientName": "Test^Patient", "StudyDate": "20220101"}


def test_validate_vr_date_invalid():
    tags = {"StudyDate": "20000101"}
    dcm = create_dcm_as_bytes(tags)

    yaml = """
version: 1
name: test profile
dicom:
  fields:
    - name: StudyDate
      replace-with: "notadate"
"""
    profile = PyDeidProfile.from_yaml(yaml)

    with pytest.raises(ValueError) as e:
        profile.deid_dcm(dcm)

    assert "cannot be parsed as DA" in str(e.value)


def test_profile_unsupported_version():
    yaml = """
version: 99
name: test
dicom: {}
"""
    with pytest.raises(ValueError) as e:
        PyDeidProfile.from_yaml(yaml)

    assert "Unsupported profile version" in str(e.value)
