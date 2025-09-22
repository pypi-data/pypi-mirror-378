#
# Copyright (c) 2023-present Didier Malenfant
#
# This file is part of pfDevTools.
#
# pfDevTools is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pfDevTools is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along with pfDevTools. If not,
# see <https://www.gnu.org/licenses/>.
#

import os
import sys
import shutil
import traceback

from SCons.Script.SConscript import SConsEnvironment

from typing import List, Optional, Any, Tuple
from pathlib import Path

from PyUtilities import Utility
from pfDevTools.PfCommand.Clone import Clone
from pfDevTools.PfCommand.Qfs import Qfs
from pfDevTools.PfCommand.Install import Install
from pfDevTools.CoreConfig import CoreConfig
from pfDevTools.Package import Package


# -- Classes
class OpenFPGACore:
    """A SCons action to build on openFPGA core."""

    @classmethod
    def clone_repo(cls, _target: Any, _source: Any, env: SConsEnvironment) -> None:
        command_line: List[str] = []

        debug_on = env.get('PF_DEBUG_ON', False)    # type: ignore[no-untyped-call]

        url = env.get('PF_CORE_TEMPLATE_REPO_URL', None)    # type: ignore[no-untyped-call]
        if url is not None:
            command_line.append(url)

        tag = env.get('PF_CORE_TEMPLATE_REPO_TAG', None)    # type: ignore[no-untyped-call]
        if tag is not None:
            command_line.append(f'tag={tag}')

        repo_folder = Path(env['PF_CORE_TEMPLATE_FOLDER'])
        command_line.append(str(repo_folder))

        if repo_folder.exists():
            Utility.delete_folder(repo_folder, force_delete=True)

        Clone(command_line, debug_on=debug_on).run()

    @classmethod
    def copy_repo(cls, _target: Any, _source: Any, env: SConsEnvironment) -> None:
        src_folder = Path(env['PF_CORE_TEMPLATE_REPO_FOLDER']).expanduser()
        dest_folder = Path(env['PF_CORE_TEMPLATE_FOLDER'])

        if not src_folder.exists() or not src_folder.is_dir():
            raise RuntimeError(f'Cannot find "{src_folder}" to copy core template repo from.')

        print(f'Copying core template repo from "{src_folder}".')

        if dest_folder.exists():
            Utility.delete_folder(dest_folder, force_delete=True)

        shutil.copytree(src_folder, dest_folder)

        git_folder = dest_folder / '.git'
        if git_folder.exists():
            Utility.delete_folder(git_folder, force_delete=True)

    @classmethod
    def _run_docker_command(cls, image: str, command: str, build_folder: Optional[Path] = None,
                            capture_output: bool = False) -> Tuple[int, List[str]]:
        if not Utility.command_exists('docker'):
            raise RuntimeError('Docker does not seem to be installed.\nCheck pre-requisites in the pf-dev-tools README '
                               'or unset PF_DOCKER_IMAGE_NAME and make sure quartus_sh is in your PATH to use native '
                               'toolchain.')

        if not OpenFPGACore._docker_is_running():
            raise RuntimeError('Docker engine does not seem to be running.\nCheck pre-requisites in the pf-dev-tools '
                               'README or unset PF_DOCKER_IMAGE_NAME and make sure quartus_sh is in your PATH to use '
                               'native toolchain.')

        if not OpenFPGACore._docker_has_image(image):
            print(f'Docker needs to download image "{image}". This may take a while...')

        if not Utility.command_exists('git'):
            raise RuntimeError('You must have git installed on your machine to continue.')

        command_line = ['docker', 'run', '--platform linux/amd64', '-t', '--rm']

        if build_folder is not None:
            command_line.append('-v')
            command_line.append(f'{build_folder}:/build')

        command_line.append(image)
        command_line.append(command)

        test: Tuple[int, List[str]] = Utility.shell_command(command_line, capture_output=capture_output)
        return test

    @classmethod
    def _docker_is_running(cls) -> bool:
        try:
            Utility.shell_command(['docker', 'ps'], capture_output=True)
        except RuntimeError:
            return False

        return True

    @classmethod
    def _docker_has_image(cls, image: str) -> bool:
        code, result = Utility.shell_command(['docker', 'images'], capture_output=True)

        image_info = image.split(':')
        if len(image_info) == 2:
            looking_for = f'{image_info[0]}   {image_info[1]}'
            for line in result:
                if line.startswith(looking_for):
                    return True

        return False

    @classmethod
    def _get_number_of_docker_cp_us(cls, image: str) -> int:
        number_of_cpus = 1

        code, result = OpenFPGACore._run_docker_command(image, 'grep --count ^processor /proc/cpuinfo',
                                                        capture_output=True)
        if len(result) == 1:
            num_cpus_found = int(result[0])
            if num_cpus_found != 0:
                number_of_cpus = num_cpus_found

        return number_of_cpus

    @classmethod
    def _update_qsf_file(cls, target: Any, source: Any, env: SConsEnvironment) -> None:
        core_qsf_file = Path(str(target))
        if not core_qsf_file.exists():
            if env.get('PF_CORE_TEMPLATE_REPO_FOLDER', None) is None:    # type: ignore[no-untyped-call]
                OpenFPGACore.clone_repo(core_qsf_file, core_qsf_file, env)
            else:
                OpenFPGACore.copy_repo(core_qsf_file, core_qsf_file, env)

        core_fpga_folder = Path(env['PF_CORE_FPGA_FOLDER'])

        core_verilog_files = []
        for f in source:
            file_path = str(f)
            if file_path.endswith('.v') or file_path.endswith('.sv'):
                core_verilog_files.append(str(Path(str(f)).relative_to(core_fpga_folder)))

        arguments = [str(core_qsf_file)]
        nb_of_cpus = env.get('PF_NB_OF_CPUS_TO_USE', None)    # type: ignore[no-untyped-call]
        if nb_of_cpus is not None:
            arguments.append(f'cpus={nb_of_cpus}')
        else:
            arguments.append('cpus=ALL')

        if env.get('PF_ENABLE_OPTIMIZATION', None) is not None:    # type: ignore[no-untyped-call]
            arguments.append('optim=perf')

        Qfs(arguments + core_verilog_files).run()

    @classmethod
    def install_core(cls, _target: Any, source: Any, env: SConsEnvironment) -> None:
        debug_on = env.get('PF_DEBUG_ON', False)    # type: ignore[no-untyped-call]

        try:
            command_line = []
            if env.get('PF_EJECT_VOLUME', False):    # type: ignore[no-untyped-call]
                command_line.append('--eject')

            command_line.append(str(source[0]))

            Install(command_line, debug_on=debug_on).run()
        except Exception as e:
            if debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error when installing core.')

            sys.exit(1)

    @classmethod
    def program_core(cls, _target: Any, _source: Any, env: SConsEnvironment) -> None:
        debug_on = env.get('PF_DEBUG_ON', False)    # type: ignore[no-untyped-call]

        try:
            config = CoreConfig(Path(env['PF_CORE_CONFIG_FILE']))
            cores_list = config.cores_list()
            if len(cores_list) != 1 and config.core_source_file(cores_list[0]) != 'pf_core.rbf':
                raise RuntimeError('Programming the Analogue Pocket via JTAG is only supported for default '
                                   'single core projects are the moment.')

            if Utility.command_exists('killall'):
                print('Making sure jtagd is not running.')
                try:
                    Utility.shell_command(['killall', 'jtagd', '--quiet'], capture_output=True)
                except RuntimeError:
                    pass

            if not Utility.command_exists('quartus_pgm'):
                raise RuntimeError('Cannot find "quartus_pgm" command. Make sure Quartus is installed '
                                   'locally/natively on this computer and that "quartus_pgm" is in your PATH.')

            print('Programming Analogue Pocket via JTAG.')

            core_bitstream_output_folder = Path(env['PF_CORE_BITSTREAM_OUTPUT_FOLDER'])
            bit_stream_sof_file = core_bitstream_output_folder / 'pf_core.sof'

            os.system(f'quartus_pgm -m jtag -o "p;{bit_stream_sof_file}@1"')
        except Exception as e:
            if debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error when programming core.')

            sys.exit(1)

    @classmethod
    def _copy_file(cls, target: Any, source: Any, _env: SConsEnvironment) -> None:
        source_file = str(source[0])
        target_file = str(target[0])
        print(f'Copying {source_file} to {target_file}.')
        parent_dest_dir = Path(target_file).parent
        os.makedirs(parent_dest_dir, exist_ok=True)
        shutil.copyfile(source_file, target_file)

    @classmethod
    def search_source_files(cls, env: SConsEnvironment, path: Path,
                            dest_verilog_folder: Path) -> List[Path]:
        dest_verilog_files: List[Path] = []

        for root, dirs, files in os.walk(path, topdown=False):
            for file in files:
                if file.endswith('.sv') or file.endswith('.v') or file.endswith('.svh') or file.endswith('.vh'):
                    src_path = Path(root) / Path(file)
                    dest_path = dest_verilog_folder / src_path.relative_to(path)
                    dest_verilog_files.append(dest_path)

                    env.Command(dest_path, src_path, OpenFPGACore._copy_file)    # type: ignore[no-untyped-call]

        return dest_verilog_files

    @classmethod
    def add_extra_files(cls, env: SConsEnvironment, path: Path, dest_verilog_folder: Path,
                        extra_files: List[Path]) -> List[Path]:
        extra_dest_files: List[Path] = []

        for file in extra_files:
            dest_path = dest_verilog_folder / file.relative_to(path)
            extra_dest_files.append(dest_path)

            env.Command(dest_path, file, OpenFPGACore._copy_file)    # type: ignore[no-untyped-call]

        return extra_dest_files

    @classmethod
    def compile_bit_stream(cls, _target: Any, source: Any, env: SConsEnvironment) -> None:
        print('Compiling core bitstream...')

        try:
            core_qsf_file = Path(env['PF_CORE_QSF_FILE'])
            OpenFPGACore._update_qsf_file(core_qsf_file, source, env)

            command = 'quartus_sh --flow compile'
            project = 'pf_core'
            folder = Path(env['PF_CORE_FPGA_FOLDER']).resolve()

            docker_image_name = os.environ.get('PF_DOCKER_IMAGE_NAME', None)
            if docker_image_name is None and not Utility.command_exists('quartus_sh'):
                docker_image_name = 'didiermalenfant/quartus:22.1-apple-silicon'

                print('WARNING: Cannot find the quartus_sh command. Make sure Quartus is installed and added '
                      'to your PATH.')
                print(f'Attempting to use default docker image "{docker_image_name}". '
                      f'Use PF_DOCKER_IMAGE_NAME to force this behavior.')

            if docker_image_name is None:
                Utility.shell_command([f'{command}', '{folder / project}'])
            else:
                OpenFPGACore._run_docker_command(docker_image_name, f'{command} {project}',
                                                 build_folder=folder)
        except Exception as e:
            if env.get('PF_DEBUG_ON', False):    # type: ignore[no-untyped-call]
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error in compileBitStream().')

            sys.exit(1)

    @classmethod
    def package_core(cls, _target: Any, _source: Any, env: SConsEnvironment) -> None:
        print('Packaging core...')

        debug_on: bool = env.get('PF_DEBUG_ON', False)    # type: ignore[no-untyped-call]

        try:
            Package([env['PF_CORE_CONFIG_FILE'], env['PF_BUILD_FOLDER'],
                    env['PF_CORE_BITSTREAM_OUTPUT_FOLDER']], debug_on=debug_on).run()
        except Exception as e:
            if debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error in packageCore().')

            sys.exit(1)


def build(env: SConsEnvironment, config_file: Path, extra_files: List[Path]) -> Path:
    debug_on: bool = env.get('PF_DEBUG_ON', False)    # type: ignore[no-untyped-call]

    try:
        if env.get('PF_SRC_FOLDER', None) is None:    # type: ignore[no-untyped-call]
            env.SetDefault(PF_SRC_FOLDER=config_file.parent)

        src_folder = Path(env['PF_SRC_FOLDER'])

        env.SetDefault(PF_BUILD_FOLDER='_build')
        build_folder = Path(env['PF_BUILD_FOLDER'])

        env.Replace(PF_CORE_CONFIG_FILE=config_file)

        core_template_folder = build_folder / '_core_template_repo'
        env.Replace(PF_CORE_TEMPLATE_FOLDER=core_template_folder)

        core_fpga_folder = core_template_folder / 'src' / 'fpga'
        env.Replace(PF_CORE_FPGA_FOLDER=core_fpga_folder)

        core_qsf_file = core_fpga_folder / 'pf_core.qsf'
        env.Replace(PF_CORE_QSF_FILE=core_qsf_file)

        core_bitstream_output_folder = core_fpga_folder / 'output_files'
        env.Replace(PF_CORE_BITSTREAM_OUTPUT_FOLDER=core_bitstream_output_folder)

        packaging_process = Package([config_file, build_folder,
                                    core_bitstream_output_folder], debug_on=debug_on)
        packaged_core = build_folder / packaging_process.packaged_filename()

        if not env.get('PF_SKIP_BUILD', False):    # type: ignore[no-untyped-call]
            if env.get('PF_CORE_TEMPLATE_REPO_FOLDER', None) is None:    # type: ignore[no-untyped-call]
                env.Command(core_template_folder, '', OpenFPGACore.clone_repo)    # type: ignore[no-untyped-call]
            else:
                env.Command(core_template_folder, '', OpenFPGACore.copy_repo)    # type: ignore[no-untyped-call]

            dest_verilog_folder = core_fpga_folder / 'core'
            dest_verilog_files = OpenFPGACore.search_source_files(env, src_folder, dest_verilog_folder)
            extra_dest_files = OpenFPGACore.add_extra_files(env, src_folder, dest_verilog_folder, extra_files)

            config = CoreConfig(config_file)
            core_output_bitstream_files: List[Path] = []
            for core_id in config.cores_list():
                core_output_bitstream_file = core_bitstream_output_folder / config.core_source_file(core_id)
                core_output_bitstream_files.append(core_output_bitstream_file)
                env.Precious(core_output_bitstream_file)    # type: ignore[no-untyped-call]

            bitstream_dependencies: List[Path] = dest_verilog_files + extra_dest_files
            stp_file_path = dest_verilog_folder / 'stp1.stp'
            if stp_file_path.exists():
                bitstream_dependencies.append(stp_file_path)

            env.Command(core_output_bitstream_files,
                        bitstream_dependencies,
                        OpenFPGACore.compile_bit_stream)    # type: ignore[no-untyped-call]
            env.Command(packaged_core,
                        packaging_process.dependencies(),
                        OpenFPGACore.package_core)    # type: ignore[no-untyped-call]

            program_command = env.Command(None,
                                          core_output_bitstream_files,
                                          OpenFPGACore.program_core)    # type: ignore[no-untyped-call]
            env.Alias('program', program_command)    # type: ignore[no-untyped-call]

        env.Default(packaged_core)
        env.Clean(packaged_core, build_folder)

        install_command = env.Command(None,
                                      packaged_core,
                                      OpenFPGACore.install_core)    # type: ignore[no-untyped-call]
        env.Alias('install', install_command)    # type: ignore[no-untyped-call]
    except Exception as e:
        if debug_on:
            print(traceback.format_exc())
        else:
            error_string = str(e)

            if len(error_string) != 0:
                print(e)

        sys.exit(1)

    return packaged_core
