import aiosmtplib

from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate
from typing import List, Optional, Dict
from mako import exceptions as mako_exceptions
from mako.template import Template

from bracelet_lib.exceptions import EmailException


class EmailCtrl:

    # noinspection PyTypeChecker
    def __init__(self):
        self.email_smtp_hostname  : str  = None
        self.email_smtp_port      : int  = None
        self.email_from_real_name : str  = None
        self.email_from_email     : str  = None
        self.email_user_account   : str  = None
        self.email_password       : str  = None
        self.email_enable_ssl     : bool = None
        self.email_enable_tls     : bool = None
        self.email_template_dir   : str  = None

    def init(
            self,
            email_smtp_hostname  : str,
            email_smtp_port      : int,
            email_from_real_name : str,
            email_from_email     : str,
            email_user_account   : str,
            email_password       : str,
            email_enable_ssl     : bool = True,
            email_enable_tls     : bool = False,
            email_template_dir   : str  = None
    ):
        self.email_smtp_hostname   = email_smtp_hostname
        self.email_smtp_port       = email_smtp_port
        self.email_from_real_name  = email_from_real_name
        self.email_from_email      = email_from_email
        self.email_user_account    = email_user_account
        self.email_password        = email_password
        self.email_enable_ssl      = email_enable_ssl
        self.email_enable_tls      = email_enable_tls
        self.email_template_dir    = email_template_dir

    @property
    def is_configured(self):
        return self.email_smtp_hostname is not None

    @staticmethod
    def render_tpl(tpl: str, tpl_data: Dict):
        mako_tpl = Template(tpl, input_encoding='utf-8')

        try:
            rendered = mako_tpl.render(**tpl_data)
        except Exception:
            print( mako_exceptions.text_error_template().render() )
            raise  # stop here

        return rendered

    async def send_email(
            self,
            subject   : str,
            to        : List[str],
            body_txt  : str           = 'Please open this email in an mail client capable of HTML rendering',
            body_html : Optional[str] = None,
            charset   : str           = "utf-8"
    ):
        """
        Function to send email using smtp server
        :return:
        """
        if not self.is_configured:
            raise EmailException(
                error             = 'smtp_not_configured',
                error_description = 'SMTP Server not configured properly'
            )

        mail    = MIMEMultipart()
        content = MIMEText(body_txt, 'plain', _charset=charset)

        if body_html is not None:
            content = MIMEMultipart("alternative")
            content.attach( MIMEText(body_txt, 'plain', _charset=charset) )
            content.attach( MIMEText( body_html, 'html', _charset=charset ) )

        mail.attach( content )

        mail['Date']    = formatdate(localtime=True)
        mail['From']    = formataddr((self.email_from_real_name, self.email_from_email))
        mail['To']      = ', '.join(to)
        mail['Subject'] = Header(subject, charset)

        try:
            # print({
            #     "hostname"  : self.email_smtp_hostname,
            #     "port"      : self.email_smtp_port,
            #     "username"  : self.email_user_account,
            #     "password"  : self.email_password,
            #     "use_tls"   : self.email_enable_ssl,
            #     "start_tls" : self.email_enable_tls
            # })

            await aiosmtplib.send(
                mail,
                hostname  = self.email_smtp_hostname,
                port      = self.email_smtp_port,
                username  = self.email_user_account,
                password  = self.email_password,
                use_tls   = self.email_enable_ssl,
                start_tls = self.email_enable_tls
            )
        except aiosmtplib.errors.SMTPAuthenticationError:
            raise EmailException(
                error             = 'email_login_error',
                error_description = 'Error when try to login to smtp host'
            )
        except aiosmtplib.errors.SMTPException as e:
            print(e)
            raise EmailException(
                error             = 'email_not_controlled_error',
                error_description = 'Generic error, see more details in the API log'
            )


# singleton
email_ctrl = EmailCtrl()
