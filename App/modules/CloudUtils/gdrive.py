from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import requests
import shutil
import os
import sys
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
def delete_folder(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
        return 1
    else:
        return 0

def authenticate():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    client_secrets_path = os.path.join(current_dir, 'client_secrets.json')
    credentials_path = os.path.join(current_dir, 'credentials.json')

    gauth = GoogleAuth()

    gauth.LoadClientConfigFile(client_secrets_path)
    gauth.LoadCredentialsFile(credentials_path)
    if gauth.credentials is None:
        print("lmao")
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        print(gauth)
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile(credentials_path)
    return gauth

def upload(filepath,folderid):
    gauth=authenticate()

    drive = GoogleDrive(gauth)
    
    file_name = os.path.basename(filepath)
    
    upload_file = drive.CreateFile({
        'title': file_name,
        'parents': [{'id': folderid}]
    })
    
    upload_file.SetContentFile(filepath)
    
    upload_file.Upload()
    
     # After uploading the file, call the /uploadFile endpoint
    response = requests.post('http://localhost:5500/uploadFile', json={'filename': file_name, 'folder_id': folderid})
    if response.status_code == 200:
        print("File uploaded and /uploadFile endpoint called successfully.")
    else:
        print(f"Error calling /uploadFile endpoint: {response.content}")
    
    return response

def getFileList(drive, folder_id):
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    return file_list

def DownloadMostRecentFile(download_path,folderid):
    gauth=authenticate()

    drive = GoogleDrive(gauth)
    
    file_list = getFileList(drive, folderid)
    
    if not file_list:
        print("No files found in the folder.")
        return ""
    
    file_list.sort(key=lambda x: x['createdDate'], reverse=True)
    
    most_recent_file = file_list[0]
    file_id = most_recent_file['id']
    file_name = most_recent_file['title']
    file_path = os.path.join(download_path, file_name)
    
    if os.path.exists(file_path):
        print(f"File already exists: {file_path}")
        return ""
    
    download_file = drive.CreateFile({'id': file_id})
    
    download_file.GetContentFile(file_path)

    return file_path