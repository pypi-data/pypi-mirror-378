import os, shutil

from .required_assets import REQUIRED_ASSETS

from localcosmos_cordova_builder.logger import get_logger

# WORKDIR is the directory where node_modules and the cordova binary are installed
WORKDIR = os.getenv('LOCALCOSMOS_CORDOVA_BUILDER_WORKDIR', None)
if not WORKDIR:
    raise ValueError('LOCALCOSMOS_CORDOVA_BUILDER_WORKDIR environment variable not found')

CORDOVA_CLI_VERSION = '12.0.0'

ANDROID_BUNDLETOOL_FILENAME = 'bundletool-all-1.18.1.jar'
ANDROID_BUNDLETOOL_LINK = os.path.join('https://github.com/google/bundletool/releases/download/1.18.1/', ANDROID_BUNDLETOOL_FILENAME)

DEFAULT_CORDOVA_PLATFORM_VERSIONS = {
    "android" : "android@14.0.1",
    "ios" : "ios@7.1.0",
    "browser" : "browser@7.1.1",
}

REQUIRED_PLUGINS = ['cordova-plugin-assetpack']

PLATFORM_IOS = 'ios'
PLATFORM_ANDROID = 'android'
PLATFORM_BROWSER = 'browser'

class CordovaBuildError(Exception):
    pass


import subprocess, os, shutil, zipfile, json
from subprocess import PIPE


from .AppImageCreator import AndroidAppImageCreator, IOSAppImageCreator, BrowserAppImageCreator

from lxml import etree


'''
    has to be independant from django model instances and app builder instances, as it also runs on a mac

    _cordova_build_path: root folder where cordova projects are created (command cordova create ...), inside the versioned app folder
    e.g.: on linux with app kit: /{settings.APP_KIT_ROOT}/{APP_UUID}/version/{APP_VERSION}/release/cordova
    e.g. on mac: /{jobmanager_settings.json['apps_root_folder']}/{APP_UUID}/version/{APP_VERSION}/release/cordova

    _app_build_sources_path: a folder containing all files required for a successful build
    e.g. on linux with app kit: /{settings.APP_KIT_ROOT}/{APP_UUID}/version/{APP_VERSION}/release/sources
    e.g. on mac: /{jobmanager_settings.json['apps_root_folder']}/{APP_UUID}/version/{APP_VERSION}/release/sources
    subfolders of sources are_ common/www , android/www , ios/www
'''
class CordovaAppBuilder:

    # cordova creates aabs in these folders
    unsigned_release_aab_output_path = 'platforms/android/app/build/outputs/bundle/release/app-release-unsigned.aab'
    signed_release_aab_output_path = 'platforms/android/app/build/outputs/bundle/release/app-release.aab'
    
    signed_apk_output_folder = 'platforms/android/app/build/outputs/apk/release/'
    apks_filename = 'app-release.apks'
    signed_apk_output_filename = 'app-release.apk'

    def __init__(self, meta_app_definition, _cordova_build_path, _app_build_sources_path):

        self.meta_app_definition = meta_app_definition

        self.build_number = meta_app_definition.build_number

        # path where cordova projects (apps) are build
        # eg version/5/release/cordova
        self._cordova_build_path = _cordova_build_path

        # {settings.APP_KIT_ROOT}/{meta_app.uuid}/{meta_app.current_version}/release/sources/
        self._app_build_sources_path = _app_build_sources_path
        
        # currently settings are only used for the smtp logger
        smtp_settings = {}
        settings_filepath = os.path.join(WORKDIR, 'app_builder_settings.json')
        
        if os.path.isfile(settings_filepath):
            with open(settings_filepath, 'r') as settings_file:
                cab_settings = json.loads(settings_file.read())
                smtp_settings = cab_settings['email']
            
        self.logger = self._get_logger(smtp_settings=smtp_settings)


    def _get_logger(self, smtp_settings={}):

        if hasattr(self, 'logger'):
            return self.logger
            
        logger_name = '{0}-logger'.format(self.__class__.__name__)
        # for cross platform logging use a logfolder within the folder in which JobManager.py lies
        logging_folder = os.path.join(WORKDIR, 'log/cordova_app_builder/')
        logfile_name = self.meta_app_definition.uuid

        self.logger = get_logger(logger_name, logging_folder, logfile_name, smtp_settings=smtp_settings)

        return self.logger

    #####################################################################################################
    # PATHS
    # it is intended to have the same folder within WORKDIR/apps (=apps root) layout on both linux and mac os
    # see AppReleaseBuilder.py for comparison
    @property
    def _app_folder_name(self):
        return self.meta_app_definition.package_name

    # {settings.APP_KIT_ROOT}/{meta_app.uuid}/{meta_app.current_version}/release/sources/www
    @property
    def _app_build_sources_www_path(self):
        return os.path.join(self._app_build_sources_path, 'www')

    # {settings.APP_KIT_ROOT}/{meta_app.uuid}/{meta_app.current_version}/release/sources/www
    @property
    def _app_build_sources_cordova_assets_path(self):
        return os.path.join(self._app_build_sources_path, 'cordova')

    # {settings.APP_KIT_ROOT}/{meta_app.uuid}/{meta_app.current_version}/release/cordova/{package_name}/
    @property
    def _app_cordova_path(self):
        return os.path.join(self._cordova_build_path, self._app_folder_name)

    # {settings.APP_KIT_ROOT}/{meta_app.uuid}/{meta_app.current_version}/release/cordova/{package_name}/www/
    @property
    def _cordova_www_path(self):
        return os.path.join(self._app_cordova_path, 'www')

    # {settings.APP_KIT_ROOT}/{meta_app.uuid}/{meta_app.current_version}/release/cordova/{package_name}/config.xml
    @property
    def config_xml_path(self):
        return os.path.join(self._app_cordova_path, 'config.xml')

    # {settings.APP_KIT_ROOT}/{meta_app.uuid}/{meta_app.current_version}/release/sources/cordova/config.xml
    @property
    def _custom_config_xml_path(self):
        return os.path.join(self._app_build_sources_cordova_assets_path, 'config.xml')

    # {settings.APP_KIT_ROOT}/{meta_app.uuid}/{meta_app.current_version}/release/sources/cordova/res
    @property
    def _app_cordova_res_source_folder_path(self):
        return os.path.join(self._app_build_sources_cordova_assets_path, 'res')

    # {settings.APP_KIT_ROOT}/{meta_app.uuid}/{meta_app.current_version}/release/cordova/{package_name}/res/
    @property
    def _cordova_res_folder_path(self):
        return os.path.join(self._app_cordova_path, 'res')
    
    @property
    def _android_bundletool_folder_path(self):
        return os.path.join(WORKDIR, 'android_bundletool')

    # installing the cordova CLI
    def load_cordova(self):

        self.logger.info('Loading cordova environment')

        # setup cordova
        cordova_manager = CordovaManager()
        cordova_is_installed = cordova_manager.cordova_is_installed()
        if not cordova_is_installed:
            self.logger.info('Installing cordova@{0} in {1}'.format(CORDOVA_CLI_VERSION, WORKDIR))
            cordova_manager.install_cordova()

        self.cordova_bin = cordova_manager.cordova_bin


    # delete and recreate a folder
    def deletecreate_folder(self, folder):
        if os.path.isdir(folder):
            for root, dirs, files in os.walk(folder):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    dirpath = os.path.join(root, d)
                    if os.path.islink(dirpath):
                        os.unlink(dirpath)
                    else:
                        shutil.rmtree(dirpath)
        else:
            os.makedirs(folder)


    #######################################################################################################
    # blank app and plugins
    def _get_cordova_platform_version(self, platform):

        platform_version = DEFAULT_CORDOVA_PLATFORM_VERSIONS[platform]

        frontend_settings = self.meta_app_definition.frontend
        cordova_settings = frontend_settings.get('cordova', {})
        platforms = cordova_settings.get('platforms', {})
        
        if platform in platforms:
            platform_version = platforms[platform]

        return platform_version


    def _get_cordova_plugins(self):
    
        frontend_settings = self.meta_app_definition.frontend
        cordova_settings = frontend_settings.get('cordova', {})
        plugins = cordova_settings.get('plugins', [])
        
        plugins = plugins + REQUIRED_PLUGINS

        return plugins

    
    def _install_cordova_plugins(self):

        commands = []

        plugins = self._get_cordova_plugins()
        for plugin in plugins:
            commands.append([self.cordova_bin, 'plugin', 'add', plugin])

        for command in commands:
            process_completed = subprocess.run(command, stdout=PIPE, stderr=PIPE, cwd=self._app_cordova_path)

            if process_completed.returncode != 0:
                raise CordovaBuildError(process_completed.stderr)
            

    # rebuild should be set to False once we are out of development
    def _build_blank_cordova_app(self, rebuild=True):

        if rebuild == True:
            self.logger.info('rebuild is set to True. removing {0}'.format(self._cordova_build_path))
            if os.path.isdir(self._cordova_build_path):
                shutil.rmtree(self._cordova_build_path)

        # check for the cordova app
        if os.path.isdir(self._cordova_build_path):
            self.logger.info('Cordova build path already exists: {0}'.format(self._cordova_build_path))
            
        else:
            os.makedirs(self._cordova_build_path)

            self.logger.info('Building initial blank cordova app')
            
            # create a blank cordova app via command
            # cordova create hello com.example.hello HelloWorld

            package_name = self.meta_app_definition.package_name

            create_command = [self.cordova_bin, 'create', self._app_folder_name, package_name,
                              self.meta_app_definition.name]

            create_process_completed = subprocess.run(create_command, stdout=PIPE, stderr=PIPE,
                                                      cwd=self._cordova_build_path)

            if create_process_completed.returncode != 0:
                raise CordovaBuildError(create_process_completed.stderr)

            self.logger.info('successfully built initial blank cordova app')

            
    def _update_config_xml(self):

        package_name = self.meta_app_definition.package_name

        # add custom config.xml if any
        custom_config_xml_path = self._custom_config_xml_path

        if os.path.isfile(custom_config_xml_path):
            self.logger.info('Copying custom config xml')
            shutil.copyfile(custom_config_xml_path, self.config_xml_path)                
            
            # make sure widget.id and <name> are set correctly
            # <widget xmlns="http://www.w3.org/ns/widgets" xmlns:cdv="http://cordova.apache.org/ns/1.0" id="[package_name]" version="5.0.385">
            # <name>[self.meta_app_definition.name]</name>

            with open(self.config_xml_path, 'rb') as config_file:
                xml_tree = etree.parse(config_file)
            
            root = xml_tree.getroot()
            root.attrib['id'] = package_name
            
            for child in root:
                tag_name = etree.QName(child.tag).localname
                if tag_name == 'name':
                    child.text = self.meta_app_definition.name
                    break
            
            with open(self.config_xml_path, 'wb') as config_file:
                xml_tree.write(config_file, encoding='utf-8', xml_declaration=True, pretty_print=True)

        # add stuff to config
        # <preference name="SplashMaintainAspectRatio" value="true" />
        # <preference name="StatusBarStyle" value="blackopaque" />
        # <preference name="StatusBarOverlaysWebView" value="false" />
        # <preference name="StatusBarBackgroundColor" value="#000000" />

        preferences = [
            {'name' : 'SplashMaintainAspectRatio', 'value' : 'true'},
            {'name' : 'StatusBarStyle', 'value' : 'blackopaque'},
            {'name' : 'StatusBarOverlaysWebView', 'value' : 'false'},
            {'name' : 'StatusBarBackgroundColor', 'value' : '#000000'},
            {'name' : 'DisallowOverscroll', 'value': 'true'},
        ]

        for tag_attributes in preferences:
            self._add_to_config_xml('preference', tag_attributes=tag_attributes)
            
        # enable asset pack delivery for android
        # inside <platform name="android"> add:
        # <preference name="AssetPackSourcePath" value="localcosmos/user_content/content_images" />
        self._add_to_config_xml('preference', tag_attributes={'name' : 'AssetPackSourcePath',
                                                             'value' : 'localcosmos/user_content/content_images'},
                                parent_node_name='platform', parent_node_attributes={'name' : 'android'})
        
    
    #####################################################################################################
    # add WWW
    # determine if the www folder already is the apps one: check for www/settings,json

    def _add_cordova_www_folder(self):

        self.logger.info('Adding app www, removing if already exists')

        if os.path.isdir(self._cordova_www_path):
            shutil.rmtree(self._cordova_www_path)

        source_www_path = os.path.join(self._app_build_sources_path, 'www')

        # copy common www, cordova cannot work with symlinks
        shutil.copytree(source_www_path, self._cordova_www_path)
        

    #####################################################################################################
    # CONFIG XML
    # 
    def _add_to_config_xml(self, tag_name, tag_attributes={}, parent_node_name=None, parent_node_attributes={}):
        """
        Add a tag to the config.xml file. Supports adding to the root or a specific parent node.

        :param tag_name: Name of the tag to add.
        :param tag_attributes: Attributes of the tag to add.
        :param parent_node_name: Name of the parent node to add the tag under (optional).
        :param parent_node_attributes: Attributes of the parent node (optional, used if parent node needs to be created).
        """
        with open(self.config_xml_path, 'rb') as config_file:
            config_xml_tree = etree.parse(config_file)

        # Get the root element (widget tag)
        root = config_xml_tree.getroot()

        # Determine the parent node
        parent_node = root
        if parent_node_name:
            # Search for the parent node
            for child in root:
                if etree.QName(child.tag).localname == parent_node_name:
                    # Check if all specified attributes match
                    if all(child.attrib.get(k) == v for k, v in parent_node_attributes.items()):
                        parent_node = child
                        break
            else:
                # If the parent node does not exist, create it
                parent_node = etree.Element(parent_node_name, attrib=parent_node_attributes)
                root.append(parent_node)

        # Check if the tag already exists under the parent node
        exists = False
        for child in parent_node:
            if etree.QName(child.tag).localname == tag_name:
                if all(child.attrib.get(k) == v for k, v in tag_attributes.items()):
                    exists = True
                    break

        # Add the tag if it does not exist
        if not exists:
            new_element = etree.Element(tag_name, attrib=tag_attributes)
            parent_node.append(new_element)

            # Write the updated XML back to the file
            with open(self.config_xml_path, 'wb') as config_file:
                config_xml_tree.write(config_file, encoding='utf-8', xml_declaration=True, pretty_print=True)


    # Full version number expressed in major/minor/patch notation.
    # currently only major is supported
    def set_config_xml_app_version(self, app_version, build_number):

        with open(self.config_xml_path, 'rb') as config_file:
            config_xml_tree = etree.parse(config_file)

        # root is the widget tag
        root = config_xml_tree.getroot()

        version_string = '{0}.0.{1}'.format(app_version, build_number)

        root.set('version', version_string)
        
        with open(self.config_xml_path, 'wb') as config_file:
            config_xml_tree.write(config_file, encoding='utf-8', xml_declaration=True, pretty_print=True)


    def _copy_cordova_res_folder(self):

        if os.path.isdir(self._app_cordova_res_source_folder_path):

            if not os.path.isdir(self._cordova_res_folder_path):
                self.logger.info('Copying res folder: {0} to {1}'.format(self._app_cordova_res_source_folder_path, self._cordova_res_folder_path))
                shutil.copytree(self._app_cordova_res_source_folder_path, self._cordova_res_folder_path)
            else:
                self.logger.info('res folder already present, not copying res folder.')
        else:
            self.logger.info('No res folder found, not copying res folder.')


    ##############################################################################################################
    # BUILD CONFIG
    ##############################################################################################################
    def _get_build_config_path(self):
        return os.path.join(WORKDIR, 'build_config.json')

            
    ##############################################################################################################
    # BUILD ANDROID AAB
    # - create blank cordova app
    # - install plugins
    # - copy config.xml and other files
    # - copy www
    # - run cordova build command
    ##############################################################################################################
    
    def build_android(self, keystore_path, keystore_password, key_password, rebuild=False):

        self.logger.info('Building cordova android app')

        self.load_cordova()

        self._build_blank_cordova_app(rebuild=rebuild)

        self._update_config_xml()

        self._copy_cordova_res_folder()

        self._install_cordova_plugins()

        # set app version
        self.set_config_xml_app_version(self.meta_app_definition.current_version, self.build_number)

        platform_version = self._get_cordova_platform_version(PLATFORM_ANDROID)

        self.logger.info('Adding android platform {0}'.format(platform_version))
        add_android_command = [self.cordova_bin, 'platform', 'add', platform_version]


        add_android_completed_process = subprocess.run(add_android_command, stdout=PIPE, stderr=PIPE,
                                                       cwd=self._app_cordova_path)

        if add_android_completed_process.returncode != 0:
            raise CordovaBuildError(add_android_completed_process.stderr)
        
        # replace cordova default www with android www
        self._add_cordova_www_folder()
        # build android images
        self.logger.info('building Android launcher images')
        image_creator = AndroidAppImageCreator(self.meta_app_definition, self._app_cordova_path,
                                                self._app_build_sources_path)
        
        for image_type, image_filename in REQUIRED_ASSETS.items():
            image_creator.generate_images_from_svg(image_type)
        
        self.logger.info('initiating cordova build android for release aab')
        build_android_command = [self.cordova_bin, 'build', 'android', '--release', '--',
                                 '--keystore={0}'.format(keystore_path),
                                 '--storePassword={0}'.format(keystore_password),
                                 '--alias=localcosmos', '--password={0}'.format(key_password)]

        build_android_process_completed = subprocess.run(build_android_command, stdout=PIPE, stderr=PIPE,
                                                         cwd=self._app_cordova_path)

        if build_android_process_completed.returncode != 0:
            raise CordovaBuildError(build_android_process_completed.stderr)
        
        return self._aab_filepath


    @property
    def _aab_filepath(self):
        # uses the default .aab filename created by cordova
        return os.path.join(self._app_cordova_path, self.signed_release_aab_output_path)
    
    ##############################################################################################################
    # BUILD ANDROID .apk
    # uses bundletool to create an apk from the aab
    def build_android_apk(self, aab_path, keystore_path, keystore_password, key_password):
        if not os.path.isfile(aab_path):
            raise CordovaBuildError('AAB file not found: {0}'.format(aab_path))

        self.logger.info('Building cordova android apk from aab')

        if not os.path.isdir(self._apk_folder):
            self.logger.info('Creating apk folder: {0}'.format(self._apk_folder))
            os.makedirs(self._apk_folder)

        self.download_bundletool()
        self.logger.info('Using bundletool to create apk from aab')

        # Generate APKs from AAB using BundleTool
        bundletool_command = [
            'java', '-jar', self._bundletool_jar_path,
            'build-apks',
            '--bundle', aab_path,
            '--output', self._apks_filepath,
            '--ks', keystore_path,
            '--ks-pass', 'pass:{0}'.format(keystore_password),
            '--ks-key-alias', 'localcosmos',
            '--key-pass', 'pass:{0}'.format(key_password),
            '--mode', 'universal'
        ]

        process_completed = subprocess.run(bundletool_command, stdout=PIPE, stderr=PIPE)

        if process_completed.returncode != 0:
            raise CordovaBuildError('Failed to create APK from AAB: {0}'.format(process_completed.stderr.decode('utf-8')))

        # Verify the contents of the .apks file
        self.logger.info('Verifying contents of the .apks file')
        list_command = ['unzip', '-l', self._apks_filepath]
        list_process_completed = subprocess.run(list_command, stdout=PIPE, stderr=PIPE)

        if list_process_completed.returncode != 0:
            raise CordovaBuildError('Failed to list contents of .apks file: {0}'.format(list_process_completed.stderr.decode('utf-8')))

        # Check if universal.apk exists in the .apks file
        if b'universal.apk' in list_process_completed.stdout:
            apk_to_extract = 'universal.apk'
        else:
            raise CordovaBuildError('universal.apk not found in .apks file. Ensure the .apks file was generated with --mode universal.')

        # Extract the universal APK from the .apks file
        extract_command = [
            'unzip', '-o', self._apks_filepath, apk_to_extract, '-d', self._apk_folder
        ]

        extract_process_completed = subprocess.run(extract_command, stdout=PIPE, stderr=PIPE)

        if extract_process_completed.returncode != 0:
            raise CordovaBuildError('Failed to extract APK from .apks file: {0}'.format(extract_process_completed.stderr.decode('utf-8')))

        # Rename the extracted APK to the desired output filename
        extracted_apk_path = os.path.join(self._apk_folder, apk_to_extract)
        if os.path.isfile(extracted_apk_path):
            os.rename(extracted_apk_path, self._apk_filepath)
            self.logger.info('APK successfully created: {0}'.format(self._apk_filepath))
        else:
            raise CordovaBuildError('Extracted APK not found: {0}'.format(extracted_apk_path))

        return self._apk_filepath
    
    
    def download_bundletool(self):
        
        if not os.path.isfile(self._bundletool_jar_path):
            self.logger.info('Downloading bundletool.jar')
            
            if not os.path.isdir(self._android_bundletool_folder_path):
                os.makedirs(self._android_bundletool_folder_path)
                
            bundletool_command = ['wget', ANDROID_BUNDLETOOL_LINK, '-O', self._bundletool_jar_path]
            bundletool_process_completed = subprocess.run(bundletool_command, stdout=PIPE, stderr=PIPE,
                                                           cwd=self._android_bundletool_folder_path)
            if bundletool_process_completed.returncode != 0:
                raise CordovaBuildError('Could not download bundletool: {0}'.format(bundletool_process_completed.stderr))
    
    @property
    def _bundletool_jar_path(self):
        return os.path.join(self._android_bundletool_folder_path, ANDROID_BUNDLETOOL_FILENAME)
    
    @property
    def _apk_folder(self):
        return os.path.join(self._app_cordova_path, self.signed_apk_output_folder)
    
    @property
    def _apk_filepath(self):
        return os.path.join(self._apk_folder, self.signed_apk_output_filename)
    
    @property
    def _apks_filepath(self):
        return os.path.join(self._apk_folder, self.apks_filename)
        

    ##############################################################################################################
    # BUILD iOS .ipa
    # - create blank cordova app, if not yet present
    # - install plugins
    # - copy config.xml and other files
    # - copy www
    # - run cordova build command
    ##############################################################################################################

    @classmethod
    def get_ipa_filename(cls, meta_app_definition):
        filename = '{0}.ipa'.format(meta_app_definition.name)
        return filename

    @property
    def _ipa_folder(self):
        return os.path.join(self._app_cordova_path, 'platforms/ios/build/Release-iphoneos/')

    @property
    def _ipa_filepath(self):
        filename = self.get_ipa_filename(self.meta_app_definition)
        return os.path.join(self._ipa_folder, filename)

    # only set once, check if it already exists first
    def set_ios_info_plist_value(self, key, value):

        with open(self.config_xml_path, 'rb') as config_file:
            config_xml_tree = etree.parse(config_file)

        # root is the widget tag
        root = config_xml_tree.getroot()

        element_exists = False

        edit_attributes = {
            'target' : key,
            'file' : '*-Info.plist',
            'mode' : 'merge',
        }

        # check all edit-configs
        for child in root:

            # tag without namespace
            tag_name = etree.QName(child.tag).localname
            
            if tag_name == 'edit-config':

                attributes = child.attrib

                all_attributes_match = True
                
                for attrib_key, attrib_value in edit_attributes.items():

                    existing_value = attributes.get(attrib_key)
                    
                    if existing_value != attrib_value:
                        all_attributes_match = False
                        break

                if all_attributes_match == True:

                    string_element = child[0]
                    string_tag = etree.QName(string_element.tag).localname

       
                    if string_tag == 'string' and string_element.text == value:
                        element_exists = True
                        break
                        
                
        if element_exists == False:

            new_element = etree.Element('edit-config', attrib=edit_attributes)
            string_element = etree.Element('string')
            string_element.text = value
            new_element.append(string_element)
            
            root.append(new_element)

            # xml_declaration: <?xml version='1.0' encoding='utf-8'?>
            with open(self.config_xml_path, 'wb') as config_file:
                config_xml_tree.write(config_file, encoding='utf-8', xml_declaration=True, pretty_print=True)
    '''
    <edit-config target="NSLocationWhenInUseUsageDescription" file="*-Info.plist" mode="merge">
        <string>need location access to find things nearby</string>
    </edit-config>
    '''
    def set_ios_NSLocationWhenInUseUsageDescription(self):

        self.set_ios_info_plist_value('NSLocationWhenInUseUsageDescription',
                                      'location access is required for observations and maps')


    def set_ios_NSCameraUsageDescription(self):

        self.set_ios_info_plist_value('NSCameraUsageDescription',
                                      'camera access is required for taking pictures for observations')

    # <splash src="res/screen/ios/Default@2x~universal~anyany.png" />
    # <splash src="res/screen/ios/Default@3x~universal~anyany.png" />
    # res folder lies in the same folder as www
    def set_config_xml_storyboard_images(self):

        attributes_2x = {
            'src' : 'res/screen/ios/Default@2x~universal~anyany.png'
        }
        self._add_to_config_xml('splash', tag_attributes=attributes_2x)

        attributes_3x = {
            'src' : 'res/screen/ios/Default@3x~universal~anyany.png'
        }

        self._add_to_config_xml('splash', tag_attributes=attributes_3x)
    
    def build_ios(self, rebuild=False):

        self.logger.info('Building cordova ios app')
        
        self.load_cordova()

        self._build_blank_cordova_app(rebuild=rebuild)

        self._update_config_xml()

        self._install_cordova_plugins()
        
        # set app version
        self.set_config_xml_app_version(self.meta_app_definition.current_version, self.build_number)

        # set NSLocationWhenInUseUsageDescription
        self.set_ios_NSLocationWhenInUseUsageDescription()

        # set NSCameraUsageDescription
        self.set_ios_NSCameraUsageDescription()

        # NSPhotoLibraryUsageDescription
        self.set_ios_info_plist_value('NSPhotoLibraryUsageDescription',
                                      'photo library access is required for adding pictures to observations')
        
        # NSLocationAlwaysUsageDescription
        self.set_ios_info_plist_value('NSLocationAlwaysUsageDescription',
                                      'location access is required for observations and maps')

        self.set_ios_info_plist_value('NSLocationAlwaysAndWhenInUseUsageDescription',
                                      'location access is required for observations and maps')

        # enable wkwebview
        # self.config_xml_enable_wkwebview()

        self.logger.info('Adding ios platform')
        platform_version = self._get_cordova_platform_version(PLATFORM_IOS)
        add_ios_command = [self.cordova_bin, 'platform', 'add', platform_version]

        add_ios_completed_process = subprocess.run(add_ios_command, stdout=PIPE, stderr=PIPE,
                                                   cwd=self._app_cordova_path)

        if add_ios_completed_process.returncode != 0:
            if b'Platform ios already added' not in add_ios_completed_process.stderr:
                raise CordovaBuildError(add_ios_completed_process.stderr)

        # replace default cordova www folder with ios www
        self._add_cordova_www_folder()

        # build ios images
        self.logger.info('building iOS launcher and splashscreen images')
        image_creator = IOSAppImageCreator(self.meta_app_definition, self._app_cordova_path,
                                                self._app_build_sources_path)
                                                
        for image_type, image_filename in REQUIRED_ASSETS.items():
            image_creator.generate_images_from_svg(image_type)

        self.set_config_xml_storyboard_images()
        image_creator.generate_storyboard_images()

        # build ios release
        self.logger.info('initiating cordova build ios')
        build_config_path = self._get_build_config_path()

        build_ios_command = [self.cordova_bin, 'build', 'ios', '--device', '--release', '--buildConfig',
                             build_config_path]

        build_ios_process_completed = subprocess.run(build_ios_command, stdout=PIPE, stderr=PIPE,
                                                     cwd=self._app_cordova_path)

        if build_ios_process_completed.returncode != 0:
            raise CordovaBuildError(build_ios_process_completed.stderr)

        self.logger.info('successfully built ios')
        return self._ipa_filepath


    ##############################################################################################################
    # BUILD browser .zip
    # - create blank cordova app, if not yet present
    # - install plugins
    # - copy config.xml and other files
    # - copy www
    # - run cordova build command
    ##############################################################################################################

    @property
    def _browser_zip_filepath(self):
        filename = '{0}.zip'.format(self.meta_app_definition.name)
        return os.path.join(self._app_cordova_path, 'platforms/browser', filename)


    # {settings.APP_KIT_ROOT}/{meta_app.uuid}/{meta_app.current_version}/release/cordova/{meta_app_definition.package_name}/platforms/browser/www
    @property
    def _browser_built_www_path(self):
        return os.path.join(self._app_cordova_path, 'platforms/browser/www')

    def build_browser(self, rebuild=False, build_zip=False):
        
        self.logger.info('Building cordova browser app')

        self.load_cordova()

        self._build_blank_cordova_app(rebuild=rebuild)

        self._update_config_xml()

        self._copy_cordova_res_folder()

        self._install_cordova_plugins()

        # set app version
        self.set_config_xml_app_version(self.meta_app_definition.current_version, self.build_number)

        self.logger.info('Adding browser platform')
        platform_version = self._get_cordova_platform_version(PLATFORM_BROWSER)
        add_browser_command = [self.cordova_bin, 'platform', 'add', platform_version]

        add_browser_completed_process = subprocess.run(add_browser_command, stdout=PIPE, stderr=PIPE,
                                                       cwd=self._app_cordova_path)

        if add_browser_completed_process.returncode != 0:
            raise CordovaBuildError(add_browser_completed_process.stderr)

        # replace cordova default www with android www
        self._add_cordova_www_folder()

        # add ico
        self.logger.info('Creating favicon')
        image_creator = BrowserAppImageCreator(self.meta_app_definition, self._app_cordova_path,
                                                self._app_build_sources_path)

        image_creator.create_favicon()

        # build ios release
        self.logger.info('initiating cordova build browser')

        build_browser_command = [self.cordova_bin, 'build', 'browser', '--release']

        build_browser_process_completed = subprocess.run(build_browser_command, stdout=PIPE, stderr=PIPE,
                                                     cwd=self._app_cordova_path)

        if build_browser_process_completed.returncode != 0:
            raise CordovaBuildError(build_browser_process_completed.stderr)

        if build_zip == True:
            self.logger.info('building zip_file for browser')

            zip_filepath = self._browser_zip_filepath

            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as www_zip:

                for root, dirs, files in os.walk(self._browser_built_www_path, followlinks=True):

                    for filename in files:
                        app_file_path = os.path.join(root, filename)
                        arcname ='www/{0}'.format(app_file_path.split(self._browser_built_www_path)[-1])
                        www_zip.write(app_file_path, arcname=arcname)

        self.logger.info('successfully built browser')
        return self._browser_built_www_path, self._browser_zip_filepath



# install a non-global (local) copy of apache cordova
class CordovaManager:

    def __init__(self):

        if not os.path.isdir(WORKDIR):
            os.makedirs(WORKDIR)

        self.check_npm()

    @property
    def cordova_bin(self):
        cordova_bin_path = os.path.join(WORKDIR, 'node_modules/cordova/bin/cordova')
        return cordova_bin_path


    def check_npm(self):

        npm_command = ['npm', '--version', '--']

        npm_command_result = subprocess.run(npm_command, stdout=PIPE, stderr=PIPE, cwd=WORKDIR)
        if npm_command_result.returncode != 0:
            raise CordovaBuildError(npm_command_result.stderr)


    def cordova_is_installed(self):

        if os.path.isfile(self.cordova_bin):
            return True

        return False

    
    def install_cordova(self):

        cordova_install_command = ['npm', 'install', 'cordova@{0}'.format(CORDOVA_CLI_VERSION)]

        cordova_install_command_result = subprocess.run(cordova_install_command, stdout=PIPE, stderr=PIPE,
                                                        cwd=WORKDIR)

        if cordova_install_command_result.returncode != 0:
            raise CordovaBuildError(cordova_install_command_result.stderr)
