"""
Copyright (c) 2014-2016 Gui Talarico
Written for pyRevit
TESTED API: 2015 | 2016

----------------------------------------------------------------------------
pyRevit Notice
Copyright (c) 2014-2016 Ehsan Iran-Nejad
Python scripts for Autodesk Revit

This file is part of pyRevit repository at https://github.com/eirannejad/pyRevit
See this link for a copy of the GNU General Public License protecting this package.
https://github.com/eirannejad/pyRevit/blob/master/LICENSE
"""

# TO DO:
# Use urllibe instead of webclient? Permissions
# Clean up temp files properly


__doc__ = "Package Manager Test."
__version__ = "0.1.0"

import clr
import os
import sys
import json
import re
import logging
import shutil
import time
# import urllib2
# from tempfile import NamedTemporaryFile, tempdir
from zipfile import ZipFile
from collections import defaultdict, OrderedDict

RELEASE_URL = 'https://raw.githubusercontent.com/gtalarico/pyrevitplus/master/release/'
PACKAGES_URL = RELEASE_URL + 'packages.json'
PYREVIT_DIR = os.path.dirname(os.path.dirname(__file__))
PYREVITPLUS_DIR = os.path.join(PYREVIT_DIR, 'pyRevitPlus')
BREAKLINE = '=' * 40
TEMPDIR = os.getenv('TEMP')

# Make Pyrevit Directory if it doesn't exist.
if not os.path.exists(PYREVITPLUS_DIR):
    os.mkdir(PYREVITPLUS_DIR)

handler = logging.StreamHandler(sys.stdout)
logger = logging.getLogger('pyrevitplust-manage')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

clr.AddReference('System')
clr.AddReference('System.Net')
clr.AddReference('System.IO')
clr.AddReference('System.Drawing')
clr.AddReference("System.Windows.Forms")
from System.Windows import Forms
from System.Windows.Forms import Application, Button, Form, Label, CheckBox, DialogResult, GroupBox
from System.Drawing import Point, Icon
from System.Net import HttpWebRequest
from System.Net import WebClient
from System.IO import StreamReader

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import TaskDialog, TaskDialogCommandLinkId
from Autodesk.Revit.UI import TaskDialogCommonButtons

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

def get_pkgs():
    logger.info('Getting packages list...')
    try:
        json_response = WebClient().DownloadString(PACKAGES_URL)
    except Exception as errmsg:
        logger.error('Error: %s', errmsg)
    else:
        json_data = json.loads(json_response, object_pairs_hook=OrderedDict)
        packages = json_data.get('packages')
        logger.debug('packages.json: \n %s', packages)
        return packages

def get_package_version(filelist):
    pat = r"(?:__version__.+)(?:\"|\')(\d\.\d\.\d)(?:\"|\')"
    for filename in filelist:
        logger.debug('Checking filename: %s', filename)
        filepath = os.path.join(PYREVITPLUS_DIR, filename)
        try:
            with open(filepath) as fp:
                content = fp.read()
        except:
            continue
        result = re.search(pat, content)
        if result:
            version = result.group(1)
            logger.debug('Found version: %s', version)
            return version
    logger.warning('Could not find version.')
    return 0

def check_local_pkgs(packages):
    logger.info('Checking local packages...')
    local_pkgs = defaultdict(list)
    logger.debug('Local Folders: %s', os.listdir(PYREVITPLUS_DIR))
    local_files = os.listdir(PYREVITPLUS_DIR)
    for package_id, package in packages.items():
        files_present = [bool(filename in local_files) for filename in package['files']]
        if all(files_present):
            local_pkgs['installed'].append(package_id)
        elif any(files_present):
            local_pkgs['missing_files'].append(package_id)
    logger.debug('Local Packages: %s', local_pkgs)
    return local_pkgs

def donwload_package(package_id, package_version):
    package_url = RELEASE_URL + package_id + package_version
    package_url = '{}{}_{}.zip'.format(RELEASE_URL, package_id, package_version)
    logger.info('Downloading: {}'.format(package_url))
    tempfile = os.path.join(TEMPDIR, package_id) + '.zip'
    tempdir = os.path.join(TEMPDIR, package_id)
    if os.path.exists(tempfile) or os.path.exists(tempdir):
        try:
            os.remove(tempfile)
        except:
            pass
        try:
            shutil.rmtree(tempdir)
        except:
            pass
    os.mkdir(tempdir)
    try:
        with open(tempfile,'w') as fp:
            fp.write('Test')
        client = WebClient()
        client.CancelAsync()
        client.DownloadFile(package_url, tempfile)
        client.Dispose()

        logger.info('File Downloaded.')
    except Exception as errmsg:
        print('Error: %s', errmsg)
    else:
        with ZipFile(tempfile,'r') as zip_ref:
            zip_ref.extractall(tempdir)
        logger.debug('Zip Extracted.')
    finally:
        for filename in os.listdir(tempdir):
            filepath = os.path.join(tempdir, filename)
            shutil.copy2(filepath, PYREVITPLUS_DIR)
        print('Files Copied. Deleting temp zip')
        try:
            ''' Files are not being properly removed'''
            shutil.rmtree(tempdir)
            os.remove(tempfile)
        except Exception as errmsg:
            logger.exception('Error deleting Temp file.')


def sync_pkgs(packages, local_pkgs, to_remove=None, to_install=None):
    logger.debug('PACKAGES: %s', packages)
    logger.debug('TO REMOVE: %s', to_remove)
    logger.debug('TO INSTALL: %s', to_install)
    logger.debug('ALREADY INSTALLED: %s', local_pkgs['installed'])
    logger.debug('INSTALLED BUT MISSING: %s', local_pkgs['missing_files'])

    # TO REMOVE:
    for package_id in to_remove:
        if package_id not in local_pkgs['installed']:
            logger.debug('[{}] unchecked, but not installed'.format(package_id))
            continue
        package_version = packages[package_id]['version']
        package_files = packages[package_id]['files']

        logger.info('Deleting Package: {}'.format(package_id))
        for filename in packages[package_id]['files']:
            filepath = os.path.join(PYREVITPLUS_DIR, filename)
            logger.info('Deleting file: {}'.format(filepath))
            try:
                os.remove(filepath)
            except Exception as errmsg:
                logger.error('Could not delete file: {}'.format(filepath))
                logger.error('ERROR: {}'.format(errmsg))
        logger.info('PACKAGE DELETED.')
        local_pkgs['installed'].remove(package_id)

    for package_id in to_install:
        logger.info('Installing Package: {}'.format(package_id))
        package_version = packages[package_id]['version']
        package_files = packages[package_id]['files']

        if package_id in local_pkgs['installed']:
            local_version = get_package_version(package_files)
            if local_version == package_version:
                logger.info('Latest Version is installed. Skipping.')
                continue
            logger.info('[{}] installed but outdated.'.format(package_id))
            logger.info('will delete first then download')
            # DELETE LOCAL
        donwload_package(package_id, package_version)
        local_pkgs['installed'].append(package_id)


    # local_pkgs['installed'].remove(package_id)


class pyRevitPlusForm(Form):

    def __init__(self, packages, local_pkgs):
        self.MinimizeBox = False
        self.MaximizeBox = False
        # self.ControlBox = False;
        self.Text = 'pyRevit Plus'
        dirname = os.path.dirname(__file__)
        icon_name = os.path.join(dirname,"manage.ico")
        logger.info(icon_name)
        self.Icon = Icon(icon_name)

        start_x = 20
        start_y = 20

        label = Label()
        label.Location = Point(start_x, start_y)
        label.Text = "Available Packages"
        label.AutoSize = True
        self.Controls.Add(label)

        cbox_packages = []
        cbox_x = start_x
        cbox_y = start_y

        for package_id, package in packages.items():
            cbox = CheckBox()
            cbox.Name = package_id
            cbox.Text = package['name']
            cbox.AutoSize = True
            cbox_x = cbox_x
            cbox_y = cbox_y + 20
            cbox.Location = Point(cbox_x, cbox_y)
            if package_id in local_pkgs['installed']:
                # cbox.Text = cbox.Text + ': INSTALLED'
                cbox.Checked = True
            if package_id in local_pkgs['missing_files']:
                cbox.Text = cbox.Text + ' [NEEDS UPDATE]'
                cbox.Checked = True
            cbox_packages.append(cbox)

        [self.Controls.Add(cbox) for cbox in cbox_packages]
        button_cancel = Button()
        button_cancel.Text = "Cancel"
        button_x = cbox_x
        button_y = cbox_y + 40
        button_cancel.Location = Point(cbox_x, button_y)
        button_cancel.Click += self.form_exit

        button_update = Button()
        button_update.Text = "Update"
        button_x += 80
        button_update.Location = Point(button_x, button_y)
        button_update.Click += self.form_update

        self.Controls.Add(button_cancel)
        self.Controls.Add(button_update)

        self.Height = button_y + 80
        self.Width = button_x + button_update.Width + 40

    def form_exit(self, sender, event):
        self.Close()

    def form_update(self, sender, event):
        checked = []
        unchecked = []
        for control in self.Controls:
            if isinstance(control, CheckBox):
                if control.Checked:
                    checked.append(control)
                else:
                    unchecked.append(control)
        logger.debug('Checked: %s', str(checked))
        logger.debug('Unchecked: %s', str(unchecked))
        pkgs_to_install = [control.Name for control in checked]
        pkgs_to_remove = [control.Name for control in unchecked]
        sync_pkgs(packages, local_pkgs,
                  to_remove=pkgs_to_remove, to_install=pkgs_to_install)
        logger.info(BREAKLINE)
        logger.info('Syncing Done.')
        # self.Close()

if __name__ == '__main__':
    # __window__.Close()
    packages = get_pkgs()
    local_pkgs = check_local_pkgs(packages)
    if not packages:
        TaskDialog.Show('Error', 'Could not Download Packages List.')
    else:
        form = pyRevitPlusForm(packages, local_pkgs)
        Application.Run(form)


# dialog = TaskDialog("Packages")
# dialog.MainContent = "Install Packages"
# dialog.AddCommandLink(TaskDialogCommandLinkId.CommandLink1,
                    #   "Option 1", "Description")
# dialog.CommonButtons = (TaskDialogCommonButtons.Ok |
#                         TaskDialogCommonButtons.Cancel)
# dialog.Show()
# __window__.Close()
