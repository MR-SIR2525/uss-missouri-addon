import os
import json

def find_folders(base_dir, keywords):
    matched_folders = []
    for root, dirs, files in os.walk(base_dir):
        for d in dirs:
            for keyword in keywords:
                if keyword.lower() in d.lower():
                    matched_folders.append(os.path.join(root, d))
                    break
    return matched_folders

def find_manifest_files(folders):
    manifest_files = []
    for folder in folders:
        manifest_path = os.path.join(folder, 'manifest.json')
        if os.path.isfile(manifest_path):
            manifest_files.append(manifest_path)
    return manifest_files

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# check indentation if needed
def write_json_file(file_path, data):
    indentation = 4
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=indentation)

def check_versions(manifest_files):
    versions = []
    for file in manifest_files:
        data = read_json_file(file)
        version = tuple(data.get('header', {}).get('version', []))
        versions.append((file, version))
    return versions

def update_versions(manifest_files, new_version):
    new_version_list = [int(v) for v in new_version.split('.')]
    for file in manifest_files:
        data = read_json_file(file)
        if 'header' in data:
            data['header']['version'] = new_version_list
        if 'modules' in data:
            for module in data['modules']:
                module['version'] = new_version_list
        if 'dependencies' in data:
            for dependency in data['dependencies']:
                dependency['version'] = new_version_list
        write_json_file(file, data)

def update_name_with_version(manifest_files, new_version):
    for file in manifest_files:
        data = read_json_file(file)
        if 'header' in data:
            name = data['header'].get('name', '')
            if 'v' in name and any(char.isdigit() for char in name.split('v')[-1]):
                name = name.rsplit('v', 1)[0].strip()
            new_name = f"{name} v{new_version}"
            data['header']['name'] = new_name
            write_json_file(file, data)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    behavior_keywords = ["behavior", "behavior_pack", " BP"]
    resource_keywords = ["resources", "resource_pack", "resource pack", " RP"]

    behavior_folders = find_folders(base_dir, behavior_keywords)
    resource_folders = find_folders(base_dir, resource_keywords)

    all_folders = behavior_folders + resource_folders
    manifest_files = find_manifest_files(all_folders)

    if not manifest_files:
        print("No manifest.json files found.")
        return

    versions = check_versions(manifest_files)
    version_set = set(version for _, version in versions)

    if len(version_set) > 1:
        print("Different versions found:")
        for file, version in versions:
            print(f"{file}: {version}")
        choice = input("Do you want to set all to a new value? (yes/no): ").strip().lower()
        if choice == 'yes':
            new_version = input("Enter the new version (format: x.x.x): ").strip()
            update_versions(manifest_files, new_version)
            update_name_with_version(manifest_files, new_version)
            print("Versions and names updated.")
    else:
        print("All versions match.")
        new_version = '.'.join(map(str, version_set.pop()))
        choice = input(f"Do you want to update the pack name to include the version {new_version}? (yes/no): ").strip().lower()
        if choice == 'yes' or choice == 'y':
            update_name_with_version(manifest_files, new_version)
            print("Names updated.")
        else:
            print("Okay, no changes made.")

if __name__ == "__main__":
    main()
