import plistlib
import os
import sys
import json
from PIL import Image
import base64
import io

def extract_image(image_data, output_dir, filename):
    try:
        image = Image.open(io.BytesIO(image_data))
        filename, _ = os.path.splitext(filename)
        output_file = os.path.join(output_dir, f'{filename}.{image.format.lower()}')
        image.save(output_file)
        print(f'Saved image: {output_file}')
    except Exception as e:
        print(f'Error extracting image for key {filename}: {e}')

def extract_images_recursive(data, output_dir, key_prefix=''):
    if isinstance(data, dict):
        if 'profileName' in data:
            # save the author name in Credits.txt
            with open(os.path.join(output_dir, 'Credits.txt'), 'w') as f:
                f.write('Please ask for permission and credit original author:\n')
                f.write(data['profileName'])
                if data.get('twitterHandle'):
                    f.write(f'\nTwitter: {data.get('twitterHandle')}')
                if data.get('tiktokHandle'):
                    f.write(f'\nTiktok: {data.get('tiktokHandle')}')

        if data.get('imageData', None) and data.get('filename', ''):
            extract_image(base64.b64decode(data['imageData']), output_dir, data['filename'])
        else:
            for key, value in data.items():
                new_key_prefix = f'{key_prefix}{key}_'
                extract_images_recursive(value, output_dir, new_key_prefix)
    elif isinstance(data, bytes):
        try:
            # Check if the data starts with a valid JSON byte sequence or image data
            if data.startswith(b'{') or data.startswith(b'['):
                json_data = json.loads(data.decode('utf-8'))
                for key, value in json_data.items():
                    extract_images_recursive(value, output_dir, key_prefix + key + '_')
            else:
                # Handle as image data directly if it's not JSON
                extract_image(data, output_dir, key_prefix)
        except Exception as e:
            print(f'Error extracting image for key {key_prefix}: {e}')
    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_key_prefix = f'{key_prefix}{index}_'
            extract_images_recursive(item, output_dir, new_key_prefix)

def extract_images_from_bplist(bplist_file, output_dir):
    # Load the binary plist file
    with open(bplist_file, 'rb') as f:
        plist_data = plistlib.load(f)

    # Check if the plist data is a dictionary
    if not isinstance(plist_data, dict):
        print('Invalid plist format.')
        return

    # Extract images
    extract_images_recursive(plist_data, output_dir)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python extract_images.py <bplist_file> [<output_directory>]')
        sys.exit(1)

    bplist_file = sys.argv[1]
    if len(sys.argv) == 3:
        output_directory = sys.argv[2]
    elif len(sys.argv) == 2:
        # Create output directory using the base name of the bplist file
        base_name = os.path.splitext(os.path.basename(bplist_file))[0]
        output_directory = os.path.join(os.path.dirname(bplist_file), base_name)
        os.makedirs(output_directory, exist_ok=True)
        print(f'Output directory created: {output_directory}')

    extract_images_from_bplist(bplist_file, output_directory)
