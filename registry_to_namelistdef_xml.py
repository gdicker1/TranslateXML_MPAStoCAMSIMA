#!/usr/bin/env python
'''
Convert namelist options contained in an MPAS-A Registry.xml to a
namelist_definition.xml suitable for CAM-SIMA
'''
import argparse
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment, tostring
from xml.dom import minidom


def parse_args():
    '''
    Parse input arguments for Registry.xml location and desired output filename
    '''
    parser = argparse.ArgumentParser(description="Convert namelist options from a MPAS-A Registry.xml to CAM-SIMA namelist_definition.xml.")

    parser.add_argument('registry', help="Path to MPAS-A Registry.xml", type=str)
    parser.add_argument('output', nargs='?', help="Path to save output to.", type=str,
                        default=Path(Path.cwd(),"namelist_definition.xml"))
    opts = parser.parse_args()
    print(f'\tparse_args opts={opts}')
    print(f'\tparse_args {Path(opts.registry)}  {Path(opts.output)}')
    sys.stdout.flush()
    return Path(opts.registry).absolute().resolve(), Path(opts.output).absolute()


def setup_files(registry_file):
    '''
    Parse the Registry.xml and setup an ElementTree for the output_file
    
    Returns an ElementTree for the Parsed Registry.xml and a Element for the
    root of the output xml
    '''
    print(f"\tsetup_files registry_file={registry_file}")
    sys.stdout.flush()
    print(f"Exists? {registry_file.exists()}")
    reg_tree = ElementTree()
    reg_tree.parse(registry_file)

    out_root = Element('entry_id_pg', version="0.1")
    comment = Comment(" MPAS dycore ")
    out_root.append(comment)

    return reg_tree, out_root

def translate_registry_to_definition(registry_handle, output_handle):
    '''
    Parse through the registry file and translate to the correct format for the
    CAM-SIMA namelist_defintion.xml
    '''
    pass

def finish_files(reg_handle, out_handle, out_file):
    '''
    Finalize work with files: write to out_handle and close both
    '''

    with open(out_file,'w') as out_fh:
        pretty_str = xmltoprettystr(out_handle)
        out_fh.write(pretty_str)

    return

def xmltoprettystr(elem):
    '''
    Re-parse the elem given and return a string that will work for a "pretty"
    print
    '''
    e_str = ET.tostring(elem, 'utf-8')
    tmp_xml = minidom.parseString(e_str)
    return tmp_xml.toprettyxml(indent="  ")


if __name__ == "__main__":
    regfile, outfile = parse_args()
    print(f"regfile={regfile}, outfile={outfile}")
    sys.stdout.flush()
    reg_handle, out_handle = setup_files(regfile)

    translate_registry_to_definition(reg_handle, out_handle)

    finish_files(reg_handle, out_handle, outfile)