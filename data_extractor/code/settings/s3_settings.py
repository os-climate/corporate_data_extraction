from pydantic import Field
from pydantic_settings import BaseSettings

class MainBucketSettings(BaseSettings):
    s3_endpoint: str = Field(default='', alias='LANDING_AWS_ENDPOINT', )
    s3_access_key: str = Field(default='', alias='LANDING_AWS_ACCESS_KEY')
    s3_secret_key: str = Field(default='', alias='LANDING_AWS_SECRET_KEY')
    s3_bucket_name: str = Field(default='', alias='LANDING_AWS_BUCKET_NAME')

class InterimBucketSettings(BaseSettings):
    s3_endpoint: str = Field(default='', alias='INTERIM_AWS_ENDPOINT')
    s3_access_key: str = Field(default='', alias='INTERIM_AWS_ACCESS_KEY')
    s3_secret_key: str = Field(default='', alias='INTERIM_AWS_SECRET_KEY')
    s3_bucket_name: str = Field(default='', alias='INTERIM_AWS_BUCKET_NAME')
    
class S3Settings(BaseSettings):
    prefix: str = Field(default='corporate_data_extraction_projects')
    main_bucket: MainBucketSettings = MainBucketSettings()
    interim_bucket: InterimBucketSettings = InterimBucketSettings()
    
class TrainingSettings(BaseSettings):
    pass
