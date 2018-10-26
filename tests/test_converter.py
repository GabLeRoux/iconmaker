import os
import random
import tempfile
import unittest

try:
    # noinspection PyCompatibility
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from iconmaker.converter import FORMAT_ICO, FORMAT_ICNS
from iconmaker.converter import Converter
from iconmaker.exceptions import ConversionError

ICONS_TEST_DIR = os.path.join(os.path.dirname(
    os.path.abspath(__file__)),
    'icons')
RANDOM_ICONSETS = 10
LARGE_ICONSETS = 10
NONSQUARE_ICONSETS = 10
INVALID_ICNS_ICONSETS = 10


class ConverterTests(unittest.TestCase):
    """Unit tests for various conversion operations.
    """

    def setUp(self):
        self.converter = Converter()

    def assertAllTargetFormatsRaise(self, exception, files):
        """``convert`` calls with any target format raises the given exception.

        :param exception: Exception type.
        :param files: File list to pass to the convert class.
        """
        print("exception type:", exception)
        with self.assertRaises(Exception):
            self.converter.convert(files, FORMAT_ICO, tempfile.mkstemp('.ico')[1])
        with self.assertRaises(Exception):
            self.converter.convert(files, FORMAT_ICNS, tempfile.mkstemp('.icns')[1])

    def assertAllTargetFormatsSucceed(self, files):
        """``convert`` calls with any target format succeeds.

        :param files: File list to pass to the convert class.
        """

        for target_format, result_path in [
            (FORMAT_ICO, tempfile.mkstemp('.ico')[1],),
            (FORMAT_ICNS, tempfile.mkstemp('.icns')[1],)
        ]:
            self.converter.convert(files, target_format, result_path)
            self.assertTrue(os.path.exists(result_path))
            self.assertTrue(os.path.isfile(result_path))
            self.assertGreater(os.path.getsize(result_path), 0)

            # deep icon validation (i.e., check the header values)
            self.assertTrue(self.converter.verify_generated_icon(target_format, result_path))

    def test_convert_empty_image_list(self):
        """Test conversion from an empty source.
        """

        self.assertAllTargetFormatsRaise(ValueError, [])

    def test_convert_invalid_format(self):
        """Test conversion given an invalid target icon format.
        """

        with self.assertRaises(ConversionError):
            self.converter.convert('foo', [
                os.path.join(ICONS_TEST_DIR, 'icon16x16.png'),
                os.path.join(ICONS_TEST_DIR, 'icon32x32.png')
            ],
                                   tempfile.mkstemp('.foo')[1])

    def test_convert_bad_local_pnglist(self):
        """Test conversion from bad local source.
        """

        self.assertAllTargetFormatsRaise(Exception, [
            os.path.join(ICONS_TEST_DIR, 'icon16x16.png'),
            os.path.join(ICONS_TEST_DIR, 'icon32x32.png'),
            '/foo.png'
        ])

    def test_convert_bad_remote_pnglist(self):
        """Test conversion from bad remote source.
        """

        self.assertAllTargetFormatsRaise(Exception, [
            'http://localhost:62010/www/icon16x16.png',
            'http://localhost:62010/www/foo.png',
            'http://localhost:62010/www/icon32x32.png'
        ])

    def test_convert_bad_png(self):
        """Test conversion of a 'bad' png.
        """

        self.assertAllTargetFormatsSucceed([
            os.path.join(ICONS_TEST_DIR, 'bad.png')
        ])

    def test_convert_local(self):
        """Test conversion from local source.
        """

        self.assertAllTargetFormatsSucceed([
            os.path.join(ICONS_TEST_DIR, 'icon16x16.gif'),
            os.path.join(ICONS_TEST_DIR, 'icon32x32.png')
        ])

    def test_convert_remote(self):
        """Test conversion from remote source.
        """

        self.assertAllTargetFormatsSucceed([
            'http://cdn1.iconfinder.com/data/icons/yooicons_set01_socialbookmarks/16/social_facebook_box_blue.png',
            'http://cdn1.iconfinder.com/data/icons/yooicons_set01_socialbookmarks/32/social_facebook_box_blue.png'
        ])

    def test_convert_MAS_iconset(self):
        """Test conversion of a complete MAS (Mac App Store) iconset.
        """

        self.assertAllTargetFormatsSucceed([
            os.path.join(ICONS_TEST_DIR, 'ttp/icon16x16.png'),
            os.path.join(ICONS_TEST_DIR, 'ttp/icon32x32.png'),
            os.path.join(ICONS_TEST_DIR, 'ttp/icon64x64.png'),
            os.path.join(ICONS_TEST_DIR, 'ttp/icon128x128.png'),
            os.path.join(ICONS_TEST_DIR, 'ttp/icon256x256.png'),
            os.path.join(ICONS_TEST_DIR, 'ttp/icon512x512.png'),
            os.path.join(ICONS_TEST_DIR, 'ttp/icon1024x1024.png'),
        ])

    def test_invalid_icns_size_iconsets(self):
        """Test conversion of invalid sized ICNS iconssets.
        """

        # todo: nonsquare iconsets

    def test_large_iconsets(self):
        """Test conversion of large iconssets.
        """

        # return

        # TODO: Get large iconsets where there are atleast 8 size icons for each.

    def test_random_iconsets(self):
        """Test conversion of random iconssets.
        """

        # get N random iconsets
        # using 1, 1000 inclusive for iconid
        random_iconsets = [random.randint(1, 1000) for _ in range(RANDOM_ICONSETS)]
        # TODO run the test
