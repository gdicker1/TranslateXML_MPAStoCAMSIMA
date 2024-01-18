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
    parser = argparse.ArgumentParser(description="Convert namelist options from a MPAS-A Registry.xml to CAM-SIMA namelist_definition_mpas_dycore.xml.")

    def_opath="./namelist_definition_mpas_dycore.xml"

    parser.add_argument('registry', help="Path to MPAS-A Registry.xml. [Required]", type=str)
    parser.add_argument('output', nargs='?', help=f'Path to save output to. [Optional, Default: "{def_opath}"]', type=str,
                        default=Path(def_opath))
    opts = parser.parse_args()
    print(f'\tparse_args: opts={opts}')
    print(f'\tparse_args: {Path(opts.registry)}  {Path(opts.output)}')
    sys.stdout.flush()
    return Path(opts.registry).absolute().resolve(), Path(opts.output).absolute().resolve()


def setup_files(registry_file):
    '''
    Parse the Registry.xml and setup an ElementTree for the output_file
    
    Returns an ElementTree for the Parsed Registry.xml and a Element for the
    root of the output xml
    '''
    print(f"\tsetup_files: registry_file={registry_file}")
    print(f"\tsetup_files: Exists? {registry_file.exists()}")
    reg_tree = ElementTree()
    reg_tree.parse(registry_file)

    out_root =Element('entry_id_pg', version="0.1")
    comment = Comment(" MPAS dycore ")
    out_root.append(comment)
    out_tree = ElementTree(out_root)

    return reg_tree, out_tree

def translate_registry_to_definition(registry_handle, output_handle):
    '''
    Parse through the registry file and translate to the correct format for the
    CAM-SIMA namelist_defintion.xml
    '''
    print(f"\ttranslate_registry_to_def: reg_file root tag {registry_handle}")
    print(f"\ttranslate_registry_to_def: out_file root tag {output_handle.tag}")

    BAD_RECORDS=['io', 'IAU', 'development', 'physics']
    BAD_OPTIONS=['calendar_type', 'start_time', 'stop_time', 'run_duration', 'num_halos',
                 'number_of_blocks', 'explicit_proc_decomp','proc_decomp_file_prefix',
                 'do_DAcycling']
    BAD_OPTIONS=['config_'+bo for bo in BAD_OPTIONS]

    for record in registry_handle.iter('nml_record'):
        r_name = record.attrib['name']
        # If any record names match a BAD_RECORD, skip
        if any(br.casefold() == r_name.casefold() for br in BAD_RECORDS):
            print(f"\ttranslate_registry_to_def: Skipping record name={r_name}")
            continue
        for option in record.iter('nml_option'):
            o_name = option.attrib['name']
            # If any option name nearly matches a BAD_OPTION, skip
            if any(bo.casefold() in o_name.casefold() for bo in BAD_OPTIONS):
                print(f"\ttranslate_registry_to_def:\tSkipping option name={o_name} from {r_name}")
                continue
            print(f"\ttranslate_registry_to_def: option={tostring(option)}")
            add_CSelement(record, option, output_handle)
    return


def add_CSelement(record, option, o_element):
    '''
    Add an element from the Registry.xml to the CAM-SIMA xml
    '''
    cs_name = trans_names(option)
    cs_type = trans_types(option)
    cs_category = 'mpas'
    cs_group = record.attrib['name']
    cs_desc = trans_desc(option)
    cs_dval = option.attrib['default_value']

    entry = SubElement(o_element, "entry", {'id':cs_name})
    e_type = SubElement(entry, "type")
    e_type.text=cs_type
    e_category = SubElement(entry, "category")
    e_category.text=cs_category
    e_group = SubElement(entry, "group")
    e_group.text=cs_group
    e_desc = SubElement(entry, "desc")
    e_desc.text=cs_desc
    e_vals = SubElement(entry, "values")
    e_val = SubElement(e_vals, "value")
    e_val.text=cs_dval
    return



def trans_names(opt):
    '''
    Given a name from the MPAS-A Registry, convert it to the correct format for
    CAM-SIMA 
    '''
    reg_name = opt.attrib['name'].replace('config_', 'mpas_')
    # Remove repeated uses of "mpas_" (e.g. for config_mpas_cam_coef)
    if reg_name.count('mpas_') > 1:
        reg_name.removeprefix('mpas_')
    return reg_name


def trans_types(opt):
    '''
    Given a type from the MPAS-A Registry, convert it to the correct format for
    CAM-SIMA 
    '''
    reg_type = opt.attrib['type']
    VALID_TYPES=('character', 'integer', 'logical', 'real')
    if reg_type.casefold() == 'character':
        return 'char*256'
    elif any(t.casefold() == reg_type.casefold() for t in VALID_TYPES[1:]):
        # reg_type is one of the other valid types, just return it
        return reg_type
    else:
        print(f'ERROR: invalid type encountered in Registry.xml: {reg_type} not in {VALID_TYPES}')
        sys.exit(-1)


def trans_desc(opt):
    '''
    Given a description from the MPAS-A Registry, convert it to the correct
    format for CAM-SIMA 
    '''
    reg_desc1 = "\n" + wrap_desc(opt.attrib['description'] + " in MPAS.")
    reg_desc2 = "\n" + wrap_desc("Possible values: " + opt.attrib['possible_values'])
    reg_desc3 = wrap_desc("Default: " + opt.attrib['default_value']) + "\n" + " "*4
    return "\n".join((reg_desc1, reg_desc2, reg_desc3))


def wrap_desc(txt):
    '''
    Wrap text to 80 characters, indent each line by 6 spaces
    '''
    import textwrap
    indent=' '*6
    return textwrap.fill(txt, 80, initial_indent=indent, subsequent_indent=indent,
                         replace_whitespace=False, fix_sentence_endings=True)


def finish_files(reg_handle, out_handle, out_file):
    '''
    Finalize work with files: write to out_handle and close both
    '''
    with open(out_file,'w') as out_fh:
        pretty_str = xmltoprettystr(out_handle)
        print('\tfinish_files: XML to save: \n', pretty_str)
        out_fh.write(pretty_str)

    return

def xmltoprettystr(elem):
    '''
    Re-parse the elem given and return a string that will work for a "pretty"
    print
    '''
    e_str = ET.tostring(elem.getroot(), 'utf-8')
    tmp_xml = minidom.parseString(e_str)
    return tmp_xml.toprettyxml(indent=" "*2)


if __name__ == "__main__":
    regfile, outfile = parse_args()
    print(f"main: regfile={regfile}, outfile={outfile}")

    reg_handle, out_handle = setup_files(regfile)

    translate_registry_to_definition(reg_handle, out_handle.getroot())

    finish_files(reg_handle, out_handle, outfile)