"""
This script is intended to automate syncinc files to neocities.org.
"""
# Imports
import requests
from getpass import getpass
from lxml import html
import sys
import os

# Save url for use later. Global var
signin_url = r"https://neocities.org/signin"

# Set username
un = input("Please input username:\t")
pw = getpass("\nPlease input password")

# Save URL for upload path
up_url = r"https://neocities.org/api/upload"

# Convert input to a proper filepath
if len(sys.argv) > 1:
    path = os.path.realpath(sys.argv[1])
else:
    path = ""


def read_folder(path: str) -> list:
    """
    This will read all files in a folder and create a dictionary
    that can be used to upload all files.

    Params:
        path str: folder name to upload

    Returns:
        dictionary of {filename: (filename, opened_file, filetype)}
    """

    # Process path to usable format
    if path == "":
        path = os.path.abspath(os.getcwd())
    elif path[0] == "~":
        path = os.path.expanduser(path)

    if not os.path.isdir(path):
        raise ValueError("Folder provided is not a real path")
    else:
        lis = os.listdir(path)
        lis = [os.path.join(path, x) for x in lis]

    # Make dictionary of files
    files = {
        f.split("/")[-1]: (
            f.split("/")[-1],
            open(f, 'rb'),
            'text/html'
        )
        for f in lis
    }

    return files


def login(un, pw) -> (requests.sessions.Session, requests.models.Response):
    """
    This function will start a requests.Session object,
    connect to the website and return a session and
    request object.

    Params:
        un: username of login
        pw: password of login
    """

    # Start session
    s = requests.Session()
    # Pull signin page
    res = s.get(signin_url)

    # Check if pull succeeded and convert for XPATH use
    if res.status_code == 200:
        x = html.fromstring(res.content)
    # May put error handling here for down internet

    # Pull csrf_token
    csrf = x.xpath("//input[@name='csrf_token']/@value")[0]

    # Compile authentication
    auth = {
        "username": un,
        "password": pw,
        "csrf_token": csrf
    }

    # Send signin request
    res = s.post(signin_url, data=auth)

    # Verify login worked:
    if r"<title>Neocities - Sign In</title>" in res.text:
        print("Login failed")
    else:
        print("Login Success")

    return (s, res)


def uploadFiles(s: requests.sessions.Session):
    """
    Take the files we read in and push them to Neocities

    Params:
        s: Session object that holds cookies for login
        validation

    Returns:
        None
    """
    # Pull page for csrf value
    req = s.get("https://www.neocities.org/dashboard")
    x = html.fromstring(req.content)
    csrf = x.xpath(
                "//form[@id='uploadFilesButtonForm']/\
                    input[@name='csrf_token']/@value"
    )[0]
    csrf_str = str(csrf)

    # Push all values to NeoCities
    output = s.post(
        up_url,
        files=read_folder(path),
        data={'csrf_token': csrf_str}
    )

    # Check if file upload was successful
    if output.status_code == 200:
        print("File upload success")
    else:
        print("Upload failed:\t", output.status_code)
        print(output.text)


if __name__ == "__main__":
    s, r = login(un, pw)
    uploadFiles(s)
