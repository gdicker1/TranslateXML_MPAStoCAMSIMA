#!/usr/bin/env python
'''
Convert namelist options contained in an MPAS-A Registry.xml to a
namelist_definition.xml suitable for CAM-SIMA
'''
import argparse
from pathlib import Path

def parse_args():
    '''
    Parse input arguments for Registry.xml location and desired output filename
    '''
    parser = argparse.ArgumentParser(description="Convert namelist options from a MPAS-A Registry.xml to CAM-SIMA namelist_definition.xml.")

    parser.add_argument('registry', help="Path to MPAS-A Registry.xml", type=str)
    parser.add_argument('output', nargs='?', help="Path to save output to.", type=str,
                        default=Path(Path.cwd(),"namelist_definition.xml"))
    opts = parser.parse_args()
    return Path(opts.registry), Path(opts.output)


def setup_files(registry_file,output_file):
    '''
    Open the Registry.xml for reading and the output_file for writing. Also
    perform any setup necessary for the output_file.
    '''
    r_handle = open(registry_file, 'w')
    o_handle = open(output_file, 'w')
    return r_handle, o_handle

def translate_registry_to_definition(registry_handle, output_handle):
    '''
    Parse through the registry file and translate to the correct format for the
    CAM-SIMA namelist_defintion.xml
    '''
    pass

def finish_files(reg_handle, out_handle):
    '''
    Finalize work with files: write to out_handle and close both
    '''
    reg_handle.close()
    out_handle.close()

if __name__ == "__main__":
    regfile, outfile = parse_args()
    reg_handle, out_handle = setup_files(regfile, outfile)

    translate_registry_to_definition(reg_handle, out_handle)

    finish_files(reg_handle, out_handle)