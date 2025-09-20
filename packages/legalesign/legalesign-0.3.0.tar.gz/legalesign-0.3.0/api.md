# Attachment

Types:

```python
from legalesign.types import AttachmentResponse, ListMeta, AttachmentListResponse
```

Methods:

- <code title="get /attachment/{attachmentId}/">client.attachment.<a href="./src/legalesign/resources/attachment.py">retrieve</a>(attachment_id) -> <a href="./src/legalesign/types/attachment_response.py">AttachmentResponse</a></code>
- <code title="get /attachment/">client.attachment.<a href="./src/legalesign/resources/attachment.py">list</a>(\*\*<a href="src/legalesign/types/attachment_list_params.py">params</a>) -> <a href="./src/legalesign/types/attachment_list_response.py">AttachmentListResponse</a></code>
- <code title="delete /attachment/{attachmentId}/">client.attachment.<a href="./src/legalesign/resources/attachment.py">delete</a>(attachment_id) -> None</code>
- <code title="post /attachment/">client.attachment.<a href="./src/legalesign/resources/attachment.py">upload</a>(\*\*<a href="src/legalesign/types/attachment_upload_params.py">params</a>) -> None</code>

# Document

Types:

```python
from legalesign.types import (
    DocumentStatusEnum,
    PdfFieldValidationEnum,
    DocumentCreateResponse,
    DocumentRetrieveResponse,
    DocumentListResponse,
    DocumentGetFieldsResponse,
)
```

Methods:

- <code title="post /document/">client.document.<a href="./src/legalesign/resources/document.py">create</a>(\*\*<a href="src/legalesign/types/document_create_params.py">params</a>) -> <a href="./src/legalesign/types/document_create_response.py">DocumentCreateResponse</a></code>
- <code title="get /document/{docId}/">client.document.<a href="./src/legalesign/resources/document.py">retrieve</a>(doc_id) -> <a href="./src/legalesign/types/document_retrieve_response.py">DocumentRetrieveResponse</a></code>
- <code title="get /document/">client.document.<a href="./src/legalesign/resources/document.py">list</a>(\*\*<a href="src/legalesign/types/document_list_params.py">params</a>) -> <a href="./src/legalesign/types/document_list_response.py">DocumentListResponse</a></code>
- <code title="delete /document/{docId}/">client.document.<a href="./src/legalesign/resources/document.py">archive</a>(doc_id) -> None</code>
- <code title="delete /document/{docId}/delete/">client.document.<a href="./src/legalesign/resources/document.py">delete_permanently</a>(doc_id) -> None</code>
- <code title="get /document/{docId}/auditlog/">client.document.<a href="./src/legalesign/resources/document.py">download_audit_log</a>(doc_id) -> BinaryAPIResponse</code>
- <code title="get /document/{docId}/fields/">client.document.<a href="./src/legalesign/resources/document.py">get_fields</a>(doc_id) -> <a href="./src/legalesign/types/document_get_fields_response.py">DocumentGetFieldsResponse</a></code>
- <code title="post /document/preview/">client.document.<a href="./src/legalesign/resources/document.py">preview</a>(\*\*<a href="src/legalesign/types/document_preview_params.py">params</a>) -> None</code>

# Group

Types:

```python
from legalesign.types import GroupRetrieveResponse, GroupListResponse
```

Methods:

- <code title="post /group/">client.group.<a href="./src/legalesign/resources/group.py">create</a>(\*\*<a href="src/legalesign/types/group_create_params.py">params</a>) -> None</code>
- <code title="get /group/{groupId}/">client.group.<a href="./src/legalesign/resources/group.py">retrieve</a>(group_id) -> <a href="./src/legalesign/types/group_retrieve_response.py">GroupRetrieveResponse</a></code>
- <code title="patch /group/{groupId}/">client.group.<a href="./src/legalesign/resources/group.py">update</a>(group_id, \*\*<a href="src/legalesign/types/group_update_params.py">params</a>) -> None</code>
- <code title="get /group/">client.group.<a href="./src/legalesign/resources/group.py">list</a>(\*\*<a href="src/legalesign/types/group_list_params.py">params</a>) -> <a href="./src/legalesign/types/group_list_response.py">GroupListResponse</a></code>

# Invited

Types:

```python
from legalesign.types import InvitedListResponse
```

Methods:

- <code title="get /invited/">client.invited.<a href="./src/legalesign/resources/invited.py">list</a>(\*\*<a href="src/legalesign/types/invited_list_params.py">params</a>) -> <a href="./src/legalesign/types/invited_list_response.py">InvitedListResponse</a></code>
- <code title="delete /invited/{invitedId}/">client.invited.<a href="./src/legalesign/resources/invited.py">delete</a>(invited_id) -> None</code>

# Member

Types:

```python
from legalesign.types import MemberResponse, PermissionsEnum, MemberListResponse
```

Methods:

- <code title="post /member/">client.member.<a href="./src/legalesign/resources/member.py">create</a>(\*\*<a href="src/legalesign/types/member_create_params.py">params</a>) -> None</code>
- <code title="get /member/{memberId}/">client.member.<a href="./src/legalesign/resources/member.py">retrieve</a>(member_id) -> <a href="./src/legalesign/types/member_response.py">MemberResponse</a></code>
- <code title="get /member/">client.member.<a href="./src/legalesign/resources/member.py">list</a>(\*\*<a href="src/legalesign/types/member_list_params.py">params</a>) -> <a href="./src/legalesign/types/member_list_response.py">MemberListResponse</a></code>
- <code title="delete /member/{memberId}/">client.member.<a href="./src/legalesign/resources/member.py">delete</a>(member_id) -> None</code>

# Notifications

Types:

```python
from legalesign.types import WebhookEventFilterEnum, NotificationListResponse
```

Methods:

- <code title="get /notifications/">client.notifications.<a href="./src/legalesign/resources/notifications.py">list</a>() -> <a href="./src/legalesign/types/notification_list_response.py">NotificationListResponse</a></code>

# Pdf

Methods:

- <code title="get /pdf/{docId}/">client.pdf.<a href="./src/legalesign/resources/pdf.py">retrieve</a>(doc_id) -> BinaryAPIResponse</code>
- <code title="post /pdf/preview/">client.pdf.<a href="./src/legalesign/resources/pdf.py">create_preview</a>(\*\*<a href="src/legalesign/types/pdf_create_preview_params.py">params</a>) -> BinaryAPIResponse</code>

# Signer

Types:

```python
from legalesign.types import (
    SignerStatusEnum,
    SignerRetrieveResponse,
    SignerGetRejectionReasonResponse,
    SignerRetrieveFieldsResponse,
)
```

Methods:

- <code title="get /signer/{signerId}/">client.signer.<a href="./src/legalesign/resources/signer.py">retrieve</a>(signer_id) -> <a href="./src/legalesign/types/signer_retrieve_response.py">SignerRetrieveResponse</a></code>
- <code title="get /signer/{signerId}/new-link/">client.signer.<a href="./src/legalesign/resources/signer.py">get_access_link</a>(signer_id) -> None</code>
- <code title="get /signer/{signerId}/rejection/">client.signer.<a href="./src/legalesign/resources/signer.py">get_rejection_reason</a>(signer_id) -> <a href="./src/legalesign/types/signer_get_rejection_reason_response.py">SignerGetRejectionReasonResponse</a></code>
- <code title="post /signer/{signerId}/reset/">client.signer.<a href="./src/legalesign/resources/signer.py">reset</a>(signer_id, \*\*<a href="src/legalesign/types/signer_reset_params.py">params</a>) -> None</code>
- <code title="get /signer/{signerId}/fields1/">client.signer.<a href="./src/legalesign/resources/signer.py">retrieve_fields</a>(signer_id) -> <a href="./src/legalesign/types/signer_retrieve_fields_response.py">SignerRetrieveFieldsResponse</a></code>
- <code title="post /signer/{signerId}/send-reminder/">client.signer.<a href="./src/legalesign/resources/signer.py">send_reminder</a>(signer_id, \*\*<a href="src/legalesign/types/signer_send_reminder_params.py">params</a>) -> None</code>

# Status

Types:

```python
from legalesign.types import StatusResponse, StatusRetrieveAllResponse
```

Methods:

- <code title="get /status/{docId}/">client.status.<a href="./src/legalesign/resources/status.py">retrieve</a>(doc_id) -> <a href="./src/legalesign/types/status_response.py">StatusResponse</a></code>
- <code title="get /status/">client.status.<a href="./src/legalesign/resources/status.py">retrieve_all</a>(\*\*<a href="src/legalesign/types/status_retrieve_all_params.py">params</a>) -> <a href="./src/legalesign/types/status_retrieve_all_response.py">StatusRetrieveAllResponse</a></code>

# Subscribe

Methods:

- <code title="post /subscribe/">client.subscribe.<a href="./src/legalesign/resources/subscribe.py">create_webhook</a>(\*\*<a href="src/legalesign/types/subscribe_create_webhook_params.py">params</a>) -> None</code>

# Template

Types:

```python
from legalesign.types import TemplateRetrieveResponse, TemplateListResponse
```

Methods:

- <code title="post /template/">client.template.<a href="./src/legalesign/resources/template.py">create</a>(\*\*<a href="src/legalesign/types/template_create_params.py">params</a>) -> None</code>
- <code title="get /template/{templateId}/">client.template.<a href="./src/legalesign/resources/template.py">retrieve</a>(template_id) -> <a href="./src/legalesign/types/template_retrieve_response.py">TemplateRetrieveResponse</a></code>
- <code title="patch /template/{templateId}/">client.template.<a href="./src/legalesign/resources/template.py">update</a>(template_id, \*\*<a href="src/legalesign/types/template_update_params.py">params</a>) -> None</code>
- <code title="get /template/">client.template.<a href="./src/legalesign/resources/template.py">list</a>(\*\*<a href="src/legalesign/types/template_list_params.py">params</a>) -> <a href="./src/legalesign/types/template_list_response.py">TemplateListResponse</a></code>
- <code title="delete /template/{templateId}/">client.template.<a href="./src/legalesign/resources/template.py">archive</a>(template_id) -> None</code>

# Templatepdf

Types:

```python
from legalesign.types import TemplatePdf, TemplatepdfListResponse, TemplatepdfGetEditLinkResponse
```

Methods:

- <code title="post /templatepdf/">client.templatepdf.<a href="./src/legalesign/resources/templatepdf/templatepdf.py">create</a>(\*\*<a href="src/legalesign/types/templatepdf_create_params.py">params</a>) -> None</code>
- <code title="get /templatepdf/{pdfId}/">client.templatepdf.<a href="./src/legalesign/resources/templatepdf/templatepdf.py">retrieve</a>(pdf_id) -> <a href="./src/legalesign/types/template_pdf.py">TemplatePdf</a></code>
- <code title="get /templatepdf/">client.templatepdf.<a href="./src/legalesign/resources/templatepdf/templatepdf.py">list</a>(\*\*<a href="src/legalesign/types/templatepdf_list_params.py">params</a>) -> <a href="./src/legalesign/types/templatepdf_list_response.py">TemplatepdfListResponse</a></code>
- <code title="post /templatepdf/{pdfId}/archive/">client.templatepdf.<a href="./src/legalesign/resources/templatepdf/templatepdf.py">archive</a>(pdf_id) -> None</code>
- <code title="post /templatepdf/{pdfId}/tags/">client.templatepdf.<a href="./src/legalesign/resources/templatepdf/templatepdf.py">convert_tags</a>(pdf_id) -> None</code>
- <code title="get /templatepdf/{pdfId}/edit-link/">client.templatepdf.<a href="./src/legalesign/resources/templatepdf/templatepdf.py">get_edit_link</a>(pdf_id) -> str</code>

## Fields

Types:

```python
from legalesign.types.templatepdf import FieldListResponse
```

Methods:

- <code title="post /templatepdf/{pdfId}/fields/">client.templatepdf.fields.<a href="./src/legalesign/resources/templatepdf/fields.py">create</a>(pdf_id, \*\*<a href="src/legalesign/types/templatepdf/field_create_params.py">params</a>) -> None</code>
- <code title="get /templatepdf/{pdfId}/fields/">client.templatepdf.fields.<a href="./src/legalesign/resources/templatepdf/fields.py">list</a>(pdf_id) -> <a href="./src/legalesign/types/templatepdf/field_list_response.py">FieldListResponse</a></code>

# Unsubscribe

Methods:

- <code title="post /unsubscribe/">client.unsubscribe.<a href="./src/legalesign/resources/unsubscribe.py">delete_webhook</a>(\*\*<a href="src/legalesign/types/unsubscribe_delete_webhook_params.py">params</a>) -> None</code>

# User

Types:

```python
from legalesign.types import TimezoneEnum, UserRetrieveResponse
```

Methods:

- <code title="post /user/">client.user.<a href="./src/legalesign/resources/user.py">create</a>(\*\*<a href="src/legalesign/types/user_create_params.py">params</a>) -> None</code>
- <code title="get /user/{userId}/">client.user.<a href="./src/legalesign/resources/user.py">retrieve</a>(user_id) -> <a href="./src/legalesign/types/user_retrieve_response.py">UserRetrieveResponse</a></code>
- <code title="patch /user/{userId}/">client.user.<a href="./src/legalesign/resources/user.py">update</a>(user_id, \*\*<a href="src/legalesign/types/user_update_params.py">params</a>) -> None</code>
