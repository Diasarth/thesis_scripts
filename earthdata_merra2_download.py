import requests
import os
import time
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ask for Earthdata credentials
username = input('Earthdata username: ')
password = getpass('Earthdata password: ')

# Read URLs from file (get the file at https://disc.gsfc.nasa.gov/datasets?project=MERRA-2)
with open('subset_M2T3NVASM_5.12.4_20250804_180634_.txt', 'r') as f:
    urls = [line.strip() for line in f if line.strip()]

# Folder where files will be saved (same as the script)
output_folder = os.path.dirname(os.path.abspath(__file__))
MAX_RETRIES = 3

# Create a session with authentication
def create_session():
    s = requests.Session()
    s.auth = (username, password)
    s.headers.update({
        'User-Agent': 'python-script',
        'Accept': 'application/x-netcdf,application/octet-stream'
    })
    return s

# Function to download one file, with multiple retry attempts
def download_file(url):
    session = create_session()

    # Extract filename
    filename = url.split('LABEL=')[-1].split('&')[0] if 'LABEL=' in url else url.split('/')[-1]
    filepath = os.path.join(output_folder, filename)

    # Skip if file already exists
    if os.path.exists(filepath):
        return f'🟡 Already exists: {filename}'

    # Try downloading up to MAX_RETRIES times
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f'⬇️  Starting: {filename} (attempt {attempt})')
            r = session.get(url, stream=True, allow_redirects=True)
            
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return f'✅ Completed: {filename}'
            elif r.status_code == 401:
                return f'❌ Error 401: Authentication failed for {filename}'
            else:
                print(f'⚠️ Error {r.status_code} while downloading {filename}')
        except Exception as e:
            print(f'❗ Exception in {filename}: {e}')

        # Wait before the next retry (unless it's the last attempt)
        if attempt < MAX_RETRIES:
            time.sleep(5)
        else:
            return f'❌ Failed after {MAX_RETRIES} attempts: {filename}'

# Number of simultaneous downloads
MAX_WORKERS = 10

# Execute parallel downloads
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(download_file, url) for url in urls]
    for future in as_completed(futures):
        print(future.result())