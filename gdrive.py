from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

data_folder_id='1z4PjHNG4bxYG6NUb5tdZvqcTRx5WksAo'
zip_folder_id='1kAdxN5oOv3jTYoSD6JN97sstCLJVU8w2'

def UploadToGdrive(gauth,filepath):
    # Try to load saved client credentials
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
    

    # Create a new file in Google Drive
    upload_file = drive.CreateFile({'title': filepath})

    # Set the content of the file from the local file
    upload_file.SetContentFile(filepath)

    # Upload the file
    upload_file.Upload()
