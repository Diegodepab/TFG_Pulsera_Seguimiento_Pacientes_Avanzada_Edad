from typing import Dict

from dotenv import load_dotenv
from pydantic import PostgresDsn, BaseSettings, AnyUrl, AnyHttpUrl


class RedisDsn(AnyUrl):
    allowed_schemes = {'redis'}


class APISettings(BaseSettings):
    """
    This class holds default values for the API settings.

    When you create the instance for this the class will try
    to read environment settings to override the default ones
    using the defined prefix, ex:

    db_url will be overridden by the value of the environment variable API_DB_URL if present and not empty
    """

    # DB settings
    db_url      : PostgresDsn = 'postgresql://postgres:postgres@db:5432/bracelet'
    test_db_url : PostgresDsn = None

    # Pagination settings
    pag_default_size : int = 50
    pag_max_size     : int = 2500

    # Redis settings
    redis_url: RedisDsn = 'redis://admin:admin@localhost'

    # Authentication settings
    jwt_secret_key                   : str = ""
    jwt_algorithm                    : str = ""
    jwt_access_token_expire_minutes  : int = 24*60
    jwt_refresh_token_expire_minutes : int = 48*60
    login_max_attempts_until_block   : int = 10
    login_attempts_ttl_minutes       : int = 60*5
    account_block_duration_hours     : int = 24

    # Basic Auth, to override:
    # export API_CLIENTS = '{"client_id": "secret"}'
    clients : Dict[str, str] = {
        'bracelet-platform' : '',
        'front': ''
    }

    # AWS S3 blob storage conf
    s3_access_key_id    : str = ''
    s3_secret_access_key: str = ''
    s3_region           : str = 'eu-west-3'
    s3_bucket           : str = 'bracelet' 
    s3_acl              : str = 'public-read'
    s3_ttl              : int = 3600

    # email conf
    email_smtp_hostname  : str = ''
    email_smtp_port      : int = 465
    email_user_account   : str = ''
    email_from_real_name : str = ''
    email_from_email     : str = ''
    email_password       : str = 'pwdenvio'
    email_enable_ssl     : bool = True
    email_enable_tls     : bool = False

    # email templates conf
    edit_password_redirect_url             : str = 'https://www.bracelet.com/password/edit'
    activate_account_redirect_url          : str = 'https://www.bracelet.com/register'
    unlock_account_token_expire_minutes    : int = 24*60
    reset_password_token_expire_minutes    : int = 24*60
    new_account_token_expire_minutes       : int = 48*60

    # Sentry config
    sentry_dsn   : AnyHttpUrl = "https://bc20d016830644dabf3271eed4762eef@o435580.ingest.sentry.io/5395178"
    sentry_debug : bool       = True

    class Config:
        env_prefix = 'API_'

load_dotenv()

settings = APISettings()  
