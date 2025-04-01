import os
import shutil
import pypinyin
import time

LOG_FILE = "video_log.log"  # 定义日志文件名

def log_to_file(log_message):
    """Log messages to a log file."""
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"{log_message}\n")
    time.sleep(1)  # 延迟以匹配文件系统性能限制

def get_initial_char(name):
    """Get the initial character for categorization."""
    time.sleep(1)  # 延迟以匹配文件系统性能限制
    if name[0].isdigit():
        return "0-9"
    else:
        pinyin = pypinyin.pinyin(name[0], style=pypinyin.Style.FIRST_LETTER)
        if pinyin and pinyin[0][0].isalpha():
            return pinyin[0][0].upper()
        else:
            return None

def create_initial_folders(root_dir):
    """Pre-create 0-9 and A-Z folders in the root directory, if they are missing."""
    folders = ['0-9'] + [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    for folder in folders:
        folder_path = os.path.join(root_dir, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created missing folder: '{folder_path}'")
        time.sleep(1)  # 延迟以匹配文件系统性能限制

def move_movie(src, dst):
    """For movies, remove existing target and then move the entire movie directory."""
    if os.path.exists(dst):
        shutil.rmtree(dst)
        print(f"Deleted existing movie directory '{dst}'")
    shutil.move(src, dst)
    print(f"Moved movie '{src}' to '{dst}'")
    time.sleep(1)  # 延迟以匹配文件系统性能限制

def move_tv_series(src, dst):
    """For TV series, handle by season level."""
    if not os.path.exists(dst):
        shutil.move(src, dst)
        print(f"Moved TV series '{src}' to '{dst}'")
        time.sleep(1)  # 延迟以匹配文件系统性能限制
    else:
        for season in os.listdir(src):
            src_season_path = os.path.join(src, season)
            dst_season_path = os.path.join(dst, season)

            if os.path.isdir(src_season_path):
                if os.path.exists(dst_season_path):
                    shutil.rmtree(dst_season_path)
                    print(f"Deleted existing season directory '{dst_season_path}'")
                shutil.move(src_season_path, dst_season_path)
                print(f"Moved season '{src_season_path}' to '{dst_season_path}'")
                time.sleep(1)  # 延迟以匹配文件系统性能限制

def move_and_rename(source_root, target_root, content_type, organize_by_initial):
    """Move and rename based on content type (movie or tv_series) and organization choice."""
    if organize_by_initial:
        create_initial_folders(target_root)

    for item in os.listdir(source_root):
        item_path = os.path.join(source_root, item)
        time.sleep(1)  # 延迟以匹配文件系统性能限制

        if organize_by_initial:
            initial_char = get_initial_char(item)
            if initial_char:
                dest_dir = os.path.join(target_root, initial_char)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                    print(f"Created missing folder: '{dest_dir}'")
                    time.sleep(1)  # 延迟以匹配文件系统性能限制
                target_path = os.path.join(dest_dir, item)
        else:
            target_path = os.path.join(target_root, item)

        try:
            if os.path.isdir(item_path) and "tmdb" not in item.lower():
                log_to_file(f"Directory without 'tmdb': {item_path}")

            if content_type == "movie":
                move_movie(item_path, target_path)
            elif content_type == "tv_series":
                move_tv_series(item_path, target_path)

        except Exception as e:
            print(f"Failed to move '{item}': {e}")
            time.sleep(1)  # 延迟以匹配文件系统性能限制

if __name__ == "__main__":
    source_directory = input("Enter the source root directory path: ").strip()
    if not os.path.isdir(source_directory):
        print(f"'{source_directory}' is not a valid directory. Exiting...")
        exit(1)

    target_directory = input("Enter the target root directory path: ").strip()
    if not os.path.isdir(target_directory):
        print(f"'{target_directory}' is not a valid directory. Exiting...")
        exit(1)

    content_type = input("Enter content type (movie or tv_series): ").strip().lower()
    if content_type not in ["movie", "tv_series"]:
        print("Invalid content type. Please enter 'movie' or 'tv_series'. Exiting...")
        exit(1)

    organize_by_initial = input("Organize by initial character? (yes or no): ").strip().lower() == "yes"
    
    move_and_rename(source_directory, target_directory, content_type, organize_by_initial)
    print("\nOperations completed.")
