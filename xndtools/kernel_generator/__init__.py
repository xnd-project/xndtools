
import os

xnd_tools_script = 'xnd_tools'

def generate_config(args):
    """ Generate initial kernel configuration file from scanning header files.

    Returns
    -------
    r : dict
      dict(config_file=...)
    """
    r = None
    print('\n--- Configuration file generator ---\n')
    if args.module is None:
        first = args.header_files[0]
        args.module = os.path.splitext(os.path.basename(first))[0]
    if args.config_file is None:
        args.config_file = '{module}-kernels.cfg'.format(**vars(args))
    if 0 and os.path.isfile(args.config_file):
        print('Configuration file {!r} exists! Remove it manually to override.\n'.format(args.config_file))
    else:
        from xndtools.kernel_generator.generate_config import generate_config
        include_dirs = list(set([os.path.dirname(fn) for fn in args.header_files]))
        includes = [os.path.basename(fn) for fn in args.header_files]
        exclude_patterns = []
        if args.exclude is not None:
            exclude_patterns = [args.exclude]
        if args.match is not None:
            match_patterns = [args.match]
        r = generate_config(modulename=args.module,
                            exclude_patterns = exclude_patterns,
                            match_patterns = match_patterns,
                            includes = includes,
                            include_dirs = include_dirs,
                            target_file = args.config_file,
        )
    print('\nHINT: After editing the configuration file, run:\n\n  {} kernel {}\n'.format(xnd_tools_script, args.config_file))
    return r

def generate_kernel(args):
    """ Generate C source of gumath kernels.

    Parameters
    ----------
    args : argparse.Namespace
      Specify `xnd_tools kernel` arguments: Namespace(config_file=..., target_file=..., source_dir=...) 

    Returns
    -------
    r : dict
      dict(sources = [...], config_file=...)
    """
    r = None
    print('\n--- Kernel file generator ---\n')

    if not os.path.isfile(args.config_file):
        print('Not a file: {!r}. Expected file path to kernel configuration file. Exiting.'.format(args.config_file))
        return
    if args.source_dir is None:
        args.source_dir = ''
    source_dir = args.source_dir
    
    from xndtools.kernel_generator.generate_kernel2 import generate_kernel
    r = generate_kernel(config_file = args.config_file,
                        target_file = args.target_file)
    print('HINT: To create extension module, run:\n\n  {} module {}\n'.format(xnd_tools_script, args.config_file))
    return r

def generate_module(args):
    """ Generate C source of gumath extension module.

    Parameters
    ----------
    args : argparse.Namespace
      Specify `xnd_tools kernel` arguments:

        Namespace(config_file=..., target_file=..., target_language=None, package=None,
                  kernel_source_file=None, source_dir=...) 

    Returns
    -------
    r : dict
      dict(sources = [...], config_file=..., include_dirs=[], language=..)
    """
    r = None
    print('\n--- Module file generator ---\n')
    print(args)
    if not os.path.isfile(args.config_file):
        print('Not a file: {!r}. Expected file path to kernel configuration file. Exiting.'.format(args.config_file))
        return
    if args.source_dir is None:
        args.source_dir = ''
    source_dir = args.source_dir
    sources = []
    if args.kernels_source_file is None:
        from xndtools.kernel_generator.generate_kernel import generate_kernel
        r = generate_kernel(config_file = args.config_file,
                            target_file = args.target_file,
                            source_dir = source_dir)
        args.kernels_source_file = r['sources'][0]
        sources.extend(r['sources'])
    if not os.path.isfile(args.kernels_source_file):
        print('Not a file: {!r}. Expected file path to kernel C source file. Exiting.'.format(args.config_file))
        return
        
    from xndtools.kernel_generator.generate_module import generate_module
    r = generate_module(config_file = args.config_file,
                        target_file = args.target_file,
                        target_language = args.target_language,
                        package = args.package,
                        sources = sources,
                        source_dir = source_dir)
    return r
