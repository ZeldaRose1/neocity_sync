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


class fileUploader:
    """
        Holds data for requests as well as methods to move files to
        neocities.

        This will read in a file in the main directory 'nc_ignore.txt'
        and avoid pushing anything listed in the file.
    """
    # URL for upload path
    up_url = r"https://neocities.org/api/upload"

    # Make set of allowed file types
    allowed_files = set([
        "html", "htm", "jpg", "png", "gif", "svg", "ico",
        "md", "markdown", "js", "json", "geojson", "css",
        "txt", "text", "csv", "tsv", "xml", "eot", "ttf",
        "woff", "woff2", "svg"
        ])

    # Convert input to a proper filepath
    if len(sys.argv) > 1:
        path = os.path.realpath(sys.argv[1])
    # elif path[0] == "~":
    #     path = os.path.expanduser(path)
    else:
        path = os.path.realpath(os.getcwd())

    # Set username
    if os.path.isfile("auth.txt"):
        # code for reading file in
        with open("auth.txt", 'r') as f:
            for lin in f:
                if lin.split(":")[0] == "username":
                    un = lin.split(":")[1].split("\n")[0]
                elif lin.split(":")[0] == "password":
                    pw = lin.split(":")[1].split("\n")[0]
    else:
        un = input("Please input username:\t")
        pw = getpass("Please input password")

    # Initialize ignore lists
    ignore_file = []
    ignore_folder = []
    # Load ignore list
    if os.path.isfile(os.path.join(path, "nc_ignore.txt")):
        with open(os.path.join(path, "nc_ignore.txt"), 'r') as f:
            for line in f:
                l = line.split('\n')[0]
                if os.path.isfile(l):
                    ignore_file.append(os.path.join(path, l))
                elif os.path.isdir(l):
                    ignore_folder.append(os.path.join(path, l))
                elif os.path.isfile(os.path.join(path, l)):
                    ignore_file.append(os.path.join(path, l))
                elif os.path.isdir(os.path.join(path, l)):
                    ignore_folder.append(os.path.join(path, l))

    def set_path(self, p):
        """Set path"""
        self.path = p
        return

    def read_folder(self):
        """
        This will read all files in a folder and create a dictionary
        that can be used to upload all files.

        Params:
            path str: folder name to upload

        Returns:
            dictionary of {filename: (filename, opened_file, filetype)}
        """
        # Make list of filenames with relative paths
        file_list = []

        # Walk folder and save all relative paths to file_list
        if not os.path.isdir(self.path):
            raise ValueError("Folder provided is not a real path")
        else:
            for dirpath, dirnames, filenames in os.walk(self.path):
                # dirpath: string for the path to the dir in current iteration
                # dirnames: list of names of subdirectories in dirpath
                # filenames: list of names of non-dir files in dirpath
                if dirpath in self.ignore_folder:
                    # This folder is ignored, do not push
                    continue
                for fi in filenames:
                    if (
                        fi in self.ignore_file or
                        os.path.join(dirpath, fi) in self.ignore_file
                    ):
                        continue
                    else:
                        file_list.append(
                            os.path.join(dirpath, fi)
                        )

            # Filter out non-allowed file types
            lis2 = [
                x for x in file_list if x.split('.')[-1] in self.allowed_files
            ]

        # Make dictionary of files
        files = {
            os.path.relpath(f, self.path): (  # key is filename
                os.path.relpath(f, self.path),
                open(f, 'rb'),
                'text/html'
            )
            for f in lis2
        }

        self.files = files
        return

    def login(self):
        """
        This function will start a requests.Session object,
        connect to the website and return a session and
        request object.
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
            "username": self.un,
            "password": self.pw,
            "csrf_token": csrf
        }

        # Send signin request
        res = s.post(signin_url, data=auth)

        # Verify login worked:
        if r"<title>Neocities - Sign In</title>" in res.text:
            print("Login failed")
        else:
            print("Login Success")

        # Assign values to class
        self.s = s
        self.res = res
        return

    def upload_files(self):
        """
        Take the files we read in and push them to Neocities

        Params:
            s: Session object that holds cookies for login
            validation

        Returns:
            None
        """
        # Pull page for csrf value
        req = self.s.get("https://www.neocities.org/dashboard")
        x = html.fromstring(req.content)
        csrf = x.xpath(
                    "//form[@id='uploadFilesButtonForm']/\
                        input[@name='csrf_token']/@value"
        )[0]
        csrf_str = str(csrf)

        # Push all values to NeoCities
        output = self.s.post(
            self.up_url,
            files=self.files,
            data={'csrf_token': csrf_str}
        )

        # Check if file upload was successful
        if output.status_code == 200:
            print("File upload success")
        else:
            print("Upload failed:\t", output.status_code)
            print(output.text)


if __name__ == "__main__":
    fu = fileUploader()
    fu.login()
    fu.read_folder()
    fu.upload_files()
