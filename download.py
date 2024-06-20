from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

data_folder_id='1z4PjHNG4bxYG6NUb5tdZvqcTRx5WksAo'
zip_folder_id='1kAdxN5oOv3jTYoSD6JN97sstCLJVU8w2'

gauth = GoogleAuth()

# Load client secrets
gauth.LoadClientConfigFile("client_secrets.json")

gauth.LoadCredentialsFile("credentials.json")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()

# Save the current credentials to a file
gauth.SaveCredentialsFile("credentials.json")
# Create a GoogleDrive instance with authenticated GoogleAuth instance
drive = GoogleDrive(gauth)

def list_files_in_folder(drive, folder_id):
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    return file_list

def download_most_recent_file(drive, folder_id, download_path):
    # List all files in the specified folder
    file_list = list_files_in_folder(drive, folder_id)

    if not file_list:
        print("No files found in the folder.")
        return 0
    
    # Sort the file list by creation date
    file_list.sort(key=lambda x: x['createdDate'], reverse=True)
    
    # Get the most recent file
    most_recent_file = file_list[0]
    file_id = most_recent_file['id']
    file_name = most_recent_file['title']
    file_path = os.path.join(download_path, file_name)
    
    # Check if the file already exists in the download path
    if os.path.exists(file_path):
        print(f"File already exists: {file_path}")
        return 0
    
    # Create a GoogleDriveFile instance with the specified file ID
    download_file = drive.CreateFile({'id': file_id})
    
    # Download the file to the specified path
    download_file.GetContentFile(file_path)
    print(f"Downloaded file: {file_path}")
    return 1

def download_all_files(drive, folder_id, download_path):
    # List all files in the specified folder
    file_list = list_files_in_folder(drive, folder_id)
    
    if not file_list:
        print("No files found in the folder.")
        return 0
    
    # Download each file in the folder
    for file in file_list:
        file_id = file['id']
        file_name = file['title']
        file_path = os.path.join(download_path, file_name)
        
        # Check if the file already exists in the download path
        if os.path.exists(file_path):
            print(f"File already exists: {file_path}")
            continue
        
        # Create a GoogleDriveFile instance with the specified file ID
        download_file = drive.CreateFile({'id': file_id})
        
        # Download the file to the specified path
        download_file.GetContentFile(file_path)
        print(f"Downloaded file: {file_path}")
    return 1

# Example usage:
# Upload a file

# Download the most recently uploaded file from a specific folder
folder_id = data_folder_id  # Replace this with your folder ID
download_path = r'C:\Users\vidha\OneDrive\Documents\phoenixAI\downloadLoc'
k=download_most_recent_file(drive, folder_id, download_path)
if k==0:
    print("File already downloaded")
download_all=r'C:\Users\vidha\OneDrive\Documents\phoenixAI\dowloadone'
# Download all files from a specific folder
n=download_all_files(drive, folder_id, download_all)
if n==0:
    print("Files already downloaded")