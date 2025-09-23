#! /usr/bin/env python3

import re
import yaml
import logging
from typing import TypedDict, Literal, Dict, List, Tuple, Union, NamedTuple, Any
from copy import deepcopy

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class BaseRow(TypedDict, total=True):
    """
    Schema for a generic TSV row.

    These are the required columns present in all rows, representing the
    variable, type, description, and workflow. The columns in the output tsv file are a subset of
    the columns in the input tsv file, so these keys are always required.
    """
    Variable: str
    Type: str
    Description: str
    Workflow: str

class Row(BaseRow, total=False):
    """
    Schema for rows in both the input and output TSV files.

    Inherits the required keys from BaseRow. Additional keys (like task name,
    default value, Terra status, and classification) are optional, allowing
    this class to represent both input tsv rows (with extra columns) and output
    tsv rows (with only the base columns) using a single type.

    Expected structure: { 'Terra Task Name': ..., 'Variable': ..., ... }

    """
    Terra_Task_Name: str
    Default_Value: str
    Terra_Status: str
    Classification: str

class RowReports(NamedTuple):
    """
    Named tuple to hold lists of dictionaries representing different types of row updates.

    Attributes:
        partial_rows (List[Dict[str, str]]): List of partial row updates made.
        missing_rows (List[Dict[str, str]]): List of missing row updates added.
        extra_rows (List[Dict[str, str]]): List of extra row updates removed.
        unknown_rows (List[Dict[str, str]]): List of unknown row updates found.
    """
    partial_rows: List[Dict[str, str]]
    missing_rows: List[Dict[str, str]]
    extra_rows: List[Dict[str, str]]
    unknown_rows: List[Dict[str, str]]

# alias for the dictionary that maps workflow names (strings) to a list of Row dictionaries.
WorkflowRows = Dict[str, List[Row]]

def read_yaml(
    yaml_file: str,
) -> Dict[str, Any]:
    """
    Read a YAML file and return its contents.

    Args:
        yaml_file (str): The path to the YAML file.
    Returns:
        The contents of the YAML file as a dictionary.
    """
    logger.debug(f"Reading YAML file: {yaml_file}")
    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)

def phb_row_to_string(
    row: Row,
) -> str:
    """
    Convert a dictionary row to a tab-separated string.

    Args:
        row (Dict): The dictionary row to convert.
    Returns:
        The tab-separated string representation of the row.
    """
    return "\t".join(str(row[col]) for col in row.keys())

def phb_sort_dict(
    wf_dict: WorkflowRows,
) -> WorkflowRows:
    """
    Sort an input dictionary by workflow names (keys) and task name / variable name (values).

    Args:
        input_dict (Dict): The input dictionary to sort.
    Returns:
        The sorted dictionary.
    """
    copy_dict = deepcopy(wf_dict)
    return {
        wf: sorted(copy_dict[wf], key=lambda x: (x.get('Terra Task Name', ''), x.get('Variable', '')))
        for wf in sorted(copy_dict.keys())
    }

def phb_resolve_classifications(
    var_name: str,
    description: str,
) -> Literal["docker", "database", "reference", "runtime", "general"]:
    """
    Resolve classifications based on variable name and descriptions.

    Args:
        var_name (str): The variable name.
        description (str): The variable description.
    Returns:
        The string classification category.
    """
    return (
        "docker" if any(_ in var_name for _ in ["docker", "docker_image"]) and "internal component" not in description.lower() else
        "database" if any(_ in var_name for _ in ["db", "database"]) and "internal component" not in description.lower() else
        "reference" if any(_ in var_name for _ in ["_ref", "ref_", "reference"]) and "internal component" not in description.lower() else
        "runtime" if any(_ in var_name for _ in ["cpu", "disk", "disk_size", "_mem", "mem_", "memory"]) and "internal component" not in description.lower() else
        "general"
    )

def phb_resolve_defaults(
    default: Union[str, Dict[str, Any]],
) -> str:
    """
    Resolve complex default values, including handling of functions like sub, addition, and nested functions like basename.

    Args:
        default (str | dict): The default value to resolve.
            - If str: returned as-is.
            - If dict: expected structure { "func": ..., "args": [...] }.
    Returns:
        The resolved default value as a string.
    """
    # recursively parse nested basename functions
    def parse_basename_func(default):
        if isinstance(default, dict) and default.get('func') == "basename":
            base, exts = parse_basename_func(default['args'][0][0])
            exts += [default['args'][1][0]]
            return base, exts
        else:
            return default, []

    # basename function
    if isinstance(default, dict) and default.get('func') == "basename":
        base, exts = parse_basename_func(default)
        default = f"basename of {base} (without {', '.join(exts)})"

    # substitution function
    elif isinstance(default, dict) and default.get('func') == "sub":
        default = f"{default['args'][0][0]} where '{default['args'][1][0]}' is substituted with '{default['args'][2][0]}'"

    # addition function
    elif isinstance(default, dict) and default.get('func') == "_add":
        default = "".join([_[0] for _ in default['args']])

    # Note converting all default values into strings for consistency between dict and input tsv
    else:
        default = str(default) if default != None else ""

    return default

def phb_resolve_var_name(
    var_name: str,
) -> Union[Tuple[str, str], Tuple[None, None]]:
    """
    Resolve an input variable name and its associated workflow from the dict file

    Args:
        var_name (str): The input variable name from the dict file.
    Returns:
        Tuple[str, str]: A tuple containing the workflow name and the variable name (in that order).
    """
    parts = var_name.split('.')
    # variable is defined at the main workflow level
    if len(parts) == 1:
        return None, var_name
    # variable is defined at the task/subworkflow level
    elif len(parts) <= 2:
        return parts[0], parts[1]
    return None, None

def phb_resolve_descriptions(
    var_name: str,
) -> str:
    """
    Resolve descriptions based on variable.

    Args:
        var_name (str): The variable name.
    Returns:
        The resolved description.
    """
    common_descriptions = {
        ("cpu", ) : "Number of CPUs to allocate to the task",
        ("disk", "disk_size") : "Amount of storage (in GB) to allocate to the task",
        ("mem", "memory") : "Amount of memory (in GB) to allocate to the task",
        ("docker", "docker_image") : "Docker image to use for the task",
    }
    description = "DESCRIPTION"
    for keys, desc in common_descriptions.items():
        for k in keys:
            if k in var_name:
                description = desc
                break
    return description

def phb_parse_tsv(
    tsv_file: str,
) -> WorkflowRows:
    """
    Read input TSV file and return its contents.

    Args:
        tsv_file (str): The path to the TSV file.
    Returns:
        A dictionary mapping workflow display names to lists of dictionaries, where each inner dictionary represents an input variable and its associated metadata.
    """
    logger.debug(f"Parsing TSV file: {tsv_file}")
    with open(tsv_file, 'r', newline='') as f:
        rows = f.readlines()
        tsv_file_header = rows[0].strip().split('\t')

        tsv_dict = {}
        for row in rows[1:]:
            row = row.strip().split('\t')
            tsv_row = dict(zip(tsv_file_header, row))

            # Making default value column to be consistent with input dict defaults
            default_value = tsv_row.get('Default Value', '')
            tsv_row['Default Value'] = {"TRUE": "True", "FALSE": "False"}.get(default_value, default_value)

            # Clean up workflow names by removing any duplicates and sorting them
            workflow_list = sorted(set(wf.strip() for wf in tsv_row.get('Workflow', '').split(',')))
            tsv_row['Workflow'] = ', '.join(workflow_list)

            # Only keep columns that exist in this row
            tsv_row = {k: v for k, v in tsv_row.items() if k in tsv_file_header}

            # Populate tsv_dict with all workflows that use this input variable
            for wf in workflow_list:
                if wf not in tsv_dict:
                    tsv_dict[wf] = []
                tsv_dict[wf].append(tsv_row)

        # sort by keys, and by terra task name/variable name
        tsv_dict = phb_sort_dict(tsv_dict)
    return tsv_dict

def phb_write_tsv(
    wf_dict: WorkflowRows,
    output_file: str = "all_inputs_sorted.tsv",
) -> None:
    """
    Write a dictionary to a TSV file.
    Expected structure: { "Workflow Name": [ { "Terra Task Name": ..., "Variable": ..., ...}, ... ], ... }
    Args:
        wf_dict (WorkflowRows): The workflow dictionary to write.
        output_file (str): The path to the output TSV file.
    """
    # Duplicate entries can exist in this dictionary because multiple workflows can use the same input variable.
    # The 'Workflow' column in this dictionary will contain a comma-separated list of all workflows that use that input,
    # So we only want to write unique rows once.
    existing_rows = {}
    first_row = next(iter(next(iter(wf_dict.values()))))
    tsv_file_header = list(first_row.keys())
    logger.debug(f"Writing TSV file: {output_file} with header: {tsv_file_header}")

    with open(output_file, 'w') as f:
        f.write("\t".join(tsv_file_header) + "\n")
        for wf_name, rows in wf_dict.items():
            for row in rows:
                row_sans_wf = phb_row_to_string({k: v for k, v in row.items() if k != 'Workflow'})
                wf_list = sorted(set(wf.strip() for wf in row.get('Workflow', '').split(',')))
                wf_string = ', '.join(wf_list)

                if row_sans_wf not in existing_rows:
                    existing_rows[row_sans_wf] = row
                else:
                    # If the row already exists, append the workflow name to the existing row's 'Workflow' column
                    if wf_string != existing_rows[row_sans_wf]['Workflow']:
                        new_wf_list = sorted(set([wf.strip() for wf in existing_rows[row_sans_wf]['Workflow'].split(',')] + wf_list))
                        existing_rows[row_sans_wf]['Workflow'] = ', '.join(new_wf_list)
        for row in existing_rows.values():
            print(phb_row_to_string(row), file=f)

def phb_get_wf_display_name(
    dockstore_yaml_file: str,
) -> Dict[str, str]:
    """
    Parse the dockstore yaml to create a mapping of workflow file paths to display names.

    Args:
        dockstore_yaml_file (str): The path to the dockstore yaml file.
    Returns:
        A dictionary mapping workflow file paths to workflow display names.
    """
    logger.debug(f"Parsing Dockstore YAML file: {dockstore_yaml_file}")

    wf_alias_map = {} # { "file_path" : "Workflow/Display Name"}

    # Structure of dockstore_yaml dictionary:
    # { 'version': ..., 'workflows': [ { 'name': ..., 'subclass': ..., 'primaryDescriptorPath': ..., 'testParameterFiles': [...] }, ... ]}
    dockstore_yaml = read_yaml(dockstore_yaml_file)

    for wf in dockstore_yaml["workflows"]:
        # this next part should be removed and the dockstore yaml should be updated so we don't have to do this.
        # or the "Workflow" column in `all_inputs.tsv` should match the display names in the dockstore yaml.
        display_name = re.sub(r'_PHB$', '', wf["name"])
        fp = wf["primaryDescriptorPath"][1:] # removes leading "/"
        if display_name == "NCBI-AMRFinderPlus":
            display_name = "AMRFinderPlus"
        if display_name == "Kraken2_ONT":
            display_name = "Kraken_ONT"
        if display_name == "Kraken2_PE":
            display_name = "Kraken_PE"
        if display_name == "Kraken2_SE":
            display_name = "Kraken_SE"
        if display_name == "Gambit_Core":
          continue

        wf_alias_map[fp] = display_name
    wf_alias_map["workflows/utilities/wf_host_decontaminate.wdl"] = "Host_Decontaminate"
    return wf_alias_map

def phb_parse_io_dict(
    io_dict: Dict[str, Dict],
    wf_alias_map: Dict[str, str],
) -> Tuple[WorkflowRows, WorkflowRows]:
    """
    Parse the I/O dictionary of all inputs/outputs with their associated workflows.

    Args:
        io_dict (str): The I/O dictionary generated from Bioblueprint workflow parsing.
        wf_alias_map (dict): A dictionary mapping workflow file paths to workflow display names.

    Returns:
        A dictionary mapping workflow display names to lists of dictionaries, where each inner dictionary represents an input variable and its associated metadata.
        A dictionary mapping workflow display names to lists of dictionaries, where each inner dictionary represents an output variable and its associated metadata.
    """
    input_dict = {}
    output_dict = {}
    logger.debug(f"Parsing IO Dictionary")
    for wf_wdl_name, info in io_dict.items():
        path = info['path']
        inputs = info['inputs']
        outputs = info['outputs']

        # If the workflow is not hosted on dockstore or no longer used, set the display name to nothing. Will be removed later.
        wf_display_name = wf_alias_map.get(path, "")
        input_dict[wf_display_name] = []
        output_dict[wf_display_name] = []

        # Parse inputs first
        logger.debug(f"Parsing inputs: {wf_wdl_name} with path: {path} and display name: {wf_display_name}")
        for var_name, attribute in inputs.items():
            # Terra only considers the first 3 levels of workflow inputs, skip if variable is too deeply nested
            if len(var_name.split('.')) > 2:
                continue

            # variable is defined at the task/subworkflow level
            terra_task_name, var_name = phb_resolve_var_name(var_name)

            # variable is defined at the main workflow level
            if terra_task_name is None:
                terra_task_name = wf_wdl_name

            var_type = attribute['type'].split("?")[0]
            description = phb_resolve_descriptions(var_name)
            default = phb_resolve_defaults(attribute['default'])
            status = "Required" if ((attribute['default'] == None) and ("?" not in attribute['type'])) else "Optional"
            classification = phb_resolve_classifications(var_name, description)

            input_dict[wf_display_name].append(
                {
                    'Terra Task Name': terra_task_name,
                    'Variable': var_name,
                    'Type': var_type,
                    'Description': description,
                    'Default Value': default,
                    'Terra Status': status,
                    'Workflow': wf_display_name,
                    'Classification': classification
                }
            )

        # Parse outputs
        logger.debug(f"Parsing outputs: {wf_wdl_name} with path: {path} and display name: {wf_display_name}")
        for var_name, var_type in outputs.items():
            output_dict[wf_display_name].append(
                {
                    'Variable': var_name,
                    'Type': var_type.split("?")[0],
                    'Description': "DESCRIPTION",
                    'Workflow': wf_display_name
                }
            )

    # sort by keys, and by terra task name/variable name
    return phb_sort_dict(input_dict), phb_sort_dict(output_dict)


def phb_check_row_equality(
    dict_row: Row,
    tsv_row : Row,
) -> Dict[str, bool]:
    """
    Calculate equality metrics between a tsv row and a dict row

    Args:
        dict_row (dict): A dictionary representing a row from the dict file.
        tsv_row (dict): A dictionary representing a row from the TSV file.

    Returns:
        dict: A dictionary containing boolean values for each attribute comparison.
    """

    equalities = {
        "Terra Task Name": (
            tsv_row.get('Terra Task Name') == dict_row.get('Terra Task Name')
        ),
        "Variable": (
            tsv_row.get('Variable') == dict_row.get('Variable')
        ),
        "Type": (
            tsv_row.get('Type') == dict_row.get('Type')
        ),
        "Default Value": (
            (tsv_row.get('Default Value') == dict_row.get('Default Value')) or
            (tsv_row.get('Default Value') is not None and not dict_row.get('Default Value'))
        ),
        "Terra Status": (
            dict_row.get('Terra Status', '') in tsv_row.get('Terra Status', '')
        ),
        "Workflow": (
            any([dict_row.get('Workflow') == _.strip() for _ in tsv_row.get('Workflow').split(',')])
        )
    }

    valid_attributes = []
    # Remove keys that don’t exist in either row
    for key in list(equalities.keys()):
        if key not in tsv_row or key not in dict_row:
            equalities.pop(key)
        else:
            valid_attributes.append(key)

    equalities['exact_match'] = all(equalities[k] for k in valid_attributes if k in equalities)

    # There's probably a cleaner way to do this, but this works for now.
    if "Terra Task Name" in valid_attributes:
        # Dealing with input tsv rows
        equalities['partial_match'] = (
            # Case 1: Task + Var + Workflow all match -> confidently resolve any mixture of type, default, status mismatches
            (equalities['Terra Task Name'] and equalities['Variable'] and equalities['Workflow'])
            or
            # Case 2: Task + Var match -> we can't confidently say it's not a new input unless only one attribute is different
            (
                equalities['Terra Task Name']
                and equalities['Variable']
                and sum([
                    not equalities['Type'],
                    not equalities['Default Value'],
                    not equalities['Terra Status'],
                    not equalities['Workflow'],
                ]) == 1
            )
        )
    else:
        # Dealing with output tsv rows
        # only one attribute can be different for a partial match otherwise consider it a new output
        equalities['partial_match'] = (
            all([
                equalities['Variable']
            ]) and sum([
                not equalities['Type'],
                not equalities['Workflow'],
            ]) == 1
        )

    return equalities

def phb_update_io(
    i_or_o_dict: WorkflowRows,
    tsv_dict: WorkflowRows,
) -> Tuple[WorkflowRows, RowReports]:
    """
    Update the input variables in the I/O tsv file based on differences found in the dict input dictionary.

    Args:
        i_or_o_dict (dict): From the input dict file. Dictionary mapping workflow display names to a list of dictionaries containing input variables and their metadata.
        tsv_dict (dict): From the IO input tsv file. Dictionary mapping workflow display names to a list of dictionaries containing input variables and their metadata.

    Returns:
        dict: The updated dictionary of valid inputs for all workflows.
        RowReports: A named tuple containing lists of dictionaries representing different types of I/O updated rows.
    """
    partial_rows, missing_rows, extra_rows, unknown_rows = [], [], [], []
    row_reports = RowReports(partial_rows, missing_rows, extra_rows, unknown_rows)

    # Creates a copy AND sorts dictionary
    # Remaining dict will be used to track inputs that need to be removed from the final updated_dict
    dict_remaining_dict = phb_sort_dict(i_or_o_dict)
    tsv_remaining_dict = phb_sort_dict(tsv_dict)

    # This will be the final updated dictionary that is returned at the end
    updated_dict = phb_sort_dict(tsv_dict)

    # Flatten both input dictionaries into lists of tuples for easier comparison
    # Ignore wf entries that are most likely subworkflows. We only want to report/document the ones that show up in Terra.
    dict_list = [(wf, row) for wf, rows in i_or_o_dict.items() for row in rows if row.get('Workflow')]
    tsv_list = [(wf, row) for wf, rows in tsv_dict.items() for row in rows if row.get('Workflow')]

    # First pass: check for exact matches between dict and TSV rows
    # Note that dict_row['Workflow'] will only have one workflow name
    logger.debug(f"Starting first pass: checking for exact matches between {len(dict_list)} dict rows and {len(tsv_list)} TSV rows")
    for dict_wf_name, dict_row in dict_list:
        for tsv_wf_name, tsv_row in tsv_list:
            if dict_wf_name == tsv_wf_name:
                # Check for exact match and mark as found by removing row from remaining_dict
                equalities = phb_check_row_equality(dict_row, tsv_row)
                if equalities['exact_match']:
                    if tsv_row in tsv_remaining_dict.get(tsv_wf_name, []):
                        tsv_remaining_dict[tsv_wf_name].remove(tsv_row)
                    if dict_row in dict_remaining_dict.get(dict_wf_name, []):
                        dict_remaining_dict[dict_wf_name].remove(dict_row)
                    break

    # After processing all exact matches, whatever is left in remaining_dicts are extras that need to be resolved/removed
    # Flatten remaining_dicts into a lists of tuples for easier comparison
    dict_remaining_list = sorted(
        [(wf, row) for wf, rows in dict_remaining_dict.items() for row in rows if row.get('Workflow')],
        key=lambda x: (x[1].get("Terra Task Name", ""), x[1].get("Variable", ""), x[0])
    )
    tsv_remaining_list = sorted(
      [(wf, row) for wf, rows in tsv_remaining_dict.items() for row in rows if row.get('Workflow')],
      key=lambda x: (x[1].get("Terra Task Name", ""), x[1].get("Variable", ""), x[0])
    )

    logger.debug(f"Exact matches: {len(tsv_list) - len(tsv_remaining_list)}")
    logger.debug(f"Remaining: {len(dict_remaining_list) + len(tsv_remaining_list)}")

    # Second pass: check for partial matches and missing inputs between dict and non-exact-matching TSV rows
    logger.debug(f"Starting second pass: checking for partial matches between {len(dict_remaining_list) + len(tsv_remaining_list)} non-matching TSV rows")
    for dict_wf_name, dict_row in dict_remaining_list:
        for tsv_wf_name, tsv_row in tsv_remaining_list:
            # Check for partial match (across all workflows) and update fields that are incorrect/don't match
            # Mark partial matches as found by removing row from remaining_dict
            equalities = phb_check_row_equality(dict_row, tsv_row)
            if equalities['partial_match']:

                # Which row needs to be updated?
                row_index = tsv_dict[tsv_wf_name].index(tsv_row)

                # What type of partial match is it? Can only be one attribute that is different. "Default Value", "Type", "Terra Status", or "Workflow"
                valid_partial_attributes = [attr for attr in tsv_row.keys() if equalities.get(attr) == False]
                for attr in valid_partial_attributes:
                    old_row = phb_row_to_string(updated_dict[tsv_wf_name][row_index])
                    # Append workflow name to existing comma-separated list of workflows if not already present
                    if attr == "Workflow":
                        updated_dict[tsv_wf_name][row_index][attr] = ', '.join(sorted(set(_.strip() for _ in tsv_row['Workflow'].split(',') + [dict_wf_name])))
                        title = "Added Missing Workflow"
                    else:
                        updated_dict[tsv_wf_name][row_index][attr] = dict_row[attr]
                        title = f"Updated {attr}"
                    new_row = phb_row_to_string(updated_dict[tsv_wf_name][row_index])
                    row_reports.partial_rows.append(
                        {
                            "title": title,
                            "workflow": dict_wf_name,
                            "old_row": old_row,
                            "new_row": new_row
                        }
                    )
                if tsv_row in tsv_remaining_dict.get(tsv_wf_name, []):
                    tsv_remaining_dict[tsv_wf_name].remove(tsv_row)
                if dict_row in dict_remaining_dict.get(dict_wf_name, []):
                    dict_remaining_dict[dict_wf_name].remove(dict_row)
                break

    # Grab remaining counts for logging
    num_dict_remaining = len(dict_remaining_list)
    num_tsv_remaining = len(tsv_remaining_list)

    # Flatten remaining_dict into a list of tuples for easier comparison
    dict_remaining_list = sorted(
        [(wf, row) for wf, rows in dict_remaining_dict.items() for row in rows if row.get('Workflow')],
        key=lambda x: (x[1].get("Terra Task Name", ""), x[1].get("Variable", ""), x[0])
    )
    tsv_remaining_list = sorted(
      [(wf, row) for wf, rows in tsv_remaining_dict.items() for row in rows if row.get('Workflow')],
      key=lambda x: (x[1].get("Terra Task Name", ""), x[1].get("Variable", ""), x[0])
    )

    logger.debug(f"Partial matches: {(num_dict_remaining - len(dict_remaining_list)) + (num_tsv_remaining - len(tsv_remaining_list))}")
    logger.debug(f"Remaining: {len(dict_remaining_list) + len(tsv_remaining_list)}")

    # After processing all partial matches, whatever is left in dict_remaining_dict are rows that need to be added as they are new inputs without a match.
    logger.info(f"Missing rows: {len(dict_remaining_list)} will be added.")
    for dict_wf_name, dict_row in dict_remaining_list:
        row_reports.missing_rows.append(
            {
                "title": f"Added New Row",
                "workflow": dict_wf_name,
                "old_row": "",
                "new_row": phb_row_to_string(dict_row)
            }
        )
        updated_dict.setdefault(dict_wf_name, []).append(dict_row)

    # After processing all partial matches, whatever is left in tsv_remaining_dict are extra rows that need to be removed as they have no match.
    logger.debug(f"Extra rows: {len(tsv_remaining_list)} will be removed.")

    # Also remove any invalid/unpublished rows where the workflow is not hosted on dockstore or no longer used.
    invalid_wf_list = [
      (wf, row) for wf, rows in tsv_dict.items() for row in rows if (
        (wf not in i_or_o_dict) and
        ((wf, row) not in tsv_remaining_list)
      )
    ]
    logger.debug(f"Invalid rows: {len(invalid_wf_list)} will be removed.")

    tsv_remaining_list = tsv_remaining_list + invalid_wf_list
    tsv_remaining_list = sorted(tsv_remaining_list, key=lambda x: (x[1].get('Terra Task Name', ''), x[1].get('Variable', ''), x[0]))

    logger.info(f"Total: {len(tsv_remaining_list)} extra rows and invalid rows will be removed.")

    for tsv_wf_name, tsv_row in tsv_remaining_list:
        row_index = tsv_dict[tsv_wf_name].index(tsv_row)
        workflow_list = sorted(set(wf.strip() for wf in updated_dict[tsv_wf_name][row_index].get('Workflow', '').split(',')))

        old_row = phb_row_to_string(updated_dict[tsv_wf_name][row_index])
        # If the extra input variable is linked to multiple workflows (comma-separated), remove only the specified workflow so valid inputs remain.
        # Otherwise, remove the entire input/row.
        if len(workflow_list) > 1:
            workflow_list.remove(tsv_wf_name)
            updated_dict[tsv_wf_name][row_index]['Workflow'] = ', '.join(workflow_list)
            title = "Removed Extra Workflow"
            new_row = phb_row_to_string(updated_dict[tsv_wf_name][row_index])
        else:
            updated_dict[tsv_wf_name][row_index] = {}
            title = "Removed Extra Row"
            new_row = ""

        row_reports.extra_rows.append(
            {
                "title": title,
                "workflow": tsv_wf_name,
                "old_row": old_row,
                "new_row": new_row
            }
        )
    # Remove any empty rows that were marked for deletion
    updated_dict = {wf: [row for row in rows if row] for wf, rows in updated_dict.items()}
    logger.debug(f"Final I/O count in the updated TSV file: {sum(len(v) for v in updated_dict.values())}")

    # Track inputs with missing/unknown wf_display_name (from unused or non-Dockstore workflows).
    # Safe to ignore since they are auto-generated and don't currently exist in the final I/O tsv file.
    # Could help debug future issues with workflow display name mapping mishaps.
    unknown_dict = i_or_o_dict.get('', [])
    if unknown_dict:
        for row in unknown_dict:
            row_reports.unknown_rows.append(
                {
                    "title": "Unknown Workflow",
                    "workflow": "N/A",
                    "old_row": phb_row_to_string(row),
                    "new_row": phb_row_to_string(row)
                }
            )
    logger.info(f"Found {len(unknown_dict)} inputs linked to unknown/missing workflows that will be ignored.")

    # One last sort before returning
    updated_dict = phb_sort_dict(updated_dict)

    return updated_dict, row_reports

def phb_generate_report(
    row_reports: RowReports,
    output_file: str = "io_changelog.tsv",
) -> None:
    """
    Generate a report of changes made to all I/O variables.

    Args:
        row_reports (RowReports): A named tuple containing lists of dictionaries representing different types of I/O updated rows.
        output_file (str, optional): Path to the output file. Defaults to "io_changelog.tsv".
    """
    logger.debug(f"Generating report of changes to I/O variables: {output_file}")
    with open(output_file, 'w', newline='') as f:

        update_list = [
          row_reports.partial_rows,
          row_reports.missing_rows,
          row_reports.extra_rows,
          row_reports.unknown_rows,
        ]

        for update_type in update_list:
            for results_dict in update_type:
                print(f"[{results_dict['title']}] in [{results_dict['workflow']}]:", file=f)
                print(f"From: {results_dict['old_row']}", file=f)
                print(f"To:   {results_dict['new_row']}", file=f)
                print("", file=f)
            print("", file=f)
            print("---------------------------------------------------------------------------------", file=f)
            print("", file=f)

def main(
    io_dict: str,
    input_tsv_file: str,
    output_tsv_file: str,
    dockstore_yaml_file: str,
    out_dir: str,
    out_prefix: str,
):
    # Read in the dockstore yaml to create a mapping of workflow file paths to display names
    wf_alias_map = phb_get_wf_display_name(dockstore_yaml_file)

    input_dict, output_dict = phb_parse_io_dict(io_dict, wf_alias_map)

    # Parse and update input variables first
    logger.info(f'Updating {input_tsv_file}')
    tsv_input_dict = phb_parse_tsv(input_tsv_file)
    updated_input_dict, input_row_reports = phb_update_io(input_dict, tsv_input_dict)

    # Create the updated input tsv file and generate a report of changes made to input variables
    phb_write_tsv(updated_input_dict, output_file=f"{out_dir}{out_prefix}_inputs.tsv")
    phb_generate_report(input_row_reports, output_file=f"{out_dir}{out_prefix}_inputs_changelog.tsv")

    # Parse and update output variables next
    logger.info(f'Updating {output_tsv_file}')
    tsv_output_dict = phb_parse_tsv(output_tsv_file)
    updated_output_dict, output_row_reports = phb_update_io(output_dict, tsv_output_dict)
    # Create the updated output tsv file and generate a report of changes made to output variables
    phb_write_tsv(updated_output_dict, output_file=f"{out_dir}{out_prefix}_outputs.tsv")
    phb_generate_report(output_row_reports, output_file=f"{out_dir}{out_prefix}_outputs_changelog.tsv")