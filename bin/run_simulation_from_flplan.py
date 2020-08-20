#!/usr/bin/env python3

# Copyright (C) 2020 Intel Corporation
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import logging

from openfl            import load_yaml
from openfl.flplan     import parse_fl_plan
from single_proc_fed    import federate
from setup_logging      import setup_logging


def main(plan, collaborators_file, data_config_fname, logging_config_path, logging_default_level, logging_directory, model_device, **kwargs):
    """Run the federation simulation from the federation (FL) plan.

    Runs a federated training from the federation (FL) plan but creates the
    aggregator and collaborators on the same compute node. This allows
    the developer to test the model and data loaders before running
    on the remote collaborator nodes.

    Args:
        plan: The Federation (FL) plan (YAML file)
        collaborators_file: The file listing the collaborators
        data_config_fname: The file describing where the dataset is located on the collaborators
        logging_config_path: The log file
        logging_default_level: The log level
        **kwargs: Variable parameters to pass to the function

    """
    # FIXME: consistent filesystem (#15)
    # establish location for fl plan as well as
    # where to get and write model protobufs
    script_dir = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.join(script_dir, 'federations')
    plan_dir = os.path.join(base_dir, 'plans')
    weights_dir = os.path.join(base_dir, 'weights')
    metadata_dir = os.path.join(base_dir, 'metadata')
    collaborators_dir = os.path.join(base_dir, 'collaborator_lists')
    logging_config_path = os.path.join(script_dir, logging_config_path)
    logging_directory = os.path.join(script_dir, logging_directory)

    setup_logging(path=logging_config_path, default_level=logging_default_level, logging_directory=logging_directory)

    # load the flplan, local_config and collaborators file
    flplan = parse_fl_plan(os.path.join(plan_dir, plan))
    local_config = load_yaml(os.path.join(base_dir, data_config_fname))
    collaborator_common_names = load_yaml(os.path.join(collaborators_dir, collaborators_file))['collaborator_common_names']
  
    # TODO: Run a loop here over various parameter values and iterations
    # TODO: implement more than just saving init, best, and latest model
    federate(flplan,
             local_config,
             collaborator_common_names,
             base_dir,
             weights_dir,
             metadata_dir,
             model_device)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', '-p', type=str, required=True)
    parser.add_argument('--collaborators_file', '-c', type=str, required=True, help="Name of YAML File in /bin/federations/collaborator_lists/")
    parser.add_argument('--data_config_fname', '-dc', type=str, default="local_data_config.yaml")
    parser.add_argument('--logging_config_path', '-lcp', type=str, default="logging.yaml")
    parser.add_argument('--logging_default_level', '-l', type=str, default="info")
    parser.add_argument('--logging_directory', '-ld', type=str, default="logs")
    # FIXME: this kind of commandline configuration needs to be done in a consistent way
    parser.add_argument('--model_device', '-md', type=str, default='cpu')
    args = parser.parse_args()
    main(**vars(args))
