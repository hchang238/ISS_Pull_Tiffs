import os
import json
import re

def line_to_key_values(line):
    key,value = line.split(":", maxsplit=1)
    return key, value.strip()

def remove_non_ascii(line):
    return ''.join([i if ord(i) < 128 and ord(i) > 0 else '' for i in line])


def lines_to_json(line_list):
    channels = [{"Channel": line.split(" ", maxsplit=1)[0]} for line in line_list if 20 * "*" in line and "Meta Data" in line]
    channel_names = [line.split(" ", maxsplit=1)[0] for line in line_list if 20 * "*" in line and "Meta Data" in line]
    line_dict = {"Channels": channels, "ChannelNames": channel_names}
    in_channel_section = False
    counter = 0
    
    for line in line_list:
        if "FileNumber" in line:
            key, value = line_to_key_values(line)
            line_dict["SetFileNumbers"] = value.split(" ")
        elif not ":" in line:
            if 20 * "*" in line and "Meta Data" in line:
                channel_dict = line_dict["Channels"][counter]
                channel_dict["FileNumber"] = line_dict["SetFileNumbers"][counter]
                in_channel_section = True
                counter += 1
            else:
                continue
        elif in_channel_section:
            key,value = line_to_key_values(line)
            channel_dict[key] = value
        else:
            key, value = line_to_key_values(line)
            line_dict[key] = value
    
    return line_dict



def sanitize_files(txt_path, json_dir_path):
    with open(txt_path, "r") as raw_metadata:
        sanitized_lines = [remove_non_ascii(line).strip() for line in raw_metadata if not len(line.strip()) == 0]
    raw_json = lines_to_json(sanitized_lines)
    
    json_path = json_dir_path + os.path.basename(txt_path).split(".")[0] + ".json"
    print(json_path)
    with open(json_path, "w") as sanitized_file:
        json.dump(raw_json, sanitized_file, ensure_ascii=True, indent=4)

if __name__ == "__main__":
    sanitize_files("../images/SPECTRUM/RGB brightfield/Uncropped tifs and metadata/Image03944_2019_06_07__12_11_18_RGB.txt", "../volumes/mysql/files/metadata/")
    #sanitize_files("../images/SPECTRUM/Monochrome RFP/Uncropped tifs and metadata/Image02340_2019_06_04__00_10_00_Mono.txt")