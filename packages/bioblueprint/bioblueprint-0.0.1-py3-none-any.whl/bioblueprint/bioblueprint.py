#! /usr/bin/env python3

# NEED to make it so graph nodes are specific to a file + task/workflow, not a task/workflow name
# will require modifying wdl.py during graph construction to identify the path of the nodes
# then reexpose the attribute errors that account for duplicate names/remove altogether
# NEED to parse diffs to identify the task that was changed, not using the whole file

# BEYOND MVP
# NEED to incorporate conditional parsing to link I/O modifications to more refined testing paths

import re
import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from lib.wdl import compile_repo, parse_wdl
from lib.graph import obtain_graph_paths
from git import Repo
from lib.repos import download_pr, define_phb_standards
from tools.update_io import main as phb_update_io

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def prep_output_dir(out_dir=None):
    """Prepare an output directory"""
    if out_dir:
        clean_dir = str(Path(out_dir).resolve())
    else:
        cur_time = datetime.now().strftime('%Y%m%d')
        clean_dir = f'{os.getcwd()}/bioblueprint_{cur_time}/'
    if not os.path.isdir(clean_dir):
        os.mkdir(clean_dir)
    return clean_dir


def prep_output_prefix(input_path, suffix):
    """Prepare the output base path"""
    out_base = input_path
    if input_path.endswith("/"):
        out_base = out_base[:-1]
    out_base = os.path.basename(re.sub(suffix + r"$", "", out_base))
    return out_base


def initialize_bioblueprint():
    parser = argparse.ArgumentParser(
        description="BioBlueprint workflow dependency compiler and automation"
    )

    in_par = parser.add_argument_group("Input parameters")
    in_par.add_argument(
        "-i", "--input", help="Local Git repository directory", required=True
    )
    in_par.add_argument(
        "-p", "--prefix", help='Workflow prefix; DEFAULT: "wf_"', default="wf_"
    )
    in_par.add_argument(
        "-s", "--suffix", help='Language suffix; DEFAULT: ".wdl"', default=".wdl"
    )

    git_par = parser.add_argument_group("Git parameters")
    git_par.add_argument(
        "-db", "--derived_branch", help="Derived branch name; DEFAULT: active branch"
    )
    git_par.add_argument(
        "-sb",
        "--source_branch",
        help='Source branch name; DEFAULT: "main"',
        default="main",
    )

    repo_par = parser.add_argument_group("Repository parameters")
    repo_par.add_argument(
        "-o",
        "--owner",
        help="GitHub repository owner; DEFAULT: theiagen",
        default="theiagen"
    )
    repo_par.add_argument(
        "-r",
        "--repository",
        help="GitHub repository name; DEFAULT: basename of -i/--input",
    )
    repo_par.add_argument(
        "-pr",
        "--pull_request",
        type=int,
        help="Modify existing pull request number; DEFAULT: create new PR",
    )

    run_par = parser.add_argument_group("Runtime parameters")
    run_par.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose debug output"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    args.input = str(Path(args.input).resolve())
    if not args.input.endswith("/"):
        args.input += "/"
    out_dir = prep_output_dir()
    out_base = prep_output_prefix(args.input, args.suffix)
    if not args.repository:
        args.repository = os.path.basename(args.input[:-1])

    logger.warning(
        "BioBlueprint may change your branch. Ensure you are pulled and committed appropriately"
    )

    return args, out_dir, out_base


def compile_branch(repo, branch_name=""):
    if branch_name:
        logger.info(f"Checking out branch: {branch_name}")
        repo.git.checkout(branch_name)
    else:
        branch_name = repo.active_branch.name
        logger.info(f"On branch: {branch_name}")
    commit = repo.head.commit.tree
    return commit, branch_name


def identify_changed_files(src_commit, der_commit, suffix):
    """Identify changed files between two commits"""
    # get the diff
    diff = src_commit.diff(der_commit)
    added_files = [
        x.b_path
        for x in diff.iter_change_type("A")
        if x.b_path.endswith(suffix)
    ]
    modified_files = [
        x.b_path
        for x in diff.iter_change_type("M")
        if x.b_path.endswith(suffix)
    ]
    removed_files = [
        x.b_path
        for x in diff.iter_change_type("D")
        if x.b_path.endswith(suffix)
    ]

    logger.info(f"Added files: {added_files}")
    logger.info(f"Modified files: {modified_files}")
    logger.info(f"Removed files: {removed_files}")
    return added_files, modified_files, removed_files


def parse_branches(derived_branch, source_branch, suffix):
    # compile the derived repository branch
    der_commit, derived_branch = compile_branch(repo, branch_name=derived_branch)
    src_commit, source_branch = compile_branch(repo, branch_name=source_branch)

    if source_branch == derived_branch:
        raise SystemExit(
            f"Source branch {source_branch} is the same as derived branch {derived_branch}"
        )

    added_files, modified_files, removed_files = identify_changed_files(
        src_commit, der_commit, suffix
    )
    if not (added_files or modified_files or removed_files):
        raise SystemExit(
            "No added, modified, or removed WDL files detected between source and derived branches"
        )

    return derived_branch, source_branch, added_files, modified_files, removed_files


def compile_affected_nodes(files, prefix):
    """Compile nodes that are affected by modifications in specific workflow files"""
    nodes_dict = {'wf': [], 'task': []}
    for file_ in files:
        node_names = parse_wdl(args.input + file_)
        logger.debug(f"Parsed WDL file {file_}: {node_names}")
        if os.path.basename(file_).startswith(prefix):
            nodes_dict['wf'].extend(node_names)
        else:
            nodes_dict['task'].extend(node_names)
    return nodes_dict




def parse_io_modifications(der_io_dict, src_io_dict):
    """Identify differences in I/O and report by its parent"""
    diff_dict = {}
    for wf in der_io_dict:
        if wf in src_io_dict:
            mod_inputs = sorted(
                set(der_io_dict[wf]["inputs"]) - set(src_io_dict[wf]["inputs"])
            )
            mod_outputs = sorted(
                set(der_io_dict[wf]["outputs"]) - set(src_io_dict[wf]["outputs"])
            )
            rm_inputs = sorted(
                set(src_io_dict[wf]["inputs"]) - set(der_io_dict[wf]["inputs"])
            )
            rm_outputs = sorted(
                set(src_io_dict[wf]["outputs"]) - set(der_io_dict[wf]["outputs"])
            )
            if mod_inputs or mod_outputs or rm_inputs or rm_outputs:
                diff_dict[wf] = {
                    "added_inputs": mod_inputs,
                    "added_outputs": mod_outputs,
                    "removed_inputs": rm_inputs,
                    "removed_outputs": rm_outputs
                }
        else:
            diff_dict[wf] = {
                "added_inputs": sorted(der_io_dict[wf]["inputs"]),
                "added_outputs": sorted(der_io_dict[wf]["outputs"]),
                "removed_inputs": [],
                "removed_outputs": []
            }
    return diff_dict


def parse_wf_task_modifications(new_nodes, perturbed_nodes, removed_nodes):
    """Identify differences in workflows and tasks"""
    wf_diff_dict = {"\+" : [], "Δ": [], "\-": []}
    task_diff_dict = {"\+": [], "Δ": [], "\-": []}
    for node in new_nodes['wf']:
        wf_diff_dict["\+"].append(node)
    for node in new_nodes['task']:
        task_diff_dict["\+"].append(node)
    for node in perturbed_nodes['wf']:
        wf_diff_dict["Δ"].append(node)
    for node in perturbed_nodes['task']:
        task_diff_dict["Δ"].append(node)
    for node in removed_nodes['wf']:
        wf_diff_dict["\-"].append(node)
    for node in removed_nodes['task']:
        task_diff_dict["\-"].append(node)
    return {k: sorted(v) for k, v in wf_diff_dict.items()}, {k: sorted(v) for k, v in task_diff_dict.items()}



if __name__ == "__main__":

    args, out_dir, out_base = initialize_bioblueprint()

    # initialize the repository and git metadata
    if not os.path.isdir(args.input + "/.git"):
        raise SystemExit(
            f"Input directory {args.input} is not the head of a git repository"
        )
    repo = Repo(args.input)

    starting_branch = repo.active_branch.name
    logger.info(f"Initial branch: {starting_branch}")

    derived_branch, source_branch, added_files, modified_files, removed_files = (
        parse_branches(args.derived_branch, args.source_branch, args.suffix)
    )

    logger.info(f"Checking out and compiling derived branch graph: {derived_branch}")
    repo.git.checkout(derived_branch)
    G_der, io_dict_der, node2path_der = compile_repo(
        args.input, args.prefix, args.suffix
    )

    # compile additional and modififed repository nodes
    new_nodes = compile_affected_nodes(added_files, args.prefix)
    perturbed_nodes = compile_affected_nodes(modified_files, args.prefix)

    # compile and parse the source graph to obtain paths for removed nodes
    repo.git.checkout(source_branch)
    G_src, io_dict_src, node2path_src = compile_repo(
        args.input, args.prefix, args.suffix
    )
    removed_nodes = compile_affected_nodes(removed_files, args.prefix)

    # compile the paths affected by modified nodes
    perturbed_roots = obtain_graph_paths(G_der, new_nodes['wf'] + new_nodes['task'] + perturbed_nodes['wf'] + perturbed_nodes['task'])
    if removed_nodes['wf'] or removed_nodes['task']:
        perturbed_roots = {
            **perturbed_roots,
            **obtain_graph_paths(G_src, removed_nodes['wf'] + removed_nodes['task']),
        }

    # create the testing dictionary by adding paths to workflows
    testing_dict = {x: {"path": io_dict_der[x]["path"], "modified": v} for x, v in sorted(perturbed_roots.items(), key = lambda x: x[0])}

    # only need the source branch if we are generating a PR or a test template
    io_diff_dict = parse_io_modifications(io_dict_der, io_dict_src)
    wf_diff_dict, task_diff_dict = parse_wf_task_modifications(new_nodes, perturbed_nodes, removed_nodes)

    io_path = f"{out_dir}{out_base}.io.json"
    pr_out_path = f"{out_dir}{out_base}.pr.md"
    if args.repository == "public_health_bioinformatics":
        # define the standardized paths for PHB and required functions
        pr_template_path, pr_pop_func, i_tsv_path, o_tsv_path, dockstore_path = define_phb_standards(args.input)
        io_update_func = phb_update_io
        io_args = (io_dict_der, i_tsv_path, o_tsv_path, dockstore_path, out_dir, out_base)
    else:
        # do not define functions to parse and output these data
        pr_pop_func, io_update_func = None, None
        pr_template_path = pr_out_path
        with open(pr_template_path, 'w') as out:
            out.write('')

    if args.pull_request is not None:
        logger.info(f"Downloading PR #{args.pull_request} from {args.owner}/{args.repository}")
        pr_str = download_pr(args.owner, args.repository, args.pull_request)
    else:
        logger.info(f"Populating new PR template from {pr_template_path}")
        with open(pr_template_path, "r") as pr_template:
            pr_str = pr_template.read()
    pr_str, testing_dict = pr_pop_func(wf_diff_dict, task_diff_dict, io_diff_dict, testing_dict, pr_str)

    # output files
    with open(io_path, "w") as out:
        out.write(json.dumps(io_dict_der, indent=2))
    with open(f"{out_dir}{out_base}.testing.json", "w") as out:
        out.write(json.dumps(testing_dict, indent=2))
    with open(pr_out_path, "w") as out:
        out.write(pr_str)

    repo.git.checkout(derived_branch)
    logger.info(f"Checking out branch: {derived_branch}")

    # update I/O if applicable
    if io_update_func:
        io_update_func(*io_args)

    repo.git.checkout(starting_branch)
    logger.info(f"Checking out branch: {starting_branch}")

    sys.exit(0)