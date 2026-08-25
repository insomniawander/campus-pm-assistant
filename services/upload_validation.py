from pathlib import Path


SUPPORTED_UPLOAD_TYPES = ("xlsx", "xlsm", "xls")
DEFAULT_MAX_UPLOAD_BYTES = 50 * 1024 * 1024


class UploadValidationError(ValueError):
    """An upload that cannot safely be passed to the workbook parser."""


def validate_excel_upload(uploaded_file, max_bytes=DEFAULT_MAX_UPLOAD_BYTES):
    name = str(getattr(uploaded_file, "name", "") or "").strip()
    suffix = Path(name).suffix.lower().lstrip(".")
    if suffix not in SUPPORTED_UPLOAD_TYPES:
        supported = "、".join(f".{item}" for item in SUPPORTED_UPLOAD_TYPES)
        raise UploadValidationError(f"不支持 {Path(name).suffix or '无扩展名'} 文件，请上传 {supported}。")

    try:
        content = uploaded_file.getvalue()
    except Exception as exc:
        raise UploadValidationError("浏览器未能完整读取该文件，请重新选择后再试。") from exc

    if not content:
        raise UploadValidationError("文件内容为空。")
    if len(content) > max_bytes:
        limit_mb = max_bytes // (1024 * 1024)
        actual_mb = len(content) / (1024 * 1024)
        raise UploadValidationError(f"文件为 {actual_mb:.1f} MB，超过 {limit_mb} MB 的单文件限制。")

    # Modern Office files are ZIP containers; legacy .xls files use OLE.
    expected_signature = b"\xd0\xcf\x11\xe0" if suffix == "xls" else b"PK"
    if not content.startswith(expected_signature):
        raise UploadValidationError("文件内容与扩展名不一致，或文件已经损坏。")
    return bytes(content)

