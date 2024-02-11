# IPTV Category Parser

## Introduction

IPTV Category Parser is a Python script designed to parse and filter M3U playlists based on specified categories. It allows for easy management of IPTV channels by categorizing them into user-defined groups. This tool is especially useful for organizing large M3U files into smaller, more manageable playlists.

## Features

- Download M3U files from provided URLs.
- Search for specific categories within M3U files.
- Generate filtered M3U playlists based on user-defined categories.
- Support for both local and remote M3U files.

## Usage

### Downloading and Parsing M3U Files

To download and parse an M3U file:

```
python IPTV-Category-Parser.py parse -u <URL> -o <output_file> -s config.ini
```

### Searching for Categories

To search for categories within an M3U file:

```
python IPTV-Category-Parser.py search-categories -i <input_file> -k <keywords>
```

## Configuring

To configure your categories, you have two options:

1. **Manually Modify the `config.ini` File:**

   - Use `config.example.ini` as a template to create your `config.ini`.
   - Modify the `config.ini` file to define your categories according to your preferences.
2. **Automatically Generate `config.ini` Using the `search-categories` Function:**

   - You can automatically generate the `config.ini` file by using the `search-categories` command with your specified keywords. This function searches the provided M3U file for categories matching the keywords and then generates a `config.ini` file with those categories.
   - Example command to search for categories and generate `config.ini`:

     ```
     python IPTV-Category-Parser.py search-categories -u <URL> -k <keyword1> <keyword2>
     ```

     Replace `<URL>` with the M3U file URL or use `-i <input_file>` for a local file, and replace `<keyword1> <keyword2>` with your search keywords. This command will create or update the `config.ini` file with the found categories.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
