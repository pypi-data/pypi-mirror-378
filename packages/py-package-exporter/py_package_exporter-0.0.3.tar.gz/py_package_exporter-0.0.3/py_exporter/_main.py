from pathlib import Path
from typing import Self

from ._utils import *
from ._enums import *
	
class WindowsOptions:
	def __init__(
		self,
		version_file: str | Path | None = None,
		manifest: str | Path | None = None,
		admin: bool = False,
		remote_desktop: bool = False
	):
		"""
		:param version_file: https://pyinstaller.org/en/stable/usage.html#cmdoption-version-file
		:param manifest: https://pyinstaller.org/en/stable/usage.html#cmdoption-manifest
		:param admin: https://pyinstaller.org/en/stable/usage.html#cmdoption-uac-admin
		:param remote_desktop: https://pyinstaller.org/en/stable/usage.html#cmdoption-uac-uiaccess
		"""
		self._resources = []
		self._options = {
			'version_file': Path(version_file) if version_file else None,
			'manifest': Path(manifest) if manifest else None,
			'admin': admin,
			'remote_desktop': remote_desktop
		}
	def get_options(self):
		d = self._options
		d.update(self._resources)
		return d
	def add_resource(self, *resources: tuple[str | Path, str, str, str | int]):
		"""https://pyinstaller.org/en/stable/usage.html#cmdoption-r"""
		return add_list(self, '_resources', resources, lambda v: (Path(v[0]), v[1:]))
class MacOsOptions:
	def __init__(self,
		argv_emulation: bool = False,
	    osx_bundle_identifier: str | None = None,
		target_architecture: TargetArchitecture | None = None,
		codesign_identify: any = None,
	    osx_entitlements_file: str | Path | None = None
	):
		"""
		:param argv_emulation: https://pyinstaller.org/en/stable/usage.html#cmdoption-argv-emulation
		:param osx_bundle_identifier: https://pyinstaller.org/en/stable/usage.html#cmdoption-osx-bundle-identifier
		:param target_architecture: https://pyinstaller.org/en/stable/usage.html#cmdoption-target-architecture
		:param codesign_identify: https://pyinstaller.org/en/stable/usage.html#cmdoption-codesign-identity
		:param osx_entitlements_file: https://pyinstaller.org/en/stable/usage.html#cmdoption-osx-entitlements-file
		"""
		self._options = {
			'argv_emulation': argv_emulation,
			'osx_bundle_identifier': osx_bundle_identifier,
			'target_architecture': target_architecture,
			'codesign_identify': codesign_identify,
			'osx_entitlements_file': Path(osx_entitlements_file),
		}
	def get_options(self):
		return self._options
	

class PyExporter:
	def __init__(self,
	             file: str | Path,
	             name: str | None = None,
	             out_dir: str | Path = Path('./dist'),
	             one_dir: bool = False,
	             one_file: bool = True,
	             spec_path: str | Path = Path('./dist'),
	             work_path: str | Path = Path('./build'),
	             no_confirm: bool = True,
	             clean: bool = False,
	             log_level: LogLevel | None = None,
	             contents_directory: str | Path | None = None,
	             windowed: bool = False,
	             console: bool = True,
	             icon: str | Path | None = None,
	             hide_console: HideConsole | None = None,
	             debug: Debug | None = None,
	             disable_windowed_traceback: bool | None = None,
	             platform_options: MacOsOptions | WindowsOptions | None = None
	             ):
		"""
		:param file: https://pyinstaller.org/en/stable/usage.html#cmdoption-arg-scriptname
		:param name: https://pyinstaller.org/en/stable/usage.html#cmdoption-n
		:param out_dir: https://pyinstaller.org/en/stable/usage.html#cmdoption-distpath
		:param one_dir: https://pyinstaller.org/en/stable/usage.html#cmdoption-D
		:param one_file: https://pyinstaller.org/en/stable/usage.html#cmdoption-F
		:param spec_path: https://pyinstaller.org/en/stable/usage.html#cmdoption-specpath
		:param work_path: https://pyinstaller.org/en/stable/usage.html#cmdoption-workpath
		:param no_confirm: https://pyinstaller.org/en/stable/usage.html#cmdoption-y
		:param clean: https://pyinstaller.org/en/stable/usage.html#cmdoption-clean
		:param log_level: https://pyinstaller.org/en/stable/usage.html#cmdoption-log-level
		:param contents_directory: https://pyinstaller.org/en/stable/usage.html#cmdoption-contents-directory
		:param console: https://pyinstaller.org/en/stable/usage.html#cmdoption-c
		:param windowed: https://pyinstaller.org/en/stable/usage.html#cmdoption-w
		:param icon: https://pyinstaller.org/en/stable/usage.html#cmdoption-i
		:param hide_console: https://pyinstaller.org/en/stable/usage.html#cmdoption-hide-console
		:param debug: https://pyinstaller.org/en/stable/usage.html#cmdoption-d
		:param disable_windowed_traceback: https://pyinstaller.org/en/stable/usage.html#cmdoption-disable-windowed-traceback
		"""
		self._options = {
			'file': file,
			'name': name,
			'out_dir': Path(out_dir),
			'one_dir': one_dir,
			'one_file': one_file,
			'spec_path': Path(spec_path),
			'work_path': Path(work_path),
			'no_confirm': no_confirm,
			'clean': clean,
			'log_level': get_enum_str(log_level),
			'contents_directory': contents_directory,
			'windowed': windowed,
			'console': console,
			'icon': icon,
			'hide_console': hide_console,
			'debug': get_enum_str(debug),
			'disable_windowed_traceback': disable_windowed_traceback,
		}
		if platform_options:
			self._options.update(platform_options.get_options())

		self._data: list[tuple[Path, Path]] = []
		self._binary: list[tuple[Path, Path]] = []
		self._paths: list[Path] = []
		self._hidden_imports: list[str] = []
		self._collects: list[tuple[CollectType, str]] = []
		self._copy_metadata: list[tuple[str, bool]] = []
		self._additional_hooks_directory: list[Path] = []
		self._runtime_hooks: list[str] = []
		self._exclude_module: list[str] = []

	def add_data(self, source: str | Path, destination: str | Path) -> Self:
		"""https://pyinstaller.org/en/stable/usage.html#cmdoption-add-data"""
		return add(self,'_data', [(Path(source), Path(destination))])
	def add_binary(self, source: str | Path, destination: str | Path) -> Self:
		"""https://pyinstaller.org/en/stable/usage.html#cmdoption-add-binary"""
		return add(self, '_binary', [(Path(source), Path(destination))])
	def add_path(self, *directories: str | Path) -> Self:
		"""https://pyinstaller.org/en/stable/usage.html#cmdoption-p"""
		return add_list(self,'_paths', directories, lambda path: Path(path))
	def add_hidden_import(self, *module_names: str):
		"""https://pyinstaller.org/en/stable/usage.html#cmdoption-hidden-import"""
		return add_list(self,'_hidden_imports', module_names)
	def add_collect(self, collect_type: CollectType | str, *module_names: str):
		"""
		Depends on `collect_type` variable:

		DATA: https://pyinstaller.org/en/stable/usage.html#cmdoption-collect-data

		SUBMODULES: https://pyinstaller.org/en/stable/usage.html#cmdoption-collect-data

		BINARIES: https://pyinstaller.org/en/stable/usage.html#cmdoption-collect-binaries

		ALL: https://pyinstaller.org/en/stable/usage.html#cmdoption-collect-all
		"""
		if not (get_enum_str(collect_type) in get_enum_data(CollectType).values()):
			raise ValueError(f'Invalid "collect_type"')
		for module_name in module_names:
			add(self,'_collects', [(collect_type, module_name)])
		return self
	def add_copy_metadata(self, *package_names: str | tuple[str, bool]):
		"""
		if tuple second argument is `True` then it uses `recursive-copy-metadata`

		https://pyinstaller.org/en/stable/usage.html#cmdoption-copy-metadata

		RECURSIVE: https://pyinstaller.org/en/stable/usage.html#cmdoption-recursive-copy-metadata
		"""
		for package in package_names:
			extended = type(package) == str
			name = package if extended else package[0]
			recursive = False if extended else package[1]
			add(self,'_copy_metadata', [(name, recursive)])
		return self
	def add_additional_hooks_directory(self, *hook_paths: str | Path):
		"""https://pyinstaller.org/en/stable/usage.html#cmdoption-additional-hooks-dir"""
		return add_list(self,'_additional_hooks_directory', hook_paths, lambda v: Path(v))
	def add_runtime_hook(self, *runtime_hooks: str):
		"""https://pyinstaller.org/en/stable/usage.html#cmdoption-runtime-hook"""
		return add_list(self,'_runtime_hooks', runtime_hooks)
	def add_exclude_module(self, *excludes: str):
		"""https://pyinstaller.org/en/stable/usage.html#cmdoption-exclude-module"""
		return add_list(self,'_exclude_module', excludes)

	def get_options(self):
		d = self._options
		items = get_dict(self.__dict__, lambda key, v, is_function: not is_function)
		for key, value in items.items():
			if type(value) != list:
				continue
			d[key] = value

		options: dict[str, any] = { key: value for key, value in d.items() if value is not None }

		def create_or_update(k: str, v: any):
			options[k] = [*(options.get(k) or []), v]

		options.pop('_collects')
		for collect_type, collect in self._collects:
			key = f'collect_{collect_type.value}'
			create_or_update(key, collect)
		options.pop('_copy_metadata')
		for data, recursive in self._copy_metadata:
			key = 'recursive_copy_metadata' if recursive else 'copy_metadata'
			create_or_update(key, data)
		return options
	def get_pyinstaller_options(self, pretty: bool = True):
		options = self.get_options()
		pyinstaller_options: list[str] = [
			options.get('file'),
		]
		for opt, value in options.items():
			key, mod = OptionsMap.get(re.sub(r'^_+', '', str(opt)))
			if value is None and key is None:
				continue

			match mod:
				case 'b':
					if not value:
						continue
					pyinstaller_options.append(key)
				case 's':
					if not value:
						continue
					pyinstaller_options.append(key)
					pyinstaller_options.append(value)
				case 'l':
					if not value:
						continue
					for item in value:
						split = key.split(' ')
						if len(split) > 1:
							pyinstaller_options.append(split[0])
							pyinstaller_options.append(format("".join(split[1:]), *[str(i) for i in item]))
							continue
						pyinstaller_options.append(key)
						pyinstaller_options.append(str(item))
		if pretty:
			values = [value.strip().split(' ') for value in re.split(r'--', " ".join([str(opt) for opt in pyinstaller_options[1:]])) if value]
			return [
				('scriptname', pyinstaller_options[0]),
				*[(value[0], " ".join(value[1:]) or None) for value in values]
			]
		return [str(opt) for opt in pyinstaller_options]
	def run(self, print_options: bool = False):
		from PyInstaller.__main__ import run
		run(self.get_pyinstaller_options(False))
		if print_options:
			print(self.get_pyinstaller_options(True))

PyExporter('./_main.py').add_copy_metadata('readchar')