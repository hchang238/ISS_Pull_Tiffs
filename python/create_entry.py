import os
import json
import re
from configparser import ConfigParser

def setup():
    config = ConfigParser()
    config.read("./settings.ini")
    print(config["images"]["extensions"])

def line_to_key_values(line):
    key,value = line.split(":", maxsplit=1)
    return key, value.strip()

def lines_to_json(line_list):
    line_dict = {}
    channels = []
    in_channel_section = False
    
    for line in line_list:
        if not ":" in line:
            # Channel divider. Looks eg. "Red Meta Data ********************"
            if 20 * "*" in line and "Meta Data" in line:
                channel_name = line.split(" ", maxsplit=1)[0]
                line_dict[channel_name] = {}
                line_dict[channel_name]["Channel"] = channel_name
                channels.append(channel_name)
                in_channel_section = True
            else:
                continue
        elif in_channel_section:
            key,value = line_to_key_values(line)
            line_dict[channel_name][key] = value
        else:
            key,value = line_to_key_values(line)
            line_dict[key] = value
        
    line_dict["Channels"] = channels
    return line_dict

def remove_non_ascii(line):
    return ''.join([i if ord(i) < 128 and ord(i) > 0 else '' for i in line])

def sanitize_files(path):
    with open(path, "r") as raw_metadata:
        sanitized_lines = [remove_non_ascii(line).strip() for line in raw_metadata if not len(line.strip()) == 0]
    raw_json = lines_to_json(sanitized_lines)
    corrected_json = metadata_special_cases(raw_json)
    
    with open("test.json", "w") as sanitized_file:
        json.dump(corrected_json, sanitized_file, ensure_ascii=True, indent=4)
    
    #special cases
    
def metadata_special_cases(metadata_dict):
    filenumberkey = None
    for key in metadata_dict.keys():
        if "FileNumber" in key:
            files = metadata_dict[key].split(" ")
            metadata_dict[key] = files
            filenumberkey = key
            
    
    for i, channel in enumerate(metadata_dict["Channels"]):
        metadata_dict[channel]["FileNumber"] = files[i]

    metadata_dict["SetFileNumbers"] = metadata_dict.pop(filenumberkey)
    metadata_dict["Imagetype"] = filenumberkey.split("FileNumber")[0]

    return metadata_dict

"""
class MetadataFile:
    def __init__(self, path):
        self._path = path
    
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, pathstring):
        if os.path.isfile(pathstring):
            _, ext = os.path.splittext(pathstring)
            if ext.lower() in [".txt"]:

""" 
    
if __name__ == "__main__":
    sanitize_files("../images/SPECTRUM/RGB brightfield/Uncropped tifs and metadata/Image03944_2019_06_07__12_11_18_RGB.txt")
    #sanitize_files("../images/SPECTRUM/Monochrome RFP/Uncropped tifs and metadata/Image02340_2019_06_04__00_10_00_Mono.txt")