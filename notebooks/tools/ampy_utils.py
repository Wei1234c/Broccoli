# coding: utf-8

import os
import shutil

baud_rate = 115200
com_port = 'COM12'

def show_com_port():
    print('com_port', com_port)
    

# local files and folders
def clear_local_folder(folder):
    print('\n[Clearing folder {}]'.format(folder))
    for file in os.listdir(folder):
        os.remove(os.path.join(folder, file))

def copy_one_file_to_local_folder(folder, file, destination_folder):
    # print('Copying {} to {}'.format(file, destination_folder))
    shutil.copy(os.path.join(folder, file), destination_folder)

def copy_all_files_to_local_folder(folders, destination_folder, clear_local_folder_first = True):    
    if clear_local_folder_first:
        clear_local_folder(destination_folder)
        
    print('\n[Copying all files to upload folder {}]'.format(destination_folder))
    
    for folder in folders: 
        for file in sorted(os.listdir(folder)):
            if (file.endswith('.py') or file.endswith('.mpy')) and not file.startswith('_'):
                copy_one_file_to_local_folder(folder, file, destination_folder)


# munipulate device via ampy
def list_files_in_device():
    files = get_ipython().getoutput('ampy --port {com_port} --baud {baud_rate} ls')
    return sorted(files)
    
def cat_file_from_device(file):
    get_ipython().system('ampy --port {com_port} --baud {baud_rate} get {file}')
    
def delete_file_in_device(file):
    print('Deleting {}'.format(file))
    get_ipython().system('ampy --port {com_port} --baud {baud_rate} rm {file}')
    
def delete_files_in_device():
    print('\n[Deleting all files in device {}]'.format(com_port))
    for file in list_files_in_device():
        delete_file_in_device(file)
        
#     try:
#         !ampy --port {com_port} --baud {baud_rate} rmdir {'/'}
#     except Exception as e:
#         print(e)   

def copy_one_file_to_device(folder, file, mpy_only = False):
    if mpy_only:
        if file.endswith('.mpy'):
            print('Copying file: {}'.format(file))
            get_ipython().system('ampy --port {com_port} --baud {baud_rate} put {os.path.join(folder, file)}  ')
    elif file.endswith('.py'):
        print('Copying file: {}'.format(file))
        get_ipython().system('ampy --port {com_port} --baud {baud_rate} put {os.path.join(folder, file)} ')
        
def copy_one_folder_to_device(folder):
    print('Copying folder: {}'.format(folder))
    get_ipython().system('ampy --port {com_port} --baud {baud_rate} put {folder} ')
    
def delet_main_in_device(main_file_names):
    print('Deleting {}'.format(main_file_names))
    files = list_files_in_device()

    for file in main_file_names:
        if file in files:
            delete_file_in_device(file)
            
def delete_main_and_files_in_device(main_file_names = ['main.py', 'main.mpy'], delete_first = False, mpy_only = False):    
    delet_main_in_device(main_file_names)
    if mpy_only: delete_first = True
    if delete_first: delete_files_in_device()
        
def copy_all_files_to_device(folder, main_file_names = ['main.py', 'main.mpy'], delete_first = False, mpy_only = False):    
    for file in sorted(os.listdir(folder)):
        if (file.endswith('.py') or file.endswith('.mpy')) and not file.startswith('_') and not file in main_file_names:
            copy_one_file_to_device(folder, file, mpy_only)                    
    
    for file in main_file_names:
        if os.path.isfile(os.path.join(folder, file)):
            copy_one_file_to_device(folder, file, mpy_only) 
            
def do_all_to_device(folder, main_file_names = ['main.py', 'main.mpy'], delete_first = False, mpy_only = False):
    print('\n[Copying all files to device {}]'.format(com_port))
    delete_main_and_files_in_device(main_file_names, delete_first, mpy_only)
    copy_all_files_to_device(folder, main_file_names, delete_first, mpy_only)
    

# format device's file system
def format_file_system():
    print('\n[Formatting file system on device {}]'.format(com_port))
    
    script_file = "script.py"
    
    try:
        os.remove(script_file)
    except Exception as e:
        pass
        
    script = '''
import os, flashbdev

os.listdir()
try:
    os.umount('/')
except Exception as e:
    print(e)
os.VfsFat.mkfs(flashbdev.bdev)
os.listdir()
'''

    with open(script_file, 'w') as f:
        f.write(script)
    get_ipython().system('ampy --port {} --baud {} run {}'.format(com_port, baud_rate, script_file))
    os.remove(script_file)

    
# put_boot_files
def put_boot_files(root_folders, delete_first = False, clear_local_folder_first = True):
    upload_folder = os.path.join('upload', 'py')
    copy_all_files_to_local_folder(root_folders, upload_folder, clear_local_folder_first = clear_local_folder_first)
    do_all_to_device(upload_folder, delete_first = delete_first)


# put folders    
def put_folders(folders):
    print('\n[Copying all folders to device {}]'.format(com_port))
    for folder in sorted(folders):
        copy_one_folder_to_device(folder)

 
# do it all
def format_put_files_folders(root_folders, folders = [], format_first = True, delete_first = False, clear_local_folder_first = True):
    if format_first:
        format_file_system()
    put_boot_files(root_folders, delete_first = delete_first, clear_local_folder_first = clear_local_folder_first)
    put_folders(folders)
    print('\n[All done!]')
    