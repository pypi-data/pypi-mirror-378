"""
Data models for Mail MCP server
"""

from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


# 邮件大小限制常量（25MB）
MAX_EMAIL_SIZE = 25 * 1024 * 1024  # 25MB in bytes
# 附件数量限制常量
MAX_ATTACHMENTS = 20
# 单个附件大小限制常量（20MB）
MAX_ATTACHMENT_SIZE = 20 * 1024 * 1024  # 20MB in bytes


@dataclass
class EmailAttachment:
    """
    邮件附件数据模型
    
    Attributes:
        filename: 附件文件名
        content_type: 附件内容类型（MIME类型）
        size: 附件大小（字节）
        content: 附件二进制内容（可选）
        attachment_id: 附件唯一标识符（可选）
    """
    filename: str
    content_type: str
    size: int
    content: Optional[bytes] = None
    attachment_id: Optional[str] = None

    def __post_init__(self):
        """初始化后验证"""
        if self.size < 0:
            raise ValueError("Attachment size cannot be negative")
        if self.size > MAX_ATTACHMENT_SIZE:
            raise ValueError(f"Attachment size exceeds maximum limit of {MAX_ATTACHMENT_SIZE} bytes")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，支持JSON序列化"""
        result = {
            'filename': self.filename,
            'content_type': self.content_type,
            'size': self.size
        }
        if self.attachment_id:
            result['attachment_id'] = self.attachment_id
        if self.content:
            # 将二进制内容转换为base64编码的字符串
            result['content'] = base64.b64encode(self.content).decode('utf-8')
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailAttachment':
        """从字典创建附件对象"""
        attachment = cls(
            filename=data['filename'],
            content_type=data['content_type'],
            size=data['size'],
            attachment_id=data.get('attachment_id')
        )
        if 'content' in data and data['content']:
            # 从base64编码的字符串还原二进制内容
            attachment.content = base64.b64decode(data['content'])
        return attachment

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'EmailAttachment':
        """从JSON字符串创建附件对象"""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class EmailMessage:
    """
    邮件消息数据模型
    
    Attributes:
        id: 邮件唯一标识符
        subject: 邮件主题
        from_address: 发件人地址
        to_addresses: 收件人地址列表
        date: 邮件日期
        body_text: 纯文本正文
        body_html: HTML正文（可选）
        attachments: 附件列表
        is_read: 是否已读
        folder: 邮件文件夹名称
        cc_addresses: 抄送地址列表
        bcc_addresses: 密送地址列表
        message_id: 邮件消息ID（可选）
        reply_to: 回复地址（可选）
        flags: 邮件标志列表（可选）
    """
    id: str
    subject: str
    from_address: str
    to_addresses: List[str]
    date: str
    body_text: str
    body_html: Optional[str] = None
    attachments: List[EmailAttachment] = field(default_factory=list)
    is_read: bool = False
    folder: str = "INBOX"
    cc_addresses: List[str] = field(default_factory=list)
    bcc_addresses: List[str] = field(default_factory=list)
    message_id: Optional[str] = None
    reply_to: Optional[str] = None
    flags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """初始化后验证"""
        if not self.id:
            raise ValueError("Email ID cannot be empty")
        if not self.subject:
            raise ValueError("Email subject cannot be empty")
        if not self.from_address:
            raise ValueError("From address cannot be empty")
        if not self.to_addresses:
            raise ValueError("At least one recipient is required")
        if len(self.attachments) > MAX_ATTACHMENTS:
            raise ValueError(f"Number of attachments exceeds maximum limit of {MAX_ATTACHMENTS}")

        # 计算邮件总大小
        total_size = self._calculate_total_size()
        if total_size > MAX_EMAIL_SIZE:
            raise ValueError(f"Total email size exceeds maximum limit of {MAX_EMAIL_SIZE} bytes")

    def _calculate_total_size(self) -> int:
        """计算邮件总大小"""
        # 估算正文大小
        body_size = len(self.body_text.encode('utf-8'))
        if self.body_html:
            body_size += len(self.body_html.encode('utf-8'))

        # 附件大小
        attachments_size = sum(att.size for att in self.attachments)

        # 估算头部大小
        headers_size = len(self.subject.encode('utf-8')) + len(self.from_address.encode('utf-8'))
        headers_size += sum(len(addr.encode('utf-8')) for addr in self.to_addresses)
        headers_size += sum(len(addr.encode('utf-8')) for addr in self.cc_addresses)
        headers_size += sum(len(addr.encode('utf-8')) for addr in self.bcc_addresses)

        return body_size + attachments_size + headers_size

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，支持JSON序列化"""
        result = {
            'id': self.id,
            'subject': self.subject,
            'from_address': self.from_address,
            'to_addresses': self.to_addresses,
            'cc_addresses': self.cc_addresses,
            'bcc_addresses': self.bcc_addresses,
            'date': self.date,
            'body_text': self.body_text,
            'body_html': self.body_html,
            'attachments': [att.to_dict() for att in self.attachments],
            'is_read': self.is_read,
            'folder': self.folder,
            'flags': self.flags
        }

        if self.message_id:
            result['message_id'] = self.message_id
        if self.reply_to:
            result['reply_to'] = self.reply_to

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailMessage':
        """从字典创建邮件对象"""
        return cls(
            id=data['id'],
            subject=data['subject'],
            from_address=data['from_address'],
            to_addresses=data['to_addresses'],
            cc_addresses=data.get('cc_addresses', []),
            bcc_addresses=data.get('bcc_addresses', []),
            date=data['date'],
            body_text=data['body_text'],
            body_html=data.get('body_html'),
            attachments=[EmailAttachment.from_dict(att_data) for att_data in data.get('attachments', [])],
            is_read=data.get('is_read', False),
            message_id=data.get('message_id'),
            folder=data.get('folder', 'INBOX'),
            reply_to=data.get('reply_to'),
            flags=data.get('flags', [])
        )

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2, default=str)

    @classmethod
    def from_json(cls, json_str: str) -> 'EmailMessage':
        """从JSON字符串创建邮件对象"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def get_summary(self) -> Dict[str, Any]:
        """获取邮件摘要信息"""
        return {
            'id': self.id,
            'subject': self.subject,
            'from_address': self.from_address,
            'to_addresses': self.to_addresses,
            'date': self.date,
            'is_read': self.is_read,
            'has_attachments': len(self.attachments) > 0,
            'attachment_count': len(self.attachments),
            'folder': self.folder
        }

    def to_mime_message(self) -> MIMEMultipart:
        """Convert to MIME message for sending"""
        if self.attachments:
            msg = MIMEMultipart()
            msg.attach(MIMEText(self.body_html or self.body_text, 'html' if self.body_html else 'plain'))
        else:
            msg = MIMEText(self.body_html or self.body_text, 'html' if self.body_html else 'plain')

        msg['Subject'] = self.subject
        msg['From'] = self.from_address
        msg['To'] = ', '.join(self.to_addresses)
        if self.cc_addresses:
            msg['Cc'] = ', '.join(self.cc_addresses)

        # Add attachments
        for attachment in self.attachments:
            if attachment.content:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.content)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{attachment.filename}"'
                )
                msg.attach(part)

        return msg


@dataclass
class EmailSearchCriteria:
    """
    邮件搜索条件数据模型
    
    Attributes:
        folder: 搜索的文件夹名称
        from_address: 发件人地址过滤
        to_address: 收件人地址过滤
        subject: 主题过滤
        body_text: 正文内容过滤
        date_from: 开始日期过滤
        date_to: 结束日期过滤
        is_read: 已读状态过滤
        limit: 返回结果数量限制
        offset: 结果偏移量
        has_attachments: 是否有附件过滤
        message_id: 消息ID过滤
    """
    folder: str = "INBOX"
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    subject: Optional[str] = None
    body_text: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    is_read: Optional[bool] = None
    limit: int = 20
    offset: int = 0
    has_attachments: Optional[bool] = None
    message_id: Optional[str] = None

    def __post_init__(self):
        """初始化后验证"""
        if self.limit < 1:
            raise ValueError("Limit must be at least 1")
        if self.limit > 100:
            raise ValueError("Limit cannot exceed 100")
        if self.offset < 0:
            raise ValueError("Offset cannot be negative")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = asdict(self)
        # 移除None值的字段
        return {k: v for k, v in result.items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailSearchCriteria':
        """从字典创建搜索条件对象"""
        return cls(**data)

    def has_filters(self) -> bool:
        """检查是否有过滤条件"""
        return any([
            self.from_address,
            self.to_address,
            self.subject,
            self.body_text,
            self.date_from,
            self.date_to,
            self.is_read is not None,
            self.has_attachments is not None,
            self.message_id
        ])
