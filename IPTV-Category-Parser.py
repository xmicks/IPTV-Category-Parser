import requests
import argparse
import configparser
import re
import os
from tqdm import tqdm
import sys  # Used for writing error messages to stderr.

# Function to download an M3U file from a URL with a progress bar.
def download_m3u(url):
    try:
        print("Connecting to the server to initialize download...")
        response = requests.get(url, stream=True)  # Stream=True to download the content in chunks
        response.raise_for_status()  # Raises HTTPError for bad responses

        # Determine the total size for progress indication
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # Define block size for chunk download

        # Initialize tqdm progress bar
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

        temp_path = "downloaded_temp.m3u"  # Temporary file path
        with open(temp_path, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))  # Update progress bar
                file.write(data)  # Write chunk to file
        progress_bar.close()

        # Sanity check in case of discrepancy in content-length reported
        if total_size != 0 and progress_bar.n != total_size:
            print("ERROR, something went wrong")

        print(f"Downloaded M3U file from {url} to {temp_path}")
        return temp_path
    except requests.RequestException as e:
        sys.stderr.write(f"Error downloading the M3U file: {e}\n")
        sys.stderr.flush()
        return None

# Function to search for categories within an M3U file based on keywords.
def search_categories(input_or_url, keywords):
    input_file = input_or_url
    # If a URL is detected, download the file first
    if input_or_url.startswith('http://') or input_or_url.startswith('https://'):
        print("URL detected, downloading M3U file...")
        input_file = download_m3u(input_or_url)
        if not input_file:
            sys.stderr.write("Failed to download M3U file.\n")
            sys.stderr.flush()
            return
    
    categories = set()
    # Open and read the M3U file, searching for category matches
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('#EXTINF'):  # EXTINF lines contain stream info
                category = re.search('group-title="([^"]+)"', line)
                if category and any(keyword.lower() in category.group(1).lower() for keyword in keywords):
                    categories.add(category.group(1))

    # Save found categories to config.ini
    config = configparser.ConfigParser()
    config['Categories'] = {f'category{i}': category for i, category in enumerate(categories)}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    print(f"Found and saved {len(categories)} categories to config.ini")
    
    # Clean up downloaded file
    if input_file != input_or_url:
        os.remove(input_file)



# Function to parse an M3U file, optionally downloading it first, and filter by categories.
def parse_m3u(input_or_url, output_file, config_file):
    input_file = input_or_url
    
    if input_or_url.startswith('http://') or input_or_url.startswith('https://'):
        downloaded_file = download_m3u(input_or_url)
        if not downloaded_file:
            sys.stderr.write("Failed to download the M3U file.\n")
            sys.stderr.flush()
            return
        input_file = downloaded_file

    config = configparser.ConfigParser()
    config.read(config_file)
    categories = {config['Categories'][key] for key in config['Categories']}

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write('#EXTM3U\n')  # Ensure the M3U file starts with the EXTINF header
        copy_next_line = False
        for line in infile:
            if line.startswith('#EXTINF'):
                match = re.search('group-title="([^"]+)"', line)
                if match and match.group(1) in categories:
                    outfile.write(line)
                    copy_next_line = True  # Next line is the stream URL
            elif copy_next_line:
                outfile.write(line)  # Write the stream URL
                copy_next_line = False  # Reset for the next entry
    
    if input_file != input_or_url:
        os.remove(input_file)

    print(f"Filtered M3U file saved to {output_file}")

# Main CLI setup for the script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="M3U IPTV List Manipulator with Integrated Download and Parse Functionality")
    subparsers = parser.add_subparsers(dest='command')

    # Setup for search-categories command
    search_parser = subparsers.add_parser('search-categories')
    search_parser.add_argument('-i', '--input_m3u_file', help="Input M3U file path", default=None)
    search_parser.add_argument('-u', '--url', help="URL of the M3U file to download", default=None)
    search_parser.add_argument('-k', '--keywords', nargs='+', required=True, help="Keywords to search for categories")

    # Setup for parse command
    parse_parser = subparsers.add_parser('parse')
    parse_parser.add_argument('-i', '--input_m3u_file', help="Input M3U file path", default=None)
    parse_parser.add_argument('-u', '--url', help="URL of the M3U file to download", default=None)
    parse_parser.add_argument('-o', '--output_m3u_file', required=True, help="Output M3U file path")
    parse_parser.add_argument('-s', '--settings', required=True, help="Settings/config.ini file with categories")

    args = parser.parse_args()

    # Execute the appropriate function based on the command-line arguments
    if args.command == 'search-categories':
        search_categories(args.input_m3u_file or args.url, args.keywords)
    elif args.command == 'parse':
        parse_m3u(args.input_m3u_file or args.url, args.output_m3u_file, args.settings)
