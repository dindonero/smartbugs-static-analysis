from os import walk

import requests
import argparse

url = "http://perseus.inesc-id.pt:8000/"


def setup_parser():
    parser = argparse.ArgumentParser(description='Upload Files to SmartBugs SASP Server.')
    parser.add_argument('--token', type=str, required=True, help="User's GitHub Token")
    group_tools = parser.add_mutually_exclusive_group(required='True')
    group_tools.add_argument('-t', '-tool', nargs='+', help='Select tool(s)')
    return parser.parse_args()


def find_solidity_files_in_repo():
    solidity_files = []
    for root, dirs, files in walk('./'):
        for file in files:
            if file.endswith('.sol'):
                solidity_files.append(root + '/' + file)
    return solidity_files


def create_body(user_hash, tools):
    return {
        'user-hash': user_hash,
        'tools': tools
    }


def upload_files_to_smartbugs(filenames, body):
    files_dict = {}
    for name in filenames:
        f = open(name, 'rb')
        files_dict[name] = f

    response = requests.post(url=url, data=body, files=files_dict)

    # Close files
    for file in files_dict.values():
        file.close()
    return response


if __name__ == "__main__":
    args = setup_parser()
    
    # Searches repo for all solidity files
    filenames = find_solidity_files_in_repo()

    # Create Body Data
    body = create_body(user_hash=args.token, tools=args.tool)

    # Upload Files to Smartbugs
    sarif_results = upload_files_to_smartbugs(filenames=filenames, body=body)

    # Save SARIF file on user repo
    with open('results.sarif', 'w') as sarif_file:
        sarif_file.write(sarif_results.text)
