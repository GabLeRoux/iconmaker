# iconmaker

Tool for converting icons from GIF or PNG images to ICO or ICNS icon container formats.

## Usage

The `iconmaker` library provides a single class, `Converter` for dealing with conversions. Input files must be in either CompuServe GIF or PNG format.

## Installation

### Docker

```bash
docker build . -t you/iconmaker
```

## Software included

* [JasPer](https://github.com/mdadams/jasper) (enables full support for 256x256 and 512x512 32-bit icons with masks as alpha channels)  
  JasPer License Version 2.0
* [licnslib](https://icns.sourceforge.io/) (for png to icns conversion)  
  libicns is distributed under the Lesser GNU public license, Version 2.1   
  icns2png, png2icns, and icontainer2png are distributed under the GNU public license, Version 2
* [ImageMagick](https://www.imagemagick.org/script/index.php) (for GIF to PNG and PNG to ICO conversion)  
  ImageMagick is free software delivered as a ready-to-run binary distribution or as source code that you may use, copy, modify, and distribute in both open and proprietary applications. It is distributed under a derived Apache 2.0 license.

## Install iconmaker

```bash
python setup.py install
```

## License

[The Apache Software License, Version 1.1](LICENSE.txt)