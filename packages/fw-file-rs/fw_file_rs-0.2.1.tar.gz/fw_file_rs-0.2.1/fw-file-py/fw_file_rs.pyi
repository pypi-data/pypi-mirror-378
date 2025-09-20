from typing import Any

class PyDCMGroup:
    """A group of DICOM files with shared metadata."""
    paths: list[str]
    is_localizer: bool

class PyDeidProfile:
    """Profile for de-identification of DICOM files."""

    @staticmethod
    def from_yaml(yaml: str) -> "PyDeidProfile":
        """Create a de-identification profile from YAML configuration."""
        ...

    def deid_dcm(self, bytes: bytes) -> bytes:
        """De-identify a DICOM file."""
        ...

def read_until_pixel_data(path: str) -> bytes:
    """Read DICOM file up to the pixel data section."""
    ...

def get_dcm_meta(bytes: bytes, tags: list[str]) -> dict[str, Any]:
    """Extract metadata from DICOM bytes for specified tags."""
    ...

def group_dcm_meta(
    metas: list[tuple[str, dict[str, Any]]],
    group_by_tags: list[str],
    split_localizer: bool
) -> list[PyDCMGroup]:
    """Group DICOM metadata by specified tags."""
    ...

def create_dcm_as_bytes(tags: dict[str, Any]) -> bytes:
    """Create a DICOM file as bytes from tag dictionary."""
    ...
