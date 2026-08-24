import dropbox
import os
import requests
import sys

# Function to refresh the access token
def refresh_access_token(refresh_token, client_id, client_secret):
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
        # Log the error response from Dropbox API
        print(f"Failed to refresh access token. Status: {response.status_code}, Response: {response.text}", file=sys.stderr)
        raise Exception("Failed to refresh access token")

# Function to delete a file or folder from Dropbox (recursive for folders)
def delete_from_dropbox(dbx, path, log_file):
    try:
        # Use files_delete_v2 for files and folders.
        # For folders, it will delete recursively.
        dbx.files_delete_v2(path)
        log_file.write(f"Deleted from Dropbox: {path}\n")
        print(f"Deleted from Dropbox: {path}")
    except Exception as e:
        log_file.write(f"Failed to delete {path}, error: {e}\n")
        print(f"Failed to delete {path}, error: {e}")
        # Do not exit here, allow other operations to proceed

# Function to download files and folders recursively from a specified Dropbox folder
def download_files_from_dropbox(dropbox_folder, local_folder, refresh_token, client_id, client_secret, log_file_path):
    access_token = refresh_access_token(refresh_token, client_id, client_secret)
    dbx = dropbox.Dropbox(access_token)

    # Use a set to keep track of successfully downloaded items for the final success check
    downloaded_items = set()

    with open(log_file_path, "a") as log_file:
        log_file.write(f"Starting download process for Dropbox folder: {dropbox_folder} to local: {local_folder}\n")
        print(f"Starting download process for Dropbox folder: {dropbox_folder} to local: {local_folder}")

        try:
            os.makedirs(local_folder, exist_ok=True)

            # --- Key change: Use recursive=True in files_list_folder ---
            # This will list all files and folders within the specified path and its subfolders.
            # Handle pagination
            has_more = True
            cursor = None
            while has_more:
                if cursor:
                    result = dbx.files_list_folder_continue(cursor)
                else:
                    # List all entries recursively within the main Dropbox folder
                    result = dbx.files_list_folder(dropbox_folder, recursive=True)
                
                log_file.write(f"Listing files in Dropbox folder: {dropbox_folder} (recursive: True)\n")
                print(f"Listing files in Dropbox folder: {dropbox_folder} (recursive: True)")

                for entry in result.entries:
                    # Construct the relative path from the base Dropbox folder.
                    # entry.path_lower gives the full lowercase path, e.g., "/simulators/vtk_output/file.pvd"
                    # We need the path relative to the initial dropbox_folder, e.g., "vtk_output/file.pvd"
                    # Using os.path.relpath ensures correct path construction across OS.
                    # dropbox_folder.lower() is used for comparison as entry.path_lower is always lowercase.
                    relative_path = os.path.relpath(entry.path_lower, dropbox_folder.lower())

                    if isinstance(entry, dropbox.files.FileMetadata):
                        local_target_path = os.path.join(local_folder, relative_path)
                        local_target_dir = os.path.dirname(local_target_path)
                        os.makedirs(local_target_dir, exist_ok=True) # Ensure local subdirectories exist for the file

                        try:
                            with open(local_target_path, "wb") as f:
                                metadata, res = dbx.files_download(path=entry.path_lower)
                                f.write(res.content)
                            log_file.write(f"Downloaded {entry.path_lower} to {local_target_path}\n")
                            print(f"Downloaded: {entry.path_lower} -> {local_target_path}")
                            downloaded_items.add(local_target_path) # Add to set of downloaded items
                        except Exception as e:
                            log_file.write(f"Failed to download file {entry.path_lower}, error: {e}\n")
                            print(f"Failed to download file {entry.path_lower}, error: {e}", file=sys.stderr)
                            # Do not exit, try to download other files

                    elif isinstance(entry, dropbox.files.FolderMetadata):
                        local_target_dir = os.path.join(local_folder, relative_path)
                        os.makedirs(local_target_dir, exist_ok=True) # Create local subfolder
                        log_file.write(f"Created local directory: {local_target_dir}\n")
                        print(f"Created local directory: {local_target_dir}")
                        # Folders themselves aren't 'downloaded' in the same way as files,
                        # but their creation signifies progress.

                    # If you re-enable deletion, consider if you want to delete files or folders
                    # as they are downloaded/processed, or after all downloads are complete.
                    # For now, deletion is commented out as in your original script.
                    # delete_from_dropbox(dbx, entry.path_lower, log_file)

                has_more = result.has_more
                cursor = result.cursor

            log_file.write("Download process completed.\n")
            print("Download process completed.")
            
            # Indicate success based on whether any files were actually downloaded.
            # This helps to catch cases where the Dropbox folder might be empty or permissions prevent listing.
            if not downloaded_items:
                print("WARNING: No files were found or downloaded from the specified Dropbox folder.", file=sys.stderr)
                return False # Indicate failure if no files were downloaded
            return True

        except dropbox.exceptions.ApiError as err:
            log_file.write(f"Dropbox API error during download: {err}\n")
            print(f"Dropbox API error during download: {err}", file=sys.stderr)
            return False
        except Exception as e:
            log_file.write(f"Unexpected error during download: {e}\n")
            print(f"Unexpected error during download: {e}", file=sys.stderr)
            return False

# Entry point for the script
if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: python3 download_dropbox_files.py <dropbox_folder_path> <local_target_folder> <refresh_token> <app_key> <app_secret> <log_file_path>", file=sys.stderr)
        sys.exit(1)

    dropbox_folder = sys.argv[1] # Dropbox folder path
    local_folder = sys.argv[2]   # Local folder path
    refresh_token = sys.argv[3]  # Dropbox refresh token
    client_id = sys.argv[4]      # Dropbox client ID
    client_secret = sys.argv[5]  # Dropbox client secret
    log_file_path = sys.argv[6]  # Path to the log file

    # Call the function and exit with appropriate status code
    if not download_files_from_dropbox(dropbox_folder, local_folder, refresh_token, client_id, client_secret, log_file_path):
        sys.exit(1) # Exit with error code if download failed


