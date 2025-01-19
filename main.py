import plistlib
import os
import sys
import json
import base64

def dump_file(raw_data, output_dir, filename):
    try:
        # Check the first few bytes to determine the file type
        if raw_data.startswith(b'\x00\x01\x00\x00'):
            if not filename.endswith('.ttf'):
                filename += '.ttf'
        elif raw_data.startswith(b'\x89PNG'):
            if not filename.endswith('.png'):
                filename += '.png'
        elif raw_data.startswith(b'\xff\xd8'):
            if not filename.endswith('.jpg'):
                filename += '.jpg'
        elif raw_data.startswith(b'\x00\x00\x00\x18'):
            if not filename.endswith('.mp4'):
                filename += '.mp4'
        elif raw_data.startswith(b'\x66\x74\x79\x70'):
            if not filename.endswith('.mov'):
                filename += '.mov'                
        else:
            print(f'Unknown file type for {filename}')

        with open(os.path.join(output_dir, filename), 'wb') as f:
            f.write(raw_data)
        print(f'Saved file: {os.path.join(output_dir, filename)}')
    except Exception as e:
        print(f'Error extracting file {filename}: {e}')

def extract_files_recursive(data, output_dir, key_prefix=''):
    if isinstance(data, dict):
        if data.get('profileName'):
            # save the author name in Credits.txt
            with open(os.path.join(output_dir, 'Credits.txt'), 'w') as f:
                f.write(f'Please ask for permission and credit original author:\n{data.get('profileName')}')
                if data.get('twitterHandle'):
                    f.write(f'\nTwitter: @{data.get('twitterHandle')}')
                if data.get('tiktokHandle'):
                    f.write(f'\nTiktok: @{data.get('tiktokHandle')}')

        if data.get('imageData', None):
            filename = data.get('filename') if data.get('filename') else key_prefix
            dump_file(base64.b64decode(data['imageData']), output_dir, filename)
        else:
            for key, value in data.items():
                new_key_prefix = f'{key_prefix}{key}_'
                extract_files_recursive(value, output_dir, new_key_prefix)
    elif isinstance(data, bytes):
        try:
            # Check if the data starts with a valid JSON byte sequence or image data
            if data.startswith(b'{') or data.startswith(b'['):
                json_data = json.loads(data.decode('utf-8'))
                for key, value in json_data.items():
                    extract_files_recursive(value, output_dir, key_prefix + key + '_')
            else:
                # Handle as raw data directly if it's not JSON
                dump_file(data, output_dir, key_prefix)
        except Exception as e:
            print(f'Error extracting image for key {key_prefix}: {e}')
    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_key_prefix = f'{key_prefix}{index}_'
            extract_files_recursive(item, output_dir, new_key_prefix)

def extract_images_from_bplist(bplist_file, output_dir):
    # Load the binary plist file
    with open(bplist_file, 'rb') as f:
        plist_data = plistlib.load(f)

    # Check if the plist data is a dictionary
    if not isinstance(plist_data, dict):
        print('Invalid plist format.')
    else:
        extract_files_recursive(plist_data, output_dir)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python main.py <bplist_file> [<output_directory>]')
        sys.exit(1)

    bplist_file = sys.argv[1]
    if len(sys.argv) == 3:
        output_directory = sys.argv[2]
    elif len(sys.argv) == 2:
        # Name output directory using the base name of the bplist file
        base_name = os.path.splitext(os.path.basename(bplist_file))[0]
        output_directory = os.path.join(os.path.dirname(bplist_file), base_name)
    os.makedirs(output_directory, exist_ok=True)
    print(f'Output directory created: {output_directory}')

    extract_images_from_bplist(bplist_file, output_directory)
