# neocity_sync
This repository contains a script that I wrote to automate syncing a folder on my home tower to Neocities.
I wanted to be able to edit things without using the UI and wanted to avoid paying for the extra
subscription so this is how I'm going to do it.

I hope this script is relatively easy to use.
You can simply call the script and pass the folder to sync as the first argument.
If there is a file named 'auth.txt' in the folder, it will read in your
username and password as long as auth.txt contains a line containing
    "username:your_username"
and
    "password:your_password"

The script also has support for a 'nc_ignore.txt' file in the directory
that is being pushed. It will read in folder names and file names
and remove found items from the list before pushing to Neocities.
Hopefully this makes it easier to use in conjunction with the 
auth.txt file. Wouldn't want to accidentally push a plaintext
password to a public website.
