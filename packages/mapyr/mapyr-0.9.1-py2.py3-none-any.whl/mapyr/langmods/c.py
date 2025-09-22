from ..core import *
from ..logs import logger
from ..utils import *

import json
import re

class Config(ConfigBase):
    dir_members = ['TARGET_PATH','SRC_DIRS','OBJ_PATH','INCLUDE_DIRS','LIB_DIRS','SOURCES']

    def __init__(self) -> None:
        super().__init__()
        self.dir_members = Config.dir_members

        self.SRC_DIRS : list[str] = ['src']
        '''
            Paths to sources
        '''

        self.OBJ_PATH : str = 'obj'
        '''
            Path where to store object files
        '''

        self.INCLUDE_DIRS : list[str] = []
        '''
            Include directories for this project and children
        '''

        self.COMPILER : str = 'clang'
        '''
            Compiler exe name
        '''

        self.AR : str = 'ar'
        '''
            Archiver
        '''

        self.AR_FLAGS : list[str] = ['r','c','s']
        '''
            Archiver flags
        '''

        self.CFLAGS : list[str] = []
        '''
            Compile flags
        '''

        self.LINK_FLAGS : list[str] = []
        '''
            Flags used while linking
        '''

        self.LIB_DIRS : list[str] = []
        '''
            Directories where looking for libraries
        '''

        self.LIBS : list[str] = []
        '''
            List of libraries
        '''

        self.DEFINES : list[str] = []
        '''
            Defines used in this project and all its children
        '''

        self.SOURCES : list[str] = []
        '''
            List of source files
        '''

        self.VSCODE_CPPTOOLS_CONFIG : bool = False
        '''
            Generate C/C++ Tools for Visual Studio Code config (c_cpp_properties.json)
        '''

        self.COMPILE_COMMANDS : bool = False
        '''
            Generate compile_commands.json
        '''

    def get_build_string(self) -> str:
        '''
            Config string need to sign config of built files
            If any flag, that influences on the result file was changed then need to rebuild all targets
        '''
        lst = [
            self.AR,
            self.COMPILER,
            self.CFLAGS,
            self.DEFINES,
            self.LINK_FLAGS,
        ]
        return str(lst)

    def extend(self, other:'Config', members : list[str] = None):
        if not members:
            members = ['DEFINES','INCLUDE_DIRS','LIBS','LIB_DIRS']

        for member in members:
            getattr(self, member).extend(getattr(other, member))

class Project(ProjectBase):
    def __init__(self,
            name:str,
            target:str,
            private_config:Config = None,
            protected_config:Config = None,
            public_config:Config = None,
            subprojects:list['ProjectBase'] = None
        ):
        super().__init__(name, target, private_config, protected_config, public_config, subprojects)

        self.private_config     : Config
        self.protected_config   : Config
        self.public_config      : Config

    def delete_objects_if_config_different(self):
        '''
            If already built objects config not match current config
            we must delete old objects and build new
        '''
        if os.path.isabs(self.private_config.OBJ_PATH):
            ap = self.private_config.OBJ_PATH
        else:
            ap = os.path.join(self.private_config.CWD, self.private_config.OBJ_PATH)

        cfg_path = os.path.join(ap,'config_tag')
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r') as f:
                if f.read() != self.private_config.get_build_string():
                    silentremove(ap)
        return 0

    def build(self, rule:Rule):
        # Before build, make all configs absolute path
        def _set_absolute_config_paths(project:ProjectBase):
            if type(project) is Project:
                project.private_config.make_abs()
                if project.protected_config:
                    project.protected_config.make_abs()
                if project.public_config:
                    project.public_config.make_abs()

            return 0

        def _check_config(project:ProjectBase):
            project.delete_objects_if_config_different()
            return 0


        self.project_recursive_run(_set_absolute_config_paths)
        self.project_recursive_run(_check_config)

        code = super().build(rule)

        # Making compile commands
        if self.private_config.COMPILE_COMMANDS and code == 0:
            if os.path.isabs(self.private_config.OBJ_PATH):
                ap = self.private_config.OBJ_PATH
            else:
                ap = os.path.join(self.private_config.CWD, self.private_config.OBJ_PATH)
            source_names_hash_file = os.path.join(ap,'source_names_hash')
            compile_commands_file = os.path.join(self.private_config.CWD, 'compile_commands.json')

            write_compile_commands = False
            if not os.path.exists(compile_commands_file) or not os.path.exists(source_names_hash_file):
                write_compile_commands = True
            else:
                with open(source_names_hash_file, 'r') as f:
                    if int(f.read()) != self.source_names_hash:
                        write_compile_commands = True

            if write_compile_commands:
                with open(compile_commands_file,'w+') as f:
                    json.dump(self.get_compile_commands(),f)

            with open(source_names_hash_file, 'w+') as f:
                f.write(str(self.source_names_hash))

        if self.private_config.VSCODE_CPPTOOLS_CONFIG:
            vscode_make_cpp_properties(self)

        return code

def vscode_make_cpp_properties(project:ProjectBase):
    '''
        For visual studio code, С/С++ extension.
    '''
    cfg : Config = project.private_config

    vscode_file_path = f'{cfg.CWD}/.vscode/c_cpp_properties.json'
    if os.path.exists(vscode_file_path):
        import inspect
        build_py_filename = inspect.stack()[2].filename
        if os.path.getmtime(build_py_filename) <= os.path.getmtime(vscode_file_path):
            return
    else:
        os.makedirs(os.path.dirname(vscode_file_path), exist_ok=True)

    config = {
        'name':project.name,
        'includePath':cfg.INCLUDE_DIRS,
        'defines':cfg.DEFINES
    }

    main_config = {
        'configurations':[config],
        "version": 4
    }

    with open(vscode_file_path, 'w+') as f:
        json.dump(main_config, f, indent=4)

def build_object(rule:Rule) -> CompileCommand:
    cfg : Config = rule.parent.private_config

    dirn = os.path.dirname(rule.target)
    if dirn:
        os.makedirs(dirn,exist_ok=True)

    compile_command = CompileCommand()
    compile_command._name = color_text(94,'Building')
    compile_command.file = rule.prerequisites[0].target
    compile_command.directory = cfg.CWD
    compile_command.output = rule.target

    compile_command.arguments = \
        [cfg.COMPILER,'-MT','','-MMD','-MP','-MF',''] \
        + cfg.CFLAGS \
        + [f"-D{x}" for x in cfg.DEFINES] \
        + [f"-I{x}" for x in cfg.INCLUDE_DIRS] \
        + ['-c','-o','','']

    path_wo_ext     = os.path.splitext(rule.target)[0]
    compile_command.arguments[2]    = rule.prerequisites[0].target
    compile_command.arguments[6]    = f"{path_wo_ext}.d"
    compile_command.arguments[-2]   = rule.target
    compile_command.arguments[-1]   = rule.prerequisites[0].target
    # mapyr special flags
    compile_command.arguments.insert(7, f'-D__MAPYR__FILENAME__="{os.path.basename(rule.prerequisites[0].target)}"')

    return compile_command

def link_executable(rule:Rule) -> CompileCommand:
    cfg : Config = rule.parent.private_config

    dirn = os.path.dirname(rule.target)
    if dirn:
        os.makedirs(dirn,exist_ok=True)

    compile_command = CompileCommand()
    compile_command._name = color_text(32,'Linking executable')
    compile_command.directory = cfg.CWD
    compile_command.output = rule.target

    compile_command.arguments = [cfg.COMPILER] \
    + cfg.LINK_FLAGS \
    + [f"-L{x}" for x in cfg.LIB_DIRS] \
    + [x.target for x in rule.prerequisites if not x.phony and x.target.endswith('.o')] \
    + ['-o',rule.target] \
    + [f"-l{x}" for x in cfg.LIBS]

    abs_dir_obj=os.path.join(cfg.CWD, cfg.OBJ_PATH)
    if not os.path.exists(abs_dir_obj):
        os.makedirs(abs_dir_obj,exist_ok=True)
    with open(os.path.join(abs_dir_obj,'config_tag'),'w+') as f:
        f.write(cfg.get_build_string())

    return compile_command

def link_static(rule:Rule) -> CompileCommand:
    cfg : Config = rule.parent.private_config

    dirn = os.path.dirname(rule.target)
    if dirn:
        os.makedirs(dirn,exist_ok=True)

    compile_command = CompileCommand()
    compile_command._name = color_text(33,'Linking static')
    compile_command.directory = cfg.CWD
    compile_command.output = rule.target

    compile_command.arguments = [cfg.AR] \
    + [''.join(cfg.AR_FLAGS)] \
    + [rule.target] \
    + [x.target for x in rule.prerequisites if not x.phony and x.target.endswith('.o')]

    abs_dir_obj=os.path.join(cfg.CWD, cfg.OBJ_PATH)
    if not os.path.exists(abs_dir_obj):
        os.makedirs(abs_dir_obj,exist_ok=True)
    with open(os.path.join(abs_dir_obj,'config_tag'),'w+') as f:
        f.write(cfg.get_build_string())

    return compile_command

def add_rules_from_d_file(path:str,project:ProjectBase):
    if not os.path.isabs(path):
        path = os.path.join(caller_cwd(),path)
    if not os.path.isfile(path):
        return

    with open(path,'r') as f:
        content = f.read()

    # make list[str] = ["/dir/targtet:src1.c src2.c src3.c", ...]
    content = content.replace('\\\n','')
    content = content.replace('\n\n','\n')
    content = content.split('\n')

    for line in content:
        if not line:
            continue
        spl = line.split(':')
        if len(spl) < 2:
            continue

        target = spl[0].strip()
        spl[1] = re.split(r'\s+',spl[1].strip()) if spl[1] else []
        prerequisites = [x for x in spl[1] if x != target]
        rule = project.find_rule(target)
        if not rule:
            rule = Rule(target,project)

        for prq in prerequisites:
            prq_rule = project.find_rule(prq)
            if not prq_rule:
                prq_rule = Rule(prq,project)
                project.rules.append(prq_rule)
            rule.prerequisites.append(prq_rule)

def gen_vscode_config(rule:Rule):
    '''
        Default vs code configs
    '''
    if os.path.exists('.vscode'):
        logger.error('directory .vscode already exists')
        exit()
    os.makedirs('.vscode')
    launch = {"version":"0.2.0","configurations":[{"name":"app","type":"cppdbg","request":"launch","program":"main","args":[],"stopAtEntry":False,"cwd":"${workspaceFolder}","environment":[],"externalConsole":False,"MIMode":"gdb","preLaunchTask":"build","setupCommands":[{"text":"-enable-pretty-printing","ignoreFailures":True},{"text":"-gdb-set disassembly-flavor intel","ignoreFailures":True}]}]}
    tasks = {"version":"2.0.0","tasks":[{"label":"build","type":"shell","command":"./build.py","group":{"isDefault":True,"kind":"build"},"presentation":{"clear":True}},{"label":"clean","type":"shell","command":"./build.py clean","presentation":{"reveal":"never"}}]}
    with open('.vscode/launch.json','w+') as flaunch, open('.vscode/tasks.json','w+') as ftasks:
        json.dump(launch, flaunch, indent=4)
        json.dump(tasks, ftasks, indent=4)

def clean(rule:Rule):
    def _clean(_prj : Project):
        silentremove(_prj.private_config.OBJ_PATH)

    rule.parent.project_recursive_run(_clean)

def pkg_config_search(packages:list[str],config:Config):
    '''
        Load libs data from pkg-config
    '''

    out = sh(["pkg-config","--cflags","--libs"]+packages,True)
    if out.stderr:
        logger.error(f'pkg_config_search :{out.stderr}')
        return
    out = out.stdout.replace('\n','')
    spl = out.split(' ')

    config.INCLUDE_DIRS.extend([x[2:] for x in spl if x.startswith('-I')])
    config.LIB_DIRS.extend([x[2:] for x in spl if x.startswith('-L')])
    config.LIBS.extend([x[2:] for x in spl if x.startswith('-l')])


def add_default_rules(project:ProjectBase) -> None:
    '''
        Auto create rules for C project
    '''
    cfg : Config = project.private_config

    # Path to main target
    target_path = cfg.parent.target if os.path.isabs(cfg.parent.target) else os.path.join(cfg.CWD,cfg.parent.target)

    # Sources
    cfg.SOURCES = cfg.get_abs_val(cfg.SOURCES) + find_files(cfg.SRC_DIRS, ['.c','.cc','.cpp'], cwd=cfg.CWD)
    cfg.SOURCES = unify_list(cfg.SOURCES)

    objects = [os.path.join(cfg.CWD,'obj',os.path.relpath(os.path.splitext(x)[0],cfg.CWD).replace('../','updir/'))+'.o' for x in cfg.SOURCES]

    # Dependencies files '.d' paths
    deps = [f'{os.path.splitext(x)[0]}.d' for x in objects]

    ext = os.path.splitext(target_path)[1]
    object_rules = []

    for i in range(len(cfg.SOURCES)):
        # Create rules for sources/objects
        src_rule = Rule(cfg.SOURCES[i], cfg.parent)
        project.rules.append(src_rule)

        object_rule = Rule(objects[i], cfg.parent, [src_rule], build_object,False)
        object_rules.append(object_rule)

        project.rules.append(object_rule)
        add_rules_from_d_file(deps[i],project)

    match ext:
        case '.a':
            if not project.public_config:
                project.public_config = cfg
            project.main_rule = Rule(target_path, cfg.parent, object_rules, link_static, False)
            project.rules.append(project.main_rule)

            pub_cfg : Config = project.public_config
            pub_cfg.LIBS.append(os.path.basename(target_path)[3:-2])
            pub_cfg.LIB_DIRS.append(os.path.dirname(target_path))

        case '.so','.dll':
            raise NotImplementedError('The shared library rules maker not implemented yet')

        case '.elf'|'.exe'|'':
            project.main_rule = Rule(target_path, cfg.parent, object_rules, link_executable, False)
            project.rules.append(project.main_rule)

    for sp in project.subprojects:
        sp.public_config.make_abs()
        project.main_rule.prerequisites.append(sp.main_rule)
        project.private_config.extend(sp.public_config)

    rule_build = Rule('build',project,[project.main_rule],phony=True)
    rule_clean = Rule('clean',project,exec=clean,phony=True)

    project.rules.append(rule_build)
    project.rules.append(rule_clean)
