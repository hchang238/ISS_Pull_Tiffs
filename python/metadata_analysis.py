import os
import re
import shutil
import pandas as pd
from datetime import datetime
from PIL import Image
import PIL

ACCEPTABLE_IMAGE_EXT = [".bmp", ".dip", ".jpeg", ".jpg", ".jpe", ".jp2"
                        ".png", ".pmb", ".ppm", ".sr", ".ras", ".tiff", ".tif"]
ACCEPTABLE_META_EXT = [".txt", ".csv", ".json"] # May expand to .xlsx or other file types later
STRIPCHAR = "\t\n\x0b\x0c\r\x1c\x1d\x1e\x1f\x00 \x85\xa0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000"
DEFAULT_REGEX = r"_\d{4}_\d{2}_\d{2}__\d{2}_\d{2}_\d{2}_" 
DEFAULT_TFORMAT = "_%Y_%m_%d__%H_%M_%S_"

class SpectrumMeta:
    def __init__(self, image_path=None, meta_path=None):
        self._image_path = image_path
        self._meta_path = meta_path
        #self._file_paths = {Imagepath:self._image_path, Metapath:self._meta_path} #update per every change in image/metapath
        self._dataframe = pd.DataFrame()
        self.dataframe = pd.DataFrame([{"Imagepath": None, "Imagefile": None, "Metapath": None, "Metafile": None}])

    @property
    def image_path(self):
        if self._image_path is None:
            return None
            #raise ValueError("Image path has not been assigned")
        elif os.path.isfile(self._image_path):
            return self._image_path
        else:
            raise ValueError("Program cannot find file: {}".format(self._image_path))
    
    @image_path.setter
    def image_path(self, new_path):
        if os.path.isfile(new_path):
            _, ext = os.path.splitext(new_path)
            if ext.lower() in ACCEPTABLE_IMAGE_EXT:
                self._image_path = new_path
                self._dataframe["Imagepath"] = new_path
                self._dataframe["Imagefile"] = os.path.basename(new_path)
            else:
                raise ValueError("File does not contain proper extension: {}".format(ACCEPTABLE_IMAGE_EXT))
        else:
            raise ValueError("Program cannot find file. Check to see if the path is valid and the file exists")
    
    def set_image_path(self, new_path):
        self.image_path = new_path

    @property
    def meta_path(self):
        if self._meta_path is None:
            return None
            #raise ValueError("Metadata path has not been assigned")
        elif os.path.isfile(self._meta_path):
            return self._meta_path
        else:
            raise ValueError("Program cannot find file: {}".format(self._image_path))
    
    @meta_path.setter
    def meta_path(self, new_path):
        if os.path.isfile(new_path):
            _, ext = os.path.splitext(new_path)
            if ext.lower() in ACCEPTABLE_META_EXT:
                self._meta_path = new_path
                self._dataframe["Metapath"] = new_path
                self._dataframe["Metafile"] = os.path.basename(new_path)
            else:
                raise ValueError("File does not contain proper extension: {}".format(ACCEPTABLE_META_EXT))
        else:
            raise ValueError("Program cannot find file. Check to see if the path is valid and the file exists")    

    def set_meta_path(self, new_path):
        self.meta_path = new_path

    @property
    def dataframe(self):
        return self._dataframe
          
    
    @dataframe.setter
    def dataframe(self, input_dataframe):
        if isinstance(input_dataframe, pd.DataFrame):
            self._dataframe = input_dataframe
            if not self.meta_path is None:
                self._dataframe["Metapath"] = self.meta_path
                self._dataframe["Metafile"] = os.path.basename(self.meta_path)
            else:
                self._dataframe["Metapath"] = float('NaN')
                self._dataframe["Metafile"] = float('NaN')
            if not self.image_path is None:
                self._dataframe["Imagepath"] = self.image_path
                self._dataframe["Imagefile"] = os.path.basename(self.image_path)
            else:
                self._dataframe["Imagepath"] = float('NaN')
                self._dataframe["Imagefile"] = float('NaN')                
        else:
            raise ValueError("Function parameter was not a Pandas DataFrame instance")   


    def set_dataframe(self, input_dataframe):
        self._dataframe = input_dataframe
    
    @property
    def datadict(self):
        if isinstance(self.dataframe, pd.DataFrame):
            return self.dataframe.to_dict(orient="index")[0]
        else:
            return None

    def imagefile_datetime(self, regex=DEFAULT_REGEX, time_format=DEFAULT_TFORMAT):
        if self.image_path is None:
            raise ValueError("Metadata file has not been defined")
        image_basename = os.path.basename(self.image_path)
        prog = re.compile(regex)
        match = prog.search(image_basename)
        if match:
            datetime_string = match.group(0)
            return datetime.strptime(datetime_string, time_format)
    
    def metafile_datetime(self, regex=DEFAULT_REGEX, time_format=DEFAULT_TFORMAT):
        if self.meta_path is None:
            raise ValueError("Metadata file has not been defined")
        metafile_basename = os.path.basename(self.meta_path)
        prog = re.compile(regex)
        match = prog.search(metafile_basename)
        if match:
            datetime_string = match.group(0)
            return datetime.strptime(datetime_string, time_format)
    
    def input_datetime(self, input_str, regex=DEFAULT_REGEX, time_format=DEFAULT_TFORMAT):
        prog = re.compile(regex)
        match = prog.search(input_str)
        if match:
            datetime_string = match.group(0)
            return datetime.strptime(datetime_string, time_format)

    def parse_meta_txt(self, delimiter=":", omitlist=["Mono Meta Data", "Time"], strip_char=STRIPCHAR, datetime_info="filename"):
        if self.meta_path is None:
            raise ValueError("Metadata file has not been defined")
        with open(self.meta_path, 'r') as raw_metadata:
            data = []
            for line in raw_metadata:
                if not line.strip():
                    continue
                if any(words in line for words in omitlist):
                    continue
                else:
                    stripped_line = line.strip(strip_char)
                    line_pairs = stripped_line.split(delimiter)
                    if len(line_pairs) == 2:
                        line_pairs = [entry.strip(strip_char) for entry in line_pairs]
                        data_pair = tuple(line_pairs)
                        data.append(data_pair)
        data_dict = [dict(data)]
        return pd.DataFrame(data_dict)

    def parse_meta_csv(self, *args, **kwargs):
        if self.meta_path is None:
            raise ValueError("Metadata file has not been defined")
        df = pd.read_csv(self.meta_path, *args, **kwargs)
        return df
    
    def parse_meta_json(self, *args, **kwargs):
        if self.meta_path is None:
            raise ValueError("Metadata file has not been defined")
        df = pd.read_json(self.meta_path,*args, **kwargs)
        return df

    def _dsc_finalize_dataframe(funct):
        def modify_dataframe(self, timestamp_source="imagefile", time_label="Timestamp", regex=DEFAULT_REGEX, time_format=DEFAULT_TFORMAT, *args, **kwargs):
            if self.meta_path is None and self.image_path is None:
                raise ValueError("Image and metadata paths are not set")
            elif self.meta_path is None:
                raise ValueError("Metadata path not set")
            funct(self, *args,**kwargs)
            df = self.add_timestamp(timestamp_source, time_label, regex, time_format)
            return df
        return modify_dataframe

    @_dsc_finalize_dataframe
    def read_meta_csv(self, *args, **kwargs):
        self.dataframe = pd.read_csv(self.meta_path, *args, **kwargs)
        return self.dataframe
    
    @_dsc_finalize_dataframe
    def read_meta_json(self, *args, **kwargs):
        self.dataframe = pd.read_json(self.meta_path, *args, **kwargs)
        return self.dataframe

    @_dsc_finalize_dataframe
    def read_meta_txt(self, *args, **kwargs):
        self.dataframe = self.parse_meta_txt(*args, **kwargs)
        return self.dataframe
    
    def add_timestamp(self, timestamp_source="imagefile", time_label="Timestamp", regex=DEFAULT_REGEX, time_format=DEFAULT_TFORMAT):
        if timestamp_source == "imagefile":
            filename_timestamp = self.imagefile_datetime(regex, time_format)
            if filename_timestamp is None:
                self.dataframe.insert(0, time_label, float("NaN"))
            else:
                self.dataframe.insert(0, time_label, filename_timestamp)
        elif timestamp_source == "metafile":
            filename_timestamp = self.metafile_datetime(regex, time_format)
            if filename_timestamp is None:
                self.dataframe.insert(0, time_label, float("NaN"))
            else:
                self.dataframe.insert(0, time_label, filename_timestamp)
        elif timestamp_source:
            input_timestamp = self.input_datetime(timestamp_source, regex, time_format)
            if input_timestamp is None:
                self.dataframe.insert(0, time_label, float("NaN"))
            else:
                self.dataframe.insert(0, time_label, input_timestamp)
        return self.dataframe

    def _dsc_change_image(funct):
        def modify_imagetype(self, dest_path, *args, **kwargs):
            if self.image_path is None:
                raise ValueError("Image path is not set")
            dest_path = dest_path + "/" + os.path.basename(self.image_path).split(".", 1)[0]
            saved_path, label = funct(self, dest_path, *args,**kwargs)
            self.dataframe.insert(len(self.dataframe.columns), label + "path", saved_path)
            self.dataframe.insert(len(self.dataframe.columns), label + "file", os.path.basename(saved_path))
            return dest_path
        return modify_imagetype
    
    @_dsc_change_image
    def image_to_jpg(self, dest_path, label="JPEG", jpeg_quality=70, scale_percent=100):
        dest_path += ".jpg"
        image = PIL.Image.open(self.image_path)
        width = int(image.size[0] * scale_percent / 100)
        height = int(image.size[1] * scale_percent / 100)
        dim = (width, height)
        image = image.resize(dim)
        image.mode = 'I'
        image.point(lambda i:i*(1./256)).convert('L').save(dest_path)
        return (dest_path, label)