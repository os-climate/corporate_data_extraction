import pytest
from unittest.mock import patch, Mock

from pathlib import Path
from utils.s3_communication import S3Communication
from utils.core_utils import download_data_from_s3_main_bucket_to_local_folder_if_required, upload_data_from_local_folder_to_s3_interim_bucket_if_required
from utils.settings import get_s3_settings
S3Settings = get_s3_settings()

@pytest.mark.parametrize('s3_usage', [True, False])
def test_download_data_from_s3_main_bucket_to_local_folder_if_required(s3_usage):
    mocked_s3_bucket = Mock(spec=S3Communication)
    mocked_path_local = Mock(spec=Path('path_local'))
    mocked_path_s3 = Mock(spec=Path('path_s3'))
    
    with (patch.object(S3Settings, 's3_usage', s3_usage)):
        download_data_from_s3_main_bucket_to_local_folder_if_required(mocked_s3_bucket, mocked_path_s3, mocked_path_local)
    
    if s3_usage:
        mocked_s3_bucket.download_files_in_prefix_to_dir.assert_called_with(mocked_path_s3, mocked_path_local)
    else:
        mocked_s3_bucket.assert_not_called()
        
        
@pytest.mark.parametrize('s3_usage', [True, False])
def test_upload_data_from_local_folder_to_s3_interim_bucket_if_required(s3_usage):
    mocked_s3_bucket = Mock(spec=S3Communication)
    mocked_path_local = Mock(spec=Path('path_local'))
    mocked_path_s3 = Mock(spec=Path('path_s3'))
    
    with (patch.object(S3Settings, 's3_usage', s3_usage)):
        upload_data_from_local_folder_to_s3_interim_bucket_if_required(mocked_s3_bucket, mocked_path_local, mocked_path_s3)
    
    if s3_usage:
        mocked_s3_bucket.upload_files_in_dir_to_prefix.assert_called_with(mocked_path_local, mocked_path_s3)
    else:
        mocked_s3_bucket.assert_not_called()