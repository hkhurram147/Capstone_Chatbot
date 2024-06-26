from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import requests

def authenticate():
    gauth = GoogleAuth()

    gauth.LoadClientConfigFile("Cloud/client_secrets.json")
    gauth.LoadCredentialsFile("Cloud/credentials.json")
    if gauth.credentials is None:
        print("lmao")
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        print(gauth)
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("Cloud/credentials.json")
    return gauth

def upload(filepath):
    gauth=authenticate()

    drive = GoogleDrive(gauth)
    
    file_name = os.path.basename(filepath)
    
    upload_file = drive.CreateFile({
        'title': file_name,
        'parents': [{'id': '1z4PjHNG4bxYG6NUb5tdZvqcTRx5WksAo'}]
    })
    
    upload_file.SetContentFile(filepath)
    
    upload_file.Upload()
    
     # After uploading the file, call the /uploadFile endpoint
    response = requests.post('http://localhost:5500/uploadFile', json={'filename': file_name})
    if response.status_code == 200:
        print("File uploaded and /uploadFile endpoint called successfully.")
    else:
        print(f"Error calling /uploadFile endpoint: {response.content}")
    
    return response

def getFileList(drive, folder_id):
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    return file_list

def DownloadMostRecentFile(download_path):
    gauth=authenticate()

    drive = GoogleDrive(gauth)
    
    file_list = getFileList(drive, '1z4PjHNG4bxYG6NUb5tdZvqcTRx5WksAo')
    
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