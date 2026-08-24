import dropbox
import os
import requests
import sys

# Function to refresh the access token
def refresh_access_token(refresh_token, client_id, client_secret):
    """Refreshes the Dropbox access token using the refresh token."""
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        # Provide more detailed error message for debugging
        error_msg = f"Failed to refresh access token: Status Code {response.status_code}, Response: {response.text}"
        print(f"❌ {error_msg}", file=sys.stderr) # Print to stderr for GitHub Actions error visibility
        raise Exception(error_msg)

# Function to upload a file to Dropbox
def upload_file_to_dropbox(local_file_path, dropbox_destination_path, refresh_token, client_id, client_secret):
    """Uploads a local file to a specified full path on Dropbox, including subfolders.
    
    Args:
        local_file_path (str): The full path to the local file on the runner.
        dropbox_destination_path (str): The full desired path on Dropbox (e.g., "/my_folder/sub_folder/file.txt").
        refresh_token (str): Dropbox refresh token.
        client_id (str): Dropbox app key.
        client_secret (str): Dropbox app secret.
    
    Returns:
        bool: True if upload was successful, False otherwise.
    """
    try:
        access_token = refresh_access_token(refresh_token, client_id, client_secret)
        dbx = dropbox.Dropbox(access_token)

        # Open the local file in binary read mode
        with open(local_file_path, "rb") as f:
            # Upload the file, overwriting if it already exists (mode=dropbox.files.WriteMode.overwrite)
            # The files_upload method will automatically create necessary parent folders on Dropbox.
            dbx.files_upload(f.read(), dropbox_destination_path, mode=dropbox.files.WriteMode.overwrite)
        print(f"✅ Successfully uploaded file to Dropbox: {dropbox_destination_path}")
        return True # Indicate success
    except Exception as e:
        print(f"❌ Failed to upload file '{local_file_path}' to Dropbox at '{dropbox_destination_path}': {e}", file=sys.stderr)
        return False # Indicate failure

# Entry point for the script when executed directly
if __name__ == "__main__":
    # The script expects 5 command-line arguments:
    # 1. local_file_path (absolute path to the file to upload from the runner)
    # 2. dropbox_destination_path (the FULL destination path in Dropbox, e.g., "/my_base_folder/subfolder/filename.ext")
    # 3. refresh_token
    # 4. client_id (APP_KEY)
    # 5. client_secret (APP_SECRET)
    if len(sys.argv) != 6:
        print("Usage: python src/upload_to_dropbox.py <local_file_path> <dropbox_destination_path> <refresh_token> <client_id> <client_secret>", file=sys.stderr)
        sys.exit(1) # Exit with an error code for incorrect usage

    # Parse command-line arguments
    local_file_to_upload = sys.argv[1]
    dropbox_destination_path = sys.argv[2]
    refresh_token = sys.argv[3]
    client_id = sys.argv[4]
    client_secret = sys.argv[5]

    # Verify that the local file exists before attempting to upload
    if not os.path.exists(local_file_to_upload):
        print(f"❌ Error: The local file '{local_file_to_upload}' was not found. Please ensure it was generated correctly by previous steps.", file=sys.stderr)
        sys.exit(1) # Exit with an error code if the file is not found

    # Call the upload function
    if not upload_file_to_dropbox(local_file_to_upload, dropbox_destination_path, refresh_token, client_id, client_secret):
        sys.exit(1) # Exit with an error code if the upload itself fails


