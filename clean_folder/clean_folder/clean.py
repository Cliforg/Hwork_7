import re
import sys
import shutil
from pathlib import Path

UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

TRANS = {}

jpeg_files = []
png_files = []
jpg_files = []
avi_files = []
mp4_files = []
mov_files = []
doc_files = []
docx_files = []
txt_files = []
mp3_files = []
wav_files = []
folders = []
archives = []
others = []
unknown = set()
extensions = set()

registered_extentions = {
    'JPEG': jpeg_files,
    'PNG': png_files,
    'JPG': jpg_files,
    'AVI': avi_files,
    'MP4': mp4_files,
    'MOV': mov_files,
    'DOC': doc_files,
    'DOCX': docx_files,
    'TXT': txt_files,
    'MP3': mp3_files,
    'WAV': wav_files,
    'ZIP': archives
}


for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()

def normalize(name: str) -> str:
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', '_', new_name)
    return f"{new_name}.{'.'.join(extension)}"



def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()

def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('IMAGES', 'DOCUMENTS', 'AUDIO', 'VIDEO', 'ARCHIVE', 'OTHERS'):
                folders.append(item)
                scan(item)
            continue
        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            others.append(new_name)
        else:
            try:
                container = registered_extentions[extension]
                extensions.add(extension)
                container.append(new_name)
            except KeyError:
                unknown.add(extension)
                others.append(new_name)


def handle_file(path, root_folder, dist):
    target_folder = root_folder/dist
    target_folder.mkdir(exist_ok = True)
    path.replace(target_folder/normalize(path.name))

def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok = True)
    new_name = normalize(path.name.replace('.zip', ''))
    archive_folder = target_folder / new_name

    try:
        shutil.unpack_archive(str(path.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        return
    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass


def process_folder(folder_path):
    result = ""
    for file in folder_path.rglob('*'):
        if file.is_file():
            result += file.name + ', '
    return result

def main():
    folder_path = Path(sys.argv[1])
    scan(folder_path)


    for file in jpeg_files:
        handle_file(file, folder_path, 'IMAGES') 

    for file in png_files:
        handle_file(file, folder_path, 'IMAGES')                                

    for file in jpg_files:
        handle_file(file, folder_path, 'IMAGES') 

    for file in avi_files:
        handle_file(file, folder_path, 'VIDEO') 

    for file in mp4_files:
        handle_file(file, folder_path, 'VIDEO') 

    for file in mov_files:
        handle_file(file, folder_path, 'VIDEO')

    for file in doc_files:
        handle_file(file, folder_path, 'DOCUMENTS')

    for file in docx_files:
        handle_file(file, folder_path, 'DOCUMENTS')

    for file in txt_files:
        handle_file(file, folder_path, 'DOCUMENTS')

    for file in mp3_files:
        handle_file(file, folder_path, 'AUDIO')

    for file in wav_files:
        handle_file(file, folder_path, 'AUDIO')

    for file in others:
        handle_file(file, folder_path, 'OTHERS')

    for file in archives:
        handle_archive(file, folder_path, 'ARCHIVE') 

    images_result = process_folder(folder_path / 'IMAGES')
    video_result = process_folder(folder_path / 'VIDEO')
    documents_result = process_folder(folder_path / 'DOCUMENTS')
    audio_result = process_folder(folder_path / 'AUDIO')
    others_result = process_folder(folder_path / 'OTHERS')
    archive_result = process_folder(folder_path / 'ARCHIVE')

    remove_empty_folders(folder_path)

    print('List of files in categories: ')
    print("IMAGES:\n", images_result)
    print("VIDEO:\n", video_result)
    print("DOCUMENTS:\n", documents_result)
    print("AUDIO:\n", audio_result)
    print("ARCHIVE:\n", archive_result)    
    print("OTHERS:\n", others_result)

    print(f'All known extensions: {extensions}')
    print(f'All unknown extensions: {unknown}')                


if __name__ == '__main__':
    main()    