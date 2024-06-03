import os
import re
from tmdbv3api import TMDb, Movie

# Initialize TMDb
tmdb = TMDb()
tmdb.api_key = 'YOUR_API_KEY'
tmdb.language = 'en'

movie_api = Movie()

# Directory containing movies
source_dir = '/YOUR_ABSOLUTE/FOLDER/'

# Define common video file extensions
video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg')

# Pattern to detect a year in the movie title
year_pattern = re.compile(r'\b(19[0-9]{2}|20[0-9]{2})\b')

# List of common tags and patterns to exclude from filenames
exclusion_patterns = [
    r'\b(?:1080p|1080|720p|720|x264|YTS\.AM|DVDRip|BRRip|BluRay|WEB-DL|WEBRip|HDRip|HDTV|FullHD|x265|YIFY|EVO|RARBG|Ita|Spa|Eng|Korean|AC3|5\.1|BDrip|DDL|realDMDJ|Multisub|H264|H265|m720p|Dual|AV1|HD|\[AV1\]|HEVC|10bit|edition|Spanish|English|OPUS|Audio|Spanishsub|Enlighsub|by|M1080p|microhd|\.net|m1080|VOSE|dvd|vhsrip|ve|subs|castellano|rip|cast|latino|mkv|uhd|2160p|h|264|IMAX|10b|mck|elitetorrent|net|open\smatte|panoramico|Director\ss\sCut|remastered|versión\sextendida|cvcd|blurayrip|sub|web\sdl|Open\sMatte|byp58|Lat|Jap)\b',
    r'\b(?:uhd|2160p|h\.?264|IMAX|10b(?:it)?|mck|elitetorrent|\.net|open\smatte|panoramico|Director\ss\sCut|remastered|cvcd|blurayrip|sub|web\sdl|Open\sMatte|byp58|BD1080p)\b',
    r'\b(?:XviD|AAC|BD|Multi|4K)\b',
    r'\b(?:Geot|KaNyO|hispashare\.com|Sav1or|Phenom|mokesky|JJ|djk|rubesp|YTS|Trial|dav1nci|Johnny|iDN|CreW|Will1869|RemY)\b',
    r'\b(?:Extended|Director\'s\sCut|Unrated|Special\sEdition|Remastered|Theatrical\sRelease|Ultimate\sEdition|V\sE|Versión|Extendida)\b',
    r'\b(?:WEB-DL|WEBRip|DTS|WEB\sDL|DDP5|GalaxyRG265|EAC3|WQHD|HDTS|CxN|ESub)\b',
    r'\b(?:Englishsub|Spanishsub|DualAudio|MultiSub|4Ka1080p|HDR|4k2160p|4Krip2160|HLG|BDR1080|maxitorrent|com|web|dl|Matte|Non|BD1080)\b',
    r'\b(?:S\d{2}E\d{2})\b',
]

# Compile the exclusion patterns into a single regular expression
exclusion_regex = re.compile('|'.join(exclusion_patterns), re.IGNORECASE | re.UNICODE)

def clean_title(title):
    print(f"Cleaning title: {title}")
    # Extract year from title, if present
    year_match = year_pattern.search(title)
    year = year_match.group() if year_match else ''

    # Split the title into parts and filter out excluded patterns
    #parts = re.split(r'[\W_]+', title)
    # Remove year with parentheses from title
    title = re.sub(r'\(\d{4}\)', '', title)
    parts = re.split(' ', title)
    cleaned = [part for part in parts if not year_pattern.match(part) and not exclusion_regex.search(part)]

    return ' '.join(cleaned), year

for filename in os.listdir(source_dir):
    if not filename.lower().endswith(video_extensions):
        continue
    # Do not enter directories
    if os.path.isdir(os.path.join(source_dir, filename)):
        continue
    clean_filename = os.path.splitext(filename)[0]
    movie_title, movie_year = clean_title(clean_filename)
    print(f"Title: {movie_title}, Year: {movie_year}")

    if not movie_title:
        print(f"Could not extract a valid title from: {filename}")
        continue

    search_results = movie_api.search(movie_title)
    if not search_results or search_results.total_results == 0:
        print(f"No results found for: {movie_title}")
        continue

    # Filter the search results to only include movies with the same year as the filename    
    if len(search_results) > 1:
        if movie_year:
            search_results = [result for result in search_results if hasattr(result, 'release_date') and result.release_date and int(movie_year) - 1 <= int(result.release_date[:4]) <= int(movie_year) + 1]

        if len(search_results) == 1:
            selected_movie = search_results[0]
        else:
            print(f"Multiple results found for: {movie_title}")
            for i, result in enumerate(search_results):
                print(f"{i + 1}: {result.title} ({result.release_date[:4] if hasattr(result, 'release_date') and result.release_date else 'Unknown Year'})")
            
            selection = input("Please select the correct movie by number (or type 'skip' to skip): ")
            if selection.lower() == 'skip':
                continue
            try:
                selected_index = int(selection) - 1
                selected_movie = search_results[selected_index]
            except (ValueError, IndexError):
                print("Invalid selection, skipping.")
                continue
    else:
        selected_movie = search_results[0]

    print(f"Selected movie: {selected_movie.title} ({selected_movie.release_date[:4] if selected_movie.release_date else 'Unknown Year'})")
    
    movie_title_corrected = selected_movie.title
    movie_year = selected_movie.release_date[:4] if selected_movie.release_date else "Unknown Year"

    new_dir = os.path.join(source_dir, f"{movie_title_corrected} ({movie_year})")
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    
    old_file_path = os.path.join(source_dir, filename)
    new_file_path = os.path.join(new_dir, filename)

    os.rename(old_file_path, new_file_path)
    print(f"Moved: {old_file_path} -> {new_file_path}")
