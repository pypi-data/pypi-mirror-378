from enum import Enum
from typing import overload
import re

class OptionsMap(Enum):
	s_out_dir = '--distpath'
	s_work_path = '--workpath'
	b_no_confirm = '--noconfirm'
	b_clean = '--clean'
	s_log_level = '--log-level'
	b_one_dir = '--onedir'
	b_one_file = '--onefile'
	s_spec_path = '--specpath'
	s_name = '--name'
	s_contents_directory = '--contents-directory'
	s_icon = '--icon'
	b_windowed = '--windowed'
	b_console = '--console'
	s_hide_console = '--hide-console'
	b_disable_windowed_traceback = '--disable-windowed-traceback'
	s_version_file = '--version-file'
	s_manifest = '--manifest'
	b_admin = '--uac-admin'
	b_remote_desktop = '--uac-uiaccess'
	b_argv_emulation = '--argv-emulation'
	s_osx_bundle_identifier = '--osx-bundle-identifier'
	s_target_architecture = '--target-architecture'
	s_codesign_identity = '--codesign-identity'
	s_osx_entitlements_file = '--osx-entitlements-file'
	l_data = '--add-data {}:{}'
	l_binary = '--add-binary {}:{}'
	l_paths = '--paths'
	l_exclude_module = '--exclude_module'
	l_collect_data = '--collect-data'
	l_collect_submodules = '--collect-submodules'
	l_collect_binaries = '--collect-binaries'
	l_collect_all = '--collect-all'
	l_copy_metadata = '--copy-metadata'
	l_recursive_copy_metadata = '--recursive-copy-metadata'
	l_additional_hooks_dir = '--additional-hooks-dir'
	l_runtime_hook = '--runtime-hook'

	@staticmethod
	@overload
	def get(keys: str) -> tuple[str | None, str | None]: ...

	@staticmethod
	@overload
	def get(*keys: str) -> list[tuple[str, str]]: ...

	@staticmethod
	def get(*keys: str):
		options = OptionsMap.get_grouped()

		options_grouped = { }
		[[options_grouped.update({ key: (value, mod) }) for key, value in opt.items()] for mod, opt in options.items()]
		values = (value for opt, value in options_grouped.items() if opt in keys)
		if len(keys) == 1:
			return next(values, (None, None))

		return [*values]

	@staticmethod
	def get_grouped() -> dict[str, dict[str, str]]:
		options = { opt.name: opt.value for opt in OptionsMap }
		options_grouped = { }
		for opt, value in options.items():
			mod, key = re.split(r'(?<=^\w)_', opt)

			d = { key: value }
			if options_grouped.get(mod) is not None:
				d.update(options_grouped.get(mod))

			options_grouped.update({ mod: d })

		return options_grouped


class TargetArchitecture(Enum):
	x86_64 = 'x86_64'
	arm64 = 'arm64'
	universal = 'universal2'


class CollectType(Enum):
	SUBMODULES = 'submodules'
	DATA = 'data'
	BINARIES = 'binaries'
	ALL = 'all'


class LogLevel(Enum):
	TRACE = 'TRACE'
	DEBUG = 'DEBUG'
	INFO = 'INFO'
	WARN = 'WARN'
	DEPRECATION = 'DEPRECATION'
	ERROR = 'ERROR'
	FATAL = 'FATAL'


class Debug(Enum):
	ALL = 'all'
	IMPORTS = 'imports'
	BOOTLOADER = 'bootloader'
	NO_ARCHIVE = 'noarchive'


class HideConsole(Enum):
	HIDE_EARLY = 'hide-early'
	HIDE_LATE = 'hide-late'
	MINIMIZE_EARLY = 'minimize-early'
	MINIMIZE_LATE = 'minimize-late'