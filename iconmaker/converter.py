# -*- coding: utf-8 -*-

import subprocess
import os
import tempfile
import requests
import StringIO
from PIL import Image

from utils import get_image_sizes, which

from logger import logging

FORMAT_PNG = 'png'
FORMAT_GIF = 'gif'
FORMAT_ICO = 'ico'
FORMAT_ICNS = 'icns'


class Converter(object):
    """Convert a set of PNG/GIF icons to either ICO or ICNS format.
    """

    def _fetch_image(self, url):
        """Fetch the requested image and save it in a temporary file.

            :params input:
                URL of the image to fetch.
            :returns:
                Path to the saved_filename.
        """

        # get the image
        response = requests.get(url)

        # save the image
        im = Image.open(StringIO.StringIO(response.content))
        image_format = im.format.lower()
        if image_format not in self.supported_source_formats:
            raise Exception('The source file is not of a supported format. \
                            Supported formats are: %s' %
                            ','.join(self.supported_source_formats))

        # generate temp filename for it
        saved_file = tempfile.NamedTemporaryFile(
                        prefix='downloaded_',
                        suffix='.' + image_format,
                        dir='/tmp',
                        delete=False)
        saved_filename = saved_file.name

        im.save(saved_filename)
        return saved_filename

    def __init__(self):
        """Initializer.
        """

        self.supported_source_formats = [FORMAT_GIF, FORMAT_PNG]
        self.supported_target_formats = [FORMAT_ICO, FORMAT_ICNS]
        self.png2ico = '/usr/local/bin/png2ico'
        self.png2icns = '/usr/local/bin/png2icns'
        self.converttool = '/opt/local/bin/convert'

        # check and/or find the correct file locations
        if not os.path.isfile(self.png2ico):
            self.png2ico = which(os.path.basename(self.png2ico))
            if not self.png2ico:
                raise Exception("Unable to locate png2ico binary: %s" %
                    self.png2ico)

        if not os.path.isfile(self.png2icns):
            self.png2icns = which(os.path.basename(self.png2icns))
            if not self.png2icns:
                raise Exception("Unable to locate png2icns binary: %s" %
                    self.png2icns)

        if not os.path.isfile(self.converttool):
            self.converttool = which(os.path.basename(self.converttool))
            if not self.converttool:
                raise Exception("Unable to locate image conversion tool: %s" %
                    self.converttool)

        self.convert_binaries = {
            FORMAT_ICO: self.png2ico,
            FORMAT_ICNS: self.png2icns
        }

    def convert(self,
                target_format,
                image_list):
        """Convert a list of image files to an ico/icns file.

        :param target_format:
            ICO or ICNS.
        :param image_list:
            List of image files to convert (either local paths or URLs).

        :returns:
            Local path to the generated ico or raise an Exception
        """

        # check our input arguments
        try:
            target_format = target_format.lower()
            conversion_binary = self.convert_binaries[target_format]
        except:
            raise Exception("Invalid target format. \
                Target format must be either ICO or ICNS.")

        try:
            assert len(image_list) > 0
        except:
            raise Exception("Input list cannot be empty.")

        # image_list can contain either a local path or an http url
        new_icon_list = []
        for image_location in image_list:
            if image_location.startswith("http:") or \
                image_location.startswith("https:"):
                image_location = self._fetch_image(image_location)

            # check the extension to see if we'll
            # need to convert something else to PNG
            image_base, image_extension = os.path.splitext(image_location)
            image_extension = image_extension[1:]

            if image_extension == FORMAT_GIF:
                logging.debug('converting png to gif: %s' % image_location)
                image_location_png = "%s.%s" % (image_base, FORMAT_PNG)

                try:
                    subprocess.check_output([
                        self.converttool,
                        image_location,
                        image_location_png])
                except subprocess.CalledProcessError, e:
                    raise Exception('Failed to convert GIF to PNG: %s' %
                        e.output)

                image_location = image_location_png

            new_icon_list.append(image_location)

        image_list = new_icon_list

        # output file in ICNS or ICO format
        output_file = tempfile.NamedTemporaryFile(
                        prefix='output_',
                        suffix='.%s' % target_format,
                        dir='/tmp',
                        delete=False)
        output_filename = output_file.name

        # Rules for ICNS generation:
        # (1) width must be multiple of 8 and <256.
        # (2) Height must be <256.
        # (3) Cannot be 64x64
        # Rules for ICO generation:
        # (1) and
        # (2) above
        # todo: compile Jasper libs to support 512 and 1024 icons

        # cache image size
        image_dict = get_image_sizes(image_list)

        # sort by size descending, and get the largest image path
        largest_image = sorted(image_dict.items(),
                                key=lambda x: x[1],
                                reverse=True)[0][0]

        existing_sizes = sorted(image_dict.values(), reverse=True)

        largest_size = existing_sizes[0]

        # generate the missing_sizes image sizes (by downscaling largest icon)
        #  need sizes: 16, 32, 64, 128, 256, 512, 1024
        need_sizes = [16, 32, 64, 128, 256, 512, 1024]
        missing_sizes = set(need_sizes) - set(existing_sizes)

        # we'll only generate if missing sizes are
        # less than the largest size available
        missing_sizes = [i for i in missing_sizes if i < largest_size]
        logging.debug('missing sizes: %s (%s)' %
            (missing_sizes, largest_image))

        # create the missing images by
        # downscaling the `largest_image` above
        for m in missing_sizes:
            image_base, image_extension = os.path.splitext(largest_image)
            image_extension = image_extension[1:]

            new_size = "%dx%d" % (m, m)

            resized_file = tempfile.NamedTemporaryFile(
                                prefix='resized_%s' % new_size,
                                suffix='.%s' % image_extension,
                                dir='/tmp',
                                delete=False)
            resized_filename = resized_file.name

            try:
                subprocess.check_output([
                    self.converttool,
                    largest_image,
                    "-resize",
                    new_size,
                    resized_filename])
            except subprocess.CalledProcessError, e:
                raise Exception('Failed to resize image: %s' % e.output)

        ## filter out certain icons
        if target_format == FORMAT_ICNS:
            image_list = [i for i in image_list if
                            image_dict[i] in need_sizes and
                            image_dict[i] != 64 and
                            image_dict[i] < 256]
        else:
            image_list = [i for i in image_list if
                            image_dict[i] % 8 == 0 and
                            image_dict[i] < 256]

        # builds args for the conversion command
        logging.debug('image list: %s' % image_list)
        args = image_list
        args.insert(0, output_filename)
        args.insert(0, conversion_binary)

        # execute conversion command
        try:
            subprocess.check_output(args)
        except subprocess.CalledProcessError, e:
            raise Exception('Failed to create container icon: %s' % e.output)

        return output_filename
