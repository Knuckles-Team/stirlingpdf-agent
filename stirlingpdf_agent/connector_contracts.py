"""Surface contracts: tool use, links, data locations and business roles."""

from scion_sdk.surface_contracts import (
    BusinessRole,
    DataLocation,
    Refusal,
    SurfaceLink,
    ToolStep,
    ToolUseContract,
)


CONTRACTS = (
    ToolUseContract(
        "check-server-status",
        (
            ToolStep(
                "stirlingpdf_get_status",
                result=("status", "version"),
                refusals=(
                    Refusal("ACCESS_DENIED", "the API key is missing or rejected"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "watermark-a-pdf",
        (
            ToolStep(
                "stirlingpdf_get_status",
                result=("status", "version"),
                refusals=(
                    Refusal("ACCESS_DENIED", "the API key is missing or rejected"),
                ),
            ),
            ToolStep(
                "stirlingpdf_add_watermark",
                params=(
                    "file_base64",
                    "filepath",
                    "filename",
                    "watermarkType",
                    "watermarkText",
                    "opacity",
                    "rotation",
                    "fontSize",
                    "alphabet",
                    "widthSpacer",
                    "heightSpacer",
                ),
                result=("data", "response"),
                refusals=(
                    Refusal(
                        "INVALID_INPUT",
                        "exactly one of file_base64 and filepath is required, and the file must be within the size limit",
                    ),
                    Refusal("ACCESS_DENIED", "the API key is missing or rejected"),
                    Refusal(
                        "INVALID_PARAMETERS",
                        "the instance rejects the operation parameters",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "reshape-a-pdf",
        (
            ToolStep(
                "stirlingpdf_rotate_pdf",
                params=("angle", "file_base64", "filepath", "filename"),
                result=("data", "response"),
                refusals=(
                    Refusal(
                        "INVALID_INPUT",
                        "exactly one of file_base64 and filepath is required, and the file must be within the size limit",
                    ),
                    Refusal("ACCESS_DENIED", "the API key is missing or rejected"),
                    Refusal(
                        "INVALID_PARAMETERS",
                        "the instance rejects the operation parameters",
                    ),
                ),
            ),
            ToolStep(
                "stirlingpdf_compress_pdf",
                params=("optimize_level", "file_base64", "filepath", "filename"),
                result=("data", "response"),
                refusals=(
                    Refusal(
                        "INVALID_INPUT",
                        "exactly one of file_base64 and filepath is required, and the file must be within the size limit",
                    ),
                    Refusal("ACCESS_DENIED", "the API key is missing or rejected"),
                    Refusal(
                        "INVALID_PARAMETERS",
                        "the instance rejects the operation parameters",
                    ),
                ),
            ),
            ToolStep(
                "stirlingpdf_split_pdf",
                params=("page_numbers", "file_base64", "filepath", "filename"),
                result=("data", "response"),
                refusals=(
                    Refusal(
                        "INVALID_INPUT",
                        "exactly one of file_base64 and filepath is required, and the file must be within the size limit",
                    ),
                    Refusal("ACCESS_DENIED", "the API key is missing or rejected"),
                    Refusal(
                        "INVALID_PARAMETERS",
                        "the instance rejects the operation parameters",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "merge-pdfs",
        (
            ToolStep(
                "stirlingpdf_merge_pdfs",
                params=("files_base64", "sort_type"),
                result=("data", "response"),
                refusals=(
                    Refusal("TOO_FEW_FILES", "fewer than two files were supplied"),
                    Refusal("ACCESS_DENIED", "the API key is missing or rejected"),
                    Refusal(
                        "INVALID_PARAMETERS",
                        "the instance rejects the operation parameters",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "protect-a-pdf",
        (
            ToolStep(
                "stirlingpdf_add_password",
                params=(
                    "password",
                    "owner_password",
                    "file_base64",
                    "filepath",
                    "filename",
                ),
                result=("data", "response"),
                refusals=(
                    Refusal(
                        "INVALID_INPUT",
                        "exactly one of file_base64 and filepath is required, and the file must be within the size limit",
                    ),
                    Refusal("ACCESS_DENIED", "the API key is missing or rejected"),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the user has not approved encrypting the file",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "unlock-a-pdf",
        (
            ToolStep(
                "stirlingpdf_remove_password",
                params=("password", "file_base64", "filepath", "filename"),
                result=("data", "response"),
                refusals=(
                    Refusal(
                        "INVALID_INPUT",
                        "exactly one of file_base64 and filepath is required, and the file must be within the size limit",
                    ),
                    Refusal("ACCESS_DENIED", "the API key is missing or rejected"),
                    Refusal("WRONG_PASSWORD", "the password does not open the file"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "sanitize-a-pdf",
        (
            ToolStep(
                "stirlingpdf_sanitize_pdf",
                params=(
                    "remove_javascript",
                    "remove_embedded_files",
                    "remove_metadata",
                    "remove_links",
                    "file_base64",
                    "filepath",
                    "filename",
                ),
                result=("data", "response"),
                refusals=(
                    Refusal(
                        "INVALID_INPUT",
                        "exactly one of file_base64 and filepath is required, and the file must be within the size limit",
                    ),
                    Refusal("ACCESS_DENIED", "the API key is missing or rejected"),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the user has not approved removing content from the file",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "record-tools-in-graph",
        (
            ToolStep(
                "stirlingpdf_ingest_tools",
                result=("listed", "ingested"),
                refusals=(
                    Refusal(
                        "NO_ENGINE",
                        "no knowledge-graph engine is reachable, ingested is null",
                    ),
                ),
            ),
        ),
    ),
)

LINKS = (
    SurfaceLink(
        "check-server-status",
        tools=("stirlingpdf_get_status",),
        prompts=("stirlingpdf-operator", "stirlingpdf-platform-administrator"),
        skills=("stirlingpdf-agent-docs",),
    ),
    SurfaceLink(
        "watermark-a-pdf",
        tools=("stirlingpdf_get_status", "stirlingpdf_add_watermark"),
        prompts=("stirlingpdf-operator", "stirlingpdf-document-processor"),
        skills=("stirlingpdf-watermarking",),
    ),
    SurfaceLink(
        "reshape-a-pdf",
        tools=(
            "stirlingpdf_rotate_pdf",
            "stirlingpdf_compress_pdf",
            "stirlingpdf_split_pdf",
        ),
        prompts=("stirlingpdf-operator", "stirlingpdf-document-processor"),
        skills=("stirlingpdf-document-operations",),
    ),
    SurfaceLink(
        "merge-pdfs",
        tools=("stirlingpdf_merge_pdfs",),
        prompts=("stirlingpdf-operator", "stirlingpdf-document-processor"),
        skills=("stirlingpdf-document-operations",),
    ),
    SurfaceLink(
        "protect-a-pdf",
        tools=("stirlingpdf_add_password",),
        prompts=("stirlingpdf-operator", "stirlingpdf-security-officer"),
        skills=("stirlingpdf-document-operations",),
    ),
    SurfaceLink(
        "unlock-a-pdf",
        tools=("stirlingpdf_remove_password",),
        prompts=("stirlingpdf-operator", "stirlingpdf-security-officer"),
        skills=("stirlingpdf-document-operations",),
    ),
    SurfaceLink(
        "sanitize-a-pdf",
        tools=("stirlingpdf_sanitize_pdf",),
        prompts=("stirlingpdf-operator", "stirlingpdf-security-officer"),
        skills=("stirlingpdf-document-operations",),
    ),
    SurfaceLink(
        "record-tools-in-graph",
        tools=("stirlingpdf_ingest_tools",),
        prompts=("stirlingpdf-operator", "stirlingpdf-platform-administrator"),
        skills=("stirlingpdf-knowledge-graph",),
    ),
    SurfaceLink(
        "stirlingpdf-agent-operations",
        tools=(
            "stirlingpdf_get_status",
            "stirlingpdf_add_watermark",
            "stirlingpdf_compress_pdf",
        ),
        skills=("stirlingpdf-agent-operations",),
    ),
    SurfaceLink(
        "stirlingpdf-agent-docs",
        tools=("stirlingpdf_get_status",),
        skills=("stirlingpdf-agent-docs",),
    ),
)

LOCATIONS = (
    DataLocation(
        "stirlingpdf-instance",
        ("PdfTool", "PdfOperation"),
        "STIRLINGPDF_URL",
        "stirlingpdf_get_status",
    ),
    DataLocation(
        "stirlingpdf-input-files",
        ("Document",),
        "STIRLINGPDF_URL",
        "stirlingpdf_add_watermark",
        federation_key="filename",
    ),
    DataLocation(
        "stirlingpdf-output-files",
        ("PdfOperation", "Watermark"),
        "STIRLINGPDF_URL",
        "stirlingpdf_compress_pdf",
        federation_key="sha256",
    ),
)

ROLES = (
    BusinessRole(
        "document-processor", tasks=("watermark-a-pdf", "reshape-a-pdf", "merge-pdfs")
    ),
    BusinessRole(
        "security-officer", tasks=("protect-a-pdf", "unlock-a-pdf", "sanitize-a-pdf")
    ),
    BusinessRole(
        "platform-administrator", tasks=("check-server-status", "record-tools-in-graph")
    ),
)
