# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for .....
"""
from io import StringIO
import os
from azure.storage.blob import ContainerClient, ContentSettings
import uuid
import pandas
import time
import requests
import logging
import sys
from .._utils._constants import ACCOUNT, DATA_INGESTION_CONTAINER
from .._utils._utils import ApiInputs

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


class Queue:
    """ """
    @staticmethod
    def get_next_messages(account: ACCOUNT, container: str, queue_name: str, message_count: int = 1):
        """Retrieve next message(s).

        Parameters
        ----------
        account : ACCOUNT
            Azure account
        container : str
            Queue container.
        queue_name : str
            Queue name.
        message_count : int
            Message count to retrieve (Default value = 1).

        Returns
        -------

        """
        pass

    @staticmethod
    def send_message(account: ACCOUNT, container, queue_name, messages: list = None):
        """Send message

        Parameters
        ----------
        account : ACCOUNT
            Azure account.
        container : str
            Queue container.
        queue_name : str
            Queue name.
        messages : list, default = None
            Message (Default value = None).

        Returns
        -------

        """
        if messages is None:
            messages = []

        pass


class Blob:
    """ """
    @staticmethod
    def list(api_inputs: ApiInputs, account: ACCOUNT, container: str, prefix: str = None):
        """Retrieve list of blobs.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize() function.
        account : ACCOUNT
            Azure account.
        container : str
            Blob container.
        prefix : str, default=None
            Prefix (Default value = None).

        Returns
        -------

        """

        if not set([account]).issubset(set(ACCOUNT.__args__)):
            logger.error('account parameter must be set to one of the allowed values defined by the '
                         'ACCOUNT literal: %s', ACCOUNT.__args__)
            return False

        if prefix is None:
            prefix = ''

        container_con_string = _get_container_sas_uri(api_inputs, container, account)
        container_client = ContainerClient.from_container_url(container_con_string)

        blob_list = container_client.list_blobs(name_starts_with=prefix)
        for blob in blob_list:
            logger.info('%s - %s', blob.name, str(blob.last_modified))
        return True

    @staticmethod
    def download(api_inputs: ApiInputs, account: ACCOUNT, container: str, blob_name: str):
        """

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize() function.
        account : ACCOUNT
            Azure account
        container : str
            Blob container.
        blob_name : str
            Blob name.

        Returns
        -------

        """
        if not set([account]).issubset(set(ACCOUNT.__args__)):
            logger.error('account parameter must be set to one of the allowed values defined by the '
                         'ACCOUNT literal: %s', ACCOUNT.__args__)
            return False

        container_con_string = _get_container_sas_uri(api_inputs, container, account)
        container_client = ContainerClient.from_container_url(container_con_string)

        blob_client = container_client.get_blob_client(blob_name)

        return blob_client.download_blob().readall()

    @staticmethod
    def upload(api_inputs: ApiInputs, data_frame: pandas.DataFrame, name: str, batch_id: uuid.UUID = None, account: ACCOUNT = 'DataIngestion',
               container: DATA_INGESTION_CONTAINER = 'data-ingestion-adx', folder: str = 'to-ingest', include_header: bool = False):
        """Upload data to blob.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize() function.
        account: ACCOUNT, optional
            Blob account data will be uploaded to (Default value = 'DataIngestion').
        data_frame : pandas.DataFrame
            Dataframe containing the data to be uploaded to blob.
        name : str
            Name.
        batch_id : str
            Data feed file status id.
        folder: str
            Top folder inside the container assigned to the uploaded blob. (Default value = 'to-ingest')
        container: DATA_INGESTION_CONTAINER
            Container name (Literal) to where the blob goes into. (Default value = 'data-ingestion-adx')
        include_header: bool
            Boolean if include data frame's headers in the output file.
            Default to False

        Returns
        -------

        """
        csv_df = data_frame.copy()
        
        # Get size in bytes
        def get_csv_size(df):
            buffer = StringIO()
            df.to_csv(buffer, index=False)
            size_in_bytes = buffer.tell()  
            buffer.close()
            return size_in_bytes

        # Splitting DataFrame into chunks
        def split_dataframe(df, chunk_size):
            for i in range(0, len(df), chunk_size):
                yield df.iloc[i:i + chunk_size]
                
        def format_size(bytes_size):
            # Define size units in increasing order
            units = ['B', 'KB', 'MB', 'GB', 'TB']
            size = bytes_size
            unit_index = 0

            # Divide size until it's smaller than 1024 or we run out of units
            while size >= 1024 and unit_index < len(units) - 1:
                size /= 1024
                unit_index += 1

            return f"{size:.2f} {units[unit_index]}"

                
        # 3 MB in bytes
        max_size = 3 * 1024 * 1024  

        if not set([account]).issubset(set(ACCOUNT.__args__)):
            logger.error('account parameter must be set to one of the allowed values defined by the '
                         'ACCOUNT literal: %s', ACCOUNT.__args__)
            return False

        if not set([container]).issubset(set(DATA_INGESTION_CONTAINER.__args__)):
            logger.error('container parameter must be set to one of the allowed values defined by the '
                         'DATA_INGESTION_CONTAINER literal: %s', DATA_INGESTION_CONTAINER.__args__)
            return False

        if batch_id is None or batch_id == '00000000-0000-0000-0000-000000000000' or batch_id == '':
            if api_inputs.data_feed_file_status_id is None \
                    or api_inputs.data_feed_file_status_id == '00000000-0000-0000-0000-000000000000':
                batch_id = uuid.uuid4()
            else:
                batch_id = api_inputs.data_feed_file_status_id

        container_con_string = _get_container_sas_uri(api_inputs, container, account, True)
        container_client = ContainerClient.from_container_url(container_con_string)

        csv_size = get_csv_size(csv_df)
        logger.info(f"Total Dataframe File Size: {format_size(csv_size)}")
        rows_per_partition = max_size // (csv_size / len(csv_df))
        chunk_size = int(rows_per_partition)

        upload_path = f"{folder}/{api_inputs.api_project_id}/{name}/{batch_id}/{time.time_ns()}_"

        item_counter = 0
        for i, current_data_frame in enumerate(split_dataframe(csv_df, chunk_size)):
            item_counter += 1
            blob_name = upload_path + str(item_counter) + ".csv"
            logger.info("Uploading ... %s, file size=%s",
                        blob_name, format_size(get_csv_size(current_data_frame)))
            blob_client = container_client.get_blob_client(blob_name)

            if pandas.__version__ < "1.5.0":
                data_csv = bytes(current_data_frame.to_csv(line_terminator='\r\n', index=False, header=include_header),
                                 encoding='utf-8')
            elif pandas.__version__ >= "1.5.0":
                data_csv = bytes(current_data_frame.to_csv(lineterminator='\r\n', index=False, header=include_header),
                                 encoding='utf-8')
            blob_client.upload_blob(
                data_csv, blob_type="BlockBlob", overwrite=True)


        return upload_path, item_counter

    @staticmethod
    def custom_upload(api_inputs: ApiInputs, account: ACCOUNT, container: str, upload_path: str, file_name: str,
                      upload_object):
        """Upload data to blob.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize() function.
        account: ACCOUNT
            Blob account data will be uploaded to.
        container : str
            Blob container.
        upload_path: str
            The prefix required to navigate from the base `container` to the folder the `upload_object` should be
            uploaded to.
        file_name : str
            File name to be stored in blob.
        upload_object :
            Object to be uploaded to blob.

        Returns
        -------

        """
        if not set([account]).issubset(set(ACCOUNT.__args__)):
            logger.error('account parameter must be set to one of the allowed values defined by the '
                         'ACCOUNT literal: %s', ACCOUNT.__args__)
            return False

        container_con_string = _get_container_sas_uri(api_inputs, container, account, True)
        container_client = ContainerClient.from_container_url(container_con_string)

        if upload_path.endswith('/') == False:
            blob_name = upload_path + '/' + file_name
        elif upload_path.endswith('/') == True:
            blob_name = upload_path + file_name

        logger.info('Uploading to blob: %s', blob_name)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(upload_object, blob_type="BlockBlob", overwrite=True)

    @staticmethod
    def _guide_blob_upload(api_inputs: ApiInputs, local_folder_path: str, driver_id: uuid.UUID):
        """Upload folder files to Guides' blob storage.

        Returns
        -------

        """
        account = "DataIngestion"
        container_name = "guides-form"
        blob_prefix = driver_id + "/"

        # Get a reference to the container
        container_con_string = _get_container_sas_uri(api_inputs, container_name, account, True)
        container_client = ContainerClient.from_container_url(container_con_string)

        # Get a list of files in the local folder
        files = [f for f in os.listdir(local_folder_path) if os.path.isfile(
            os.path.join(local_folder_path, f))]

        try:
            # Upload each file to storage
            for root, _, files in os.walk(local_folder_path):
                for file_name in files:
                    local_file_path = os.path.join(root, file_name)
                    blob_name = blob_prefix + os.path.relpath(local_file_path, local_folder_path).replace(
                        os.path.sep, "/")

                    with open(local_file_path, "rb") as data:
                        container_client.upload_blob(name=blob_name, data=data, content_settings=ContentSettings(
                            content_type='application/octet-stream'), overwrite=True)

                    logger.info(f"Uploaded {local_file_path} to {blob_name}")

            return True
        except Exception as exc:
            logger.exception(str(exc))
            return False


def _get_ingestion_service_bus_connection_string(api_inputs: ApiInputs, queue_type: str = 'DataIngestion'):
    """
    Get connection string specific to Data Ingestion Service Bus

    Parameters
    ----------
    api_inputs : ApiInputs
            Object returned by initialize() function.

    Returns
    -------
    str
        Data Ingestion Service Bus connection string
    """
    headers = api_inputs.api_headers.default

    if not queue_type or queue_type == '':
        queue_type = 'DataIngestion'

    params = {'serviceBusType': queue_type}

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/data-feed/service-bus"
    response = requests.request("GET", url, timeout=20, headers=headers, params=params)

    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return None
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return None

    return response.text


def _get_container_sas_uri(api_inputs: ApiInputs, container: str, account: ACCOUNT = 'SwitcStorage', writable: bool = False):
    """
    Get container connection string from specified Storage Account

    Parameters
    ----------
    api_inputs : ApiInputs
            Object returned by initialize() function.
    container: str
        Name of the container under the account specified
    account : ACCOUNT, default = 'SwitchStorage'x
         (Default value = 'SwitchStorage')
    writable: bool
        Sets permissions expectation for the generated SAS Uri

    Returns
    -------
    str
        container connection string
    """

    if container == None or len(container) == 0:
        logger.error('Must set a container to get Container connection string.')

    headers = api_inputs.api_headers.default
    expire_after_hours = 1

    payload = {
        "storageOptions": __get_storage_options(account),
        "containerName": container,
        "expireAfterHours": expire_after_hours,
        "isWritable": writable
    }

    url = f"{api_inputs.api_base_url}/blob/container-sas"
    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return ""
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return ""

    return response.text


def _get_structure(df):
    """Get dataframe structure

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------

    """

    a = df.dtypes
    a = pandas.Series(a)
    a = a.reset_index().rename(columns={0: 'dtype'})
    a['dtype'] = a['dtype'].astype('str')
    a.set_index('index', inplace=True)
    a = a.to_dict()
    return a['dtype']


def __get_storage_options(account: ACCOUNT):
    """
    Get Storage Account Options. Currently the existing account literal doesn't match the Enum equivalent of storage
    options in the API, so we have this method

    Parameters
    ----------
    account : ACCOUNT
        Account to map API storage account options

    Returns
    -------
    str
        API equivalent account storage name
    """

    if account == None or len(account) == 0:
        logger.error('Mapping to storage options requires Account Parameter Value.')
        return account

    if account == 'SwitchStorage':
        return 'LegacySwitchStorage'
    elif account == 'SwitchContainer':
        return 'LegacySwitchContainer'
    elif account == 'Argus':
        return 'ArgusStorage'
    elif account == 'DataIngestion':
        return 'DataIngestionStorage'
    elif account == 'SwitchGuides':
        return 'DataIngestionStorage'

    return account
