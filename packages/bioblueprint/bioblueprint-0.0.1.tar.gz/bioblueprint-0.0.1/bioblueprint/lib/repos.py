#! /usr/bin/env python3

import re
import logging
import requests

# NEED to modify populate PR/create new function to enable editing existing PR
"""Repository interface and Repository-specific functions"""

logger = logging.getLogger(__name__)

def download_pr(owner, repo, pr_number):
    """Download a PR from GitHub and return its body text."""

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    response = requests.get(url)
    if response.status_code == 200:
        pr_data = response.json()
        return pr_data.get("body", "")
    else:
        raise Exception(f"Failed to fetch PR: {response.status_code} - {response.text}")


def define_phb_standards(phb_dir):
    """Define standardized paths for github.com/theiagen/public_health_bioinformatics"""
    pr_template_path = phb_dir + ".github/PULL_REQUEST_TEMPLATE/code.md"
    pr_pop_func = populate_phb_pr
    i_tsv_path = f'{phb_dir}docs/assets/tables/all_inputs.tsv'
    o_tsv_path = f'{phb_dir}docs/assets/tables/all_outputs.tsv'
    dockstore_path = f'{phb_dir}.dockstore.yml'
    return pr_template_path, pr_pop_func, i_tsv_path, o_tsv_path, dockstore_path


def populate_phb_pr(wf_dict,
                    task_dict,
                    io_diff_dict,
                    testing_dict,
                    pr_template):
    """Populate the PR template with the modified workflows, tasks, inputs, and outputs."""

    # populate the expected section headings
    wf_task_header = "## :zap: Impacted Workflows/Tasks"
    impact_section = "This PR may lead to different results in pre-existing outputs:"
    inputs_header = "### ➡️ Inputs"
    outputs_header = "### ⬅️ Outputs"
    testing_header = "## :test_tube: Testing"
    scenarios_header = "### Suggested Scenarios for Reviewer to Test"

    # initialize the PR and populate from last to first sections to preserve indices
    pr_list = pr_template.splitlines()

    # add the testing workflows that don't already exist
    test_index = pr_list.index(testing_header)
    entered_tests = set()
    if scenarios_header in pr_list:
        scenarios_index = pr_list.index(scenarios_header)
        for line in pr_list[test_index + 1:scenarios_index]:
            if line.strip().startswith(("- [ ]", "- [x]")):
                if line.strip().startswith("- [ ]"):
                    wf_name_prep = line.split("- [ ]")[1].strip()
                    complete = False
                else:
                    wf_name_prep = line.split("- [x]")[1].strip()
                    complete = True
                wf_name_prep1 = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', wf_name_prep)  # remove markdown links
                wf_data = wf_name_prep1.split(" ")  # remove any comments after the name
                wf_name = wf_data[0]
                if len(wf_data) > 1:
                    comment = " ".join(wf_data[1:])
                else:
                    comment = ""
                if wf_name in testing_dict:
                    testing_dict[wf_name]['complete'] = complete
                    if comment:
                        testing_dict[wf_name]['comment'] = comment
                    logger.debug(f"{wf_name} testing complete: {complete}, comment: {comment}")
                else:
                    testing_dict[wf_name] = {'complete': complete, 'comment': comment}
                entered_tests.add(wf_name)

    test_str = ""
    for x in testing_dict:
        if x not in entered_tests:
            test_str += f"- [ ] {x}\n"
            testing_dict[x]['complete'] = False  # add to dict
    if test_str:
        pr_list.insert(test_index + 1, test_str)

    # add the input/output changes
    # use the key to indicate the workflow/task
    in_str, out_str = "\n", "\n"
    for k, v in io_diff_dict.items():
        if v['added_inputs'] or v['removed_inputs']:
            in_str += f"\n<details>\n<summary>{k}</summary>\n\n"
            if v['added_inputs']:
                in_str += "\n".join(f"\t+ {x}" for x in v['added_inputs']) + "\n"
            if v['removed_inputs']:
                in_str += "\n".join(f"\t- {x}" for x in v['removed_inputs']) + "\n"
            in_str += "\n</details>\n"
        if v['added_outputs'] or v['removed_outputs']:
            out_str += f"\n<details>\n<summary>{k}</summary>\n\n"
            if v['added_outputs']:
                out_str += "\n".join(f"\t+ {x}" for x in v['added_outputs']) + "\n"
            if v['removed_outputs']:
                out_str += "\n".join(f"\t- {x}" for x in v['removed_outputs']) + "\n"
            out_str += "\n</details>\n"

    # remove I/O entries prior to population 
    in_index = pr_list.index(inputs_header)
    out_index = pr_list.index(outputs_header)
    for index in reversed(range(out_index + 1, test_index)):
        pr_list.pop(index)
    pr_list.insert(out_index + 1, out_str)
    for index in reversed(range(in_index + 1, out_index)):
        pr_list.pop(index)
    pr_list.insert(in_index + 1, in_str)

    # add the workflow/task changes
    wf_str = ""
    # use the key to indicate the type of change
    for k, v in wf_dict.items():
        if v:
            wf_str += "\n\n".join(f"{k} `{x}`" for x in v) + "\n\n"
    task_str = ""
    for k, v in task_dict.items():
        if v:
            task_str += "\n\n".join(f"{k} `{x}`" for x in v) + "\n\n"
    wf_task_index = pr_list.index(wf_task_header)
    # remove preexisting entries

    impact_index = [i for i, line in enumerate(pr_list) if line.strip().startswith(impact_section)][0]
    for index in reversed(range(wf_task_index + 1, impact_index)):
        pr_list.pop(index)

    # readd a line break, then add workflows before tasks
    pr_list.insert(wf_task_index + 1, "\n")
    if task_str:
        pr_list.insert(wf_task_index + 1, f"\n### Tasks\n{task_str}")
    if wf_str:
        pr_list.insert(wf_task_index + 1, f"\n### Workflows\n{wf_str}\n")
    
    return '\n'.join(pr_list), testing_dict