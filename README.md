# TranslateXML_MPAStoCAMSIMA

Convert MPAS Registry.xml to a CAM-SIMA namelist_definition file

## Usage

Help text:

```bash
$ ./registry_to_namelistdef_xml.py --help
usage: registry_to_namelistdef_xml.py [-h] registry [output]

Convert namelist options from a MPAS-A Registry.xml to CAM-SIMA namelist_definition_mpas_dycore.xml.

positional arguments:
  registry    Path to MPAS-A Registry.xml. [Required]
  output      Path to save output to. [Optional, Default: "./namelist_definition_mpas_dycore.xml"]

options:
  -h, --help  show this help message and exit
```

Example usage:

```bash
$ ./registry_to_namelistdef_xml.py ../MPAS-Model/src/core_atmosphere/Registry.xml namelist_default_mpas_dycore.xml
# Output omitted...
```
