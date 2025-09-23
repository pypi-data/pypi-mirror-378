"""
Heart of the "gluetool" script. Referred to by setuptools' entry point.
"""

from __future__ import print_function

import functools
import logging
import os
import re
import signal
import sys
import traceback

from six import ensure_str, iteritems, iterkeys

import psutil
import tabulate

import gluetool
import gluetool.action
import gluetool.sentry

from .glue import GlueError, GlueRetryError, Failure, PipelineStepModule
from .help import extract_eval_context_info, docstring_to_help
from .log import log_dict
from .utils import format_command_line, cached_property, normalize_path, render_template, normalize_multistring_option

# Type annotations
# pylint: disable=unused-import,wrong-import-order,ungrouped-imports
from typing import cast, overload, Any, Callable, List, Optional, NoReturn, Union, TYPE_CHECKING  # noqa
from types import FrameType  # noqa
from gluetool.glue import PipelineReturnType  # noqa

if TYPE_CHECKING:
    from typing import Literal  # noqa

# Order is important, the later one overrides values from the former
DEFAULT_GLUETOOL_CONFIG_PATHS = [
    '/etc/gluetool.d/gluetool',
    normalize_path('~/.gluetool.d/gluetool'),
    normalize_path('./.gluetool.d/gluetool')
]

DEFAULT_SIGTERM_TIMEOUT = 60


def handle_exc(func: Callable[..., Any]) -> Callable[..., Any]:

    @functools.wraps(func)
    def wrapped(self: 'Gluetool', *args: Any, **kwargs: Any) -> Any:

        # pylint: disable=broad-except, protected-access

        try:
            return func(self, *args, **kwargs)

        except (SystemExit, KeyboardInterrupt, Exception):
            self._handle_failure(Failure(self.Glue.current_module if self.Glue else None, sys.exc_info()))

    return wrapped


class Gluetool(object):
    def __init__(self) -> None:

        self.gluetool_config_paths = DEFAULT_GLUETOOL_CONFIG_PATHS

        if 'GLUETOOL_CONFIG_PATHS' in os.environ:
            self.gluetool_config_paths = gluetool.utils.normalize_path_option(
                os.environ['GLUETOOL_CONFIG_PATHS']
            )

        self.sentry: Optional[gluetool.sentry.Sentry] = None
        self.tracer: Optional[gluetool.action.Tracer] = None

        # pylint: disable=invalid-name
        self.Glue: Optional[gluetool.glue.Glue] = None

        self.argv: Optional[List[str]] = None
        self.pipeline_desc: Optional[List[gluetool.glue.PipelineStepModule]] = None

    @cached_property
    def _version(self) -> str:

        from .version import __version__

        return ensure_str(__version__.strip())

    def _deduce_pipeline_desc(self, argv: List[Any], modules: List[str]) -> List[gluetool.glue.PipelineStepModule]:

        """
        Split command-line arguments, left by ``gluetool``, into a pipeline description, splitting them
        by modules and their options.

        :param list argv: Remainder of :py:data:`sys.argv` after removing ``gluetool``'s own options.
        :param list(text) modules: List of known module names.
        :returns: Pipeline description in a form of a list of :py:class:`gluetool.glue.PipelineStepModule` instances.
        """

        alias_pattern = re.compile(r'^([a-z\-]*):([a-z\-]*)$', re.I)

        pipeline_desc = []
        step = None

        while argv:
            arg = argv.pop(0)

            # is the "arg" a module name? If so, add new step to the pipeline
            if arg in modules:
                step = PipelineStepModule(arg)
                pipeline_desc.append(step)
                continue

            # is the "arg" a module with an alias? If so, add a new step to the pipeline, and note the alias
            match = alias_pattern.match(arg)
            if match is not None:
                module, actual_module = match.groups()

                step = PipelineStepModule(module, actual_module=actual_module)
                pipeline_desc.append(step)
                continue

            if step is None:
                raise GlueError("Cannot parse module argument: '{}'".format(arg))

            step.argv.append(arg)

        return pipeline_desc

    def log_cmdline(self, argv: List[Any], pipeline_desc: List[gluetool.glue.PipelineStepModule]) -> None:

        cmdline = [
            [ensure_str(sys.argv[0])] + argv
        ]

        for step in pipeline_desc:
            cmdline.append([step.module_designation] + step.argv)

        assert self.Glue is not None
        self.Glue.info('command-line:\n{}'.format(format_command_line(cmdline)))

    @cached_property
    def _exit_logger(self) -> gluetool.log.ContextAdapter:

        """
        Return logger for use when finishing the ``gluetool`` pipeline.
        """

        # We want to use the current logger, if there's any set up.
        logger = gluetool.log.Logging.get_logger()

        if logger:
            return logger

        # This may happen only when something went wrong during logger initialization
        # when Glue instance was created. Falling back to a very basic Logger seems
        # to be the best option here.

        logging.basicConfig(level=logging.DEBUG)
        logger = gluetool.log.ContextAdapter(logging.getLogger())

        logger.warning('Cannot use custom logger, falling back to a default one')

        return logger

    def _quit(self, exit_status: int) -> NoReturn:

        """
        Log exit status and quit.
        """

        logger = self._exit_logger

        if self.tracer:
            self.tracer.close(logger=logger)

        (logger.debug if exit_status == 0 else logger.error)('Exiting with status {}'.format(exit_status))

        sys.exit(exit_status)

    # Depending on the value of the optional `do_quit` parameter, the methods may not return,
    # because when set to `True`, the methods eventually call `sys.exit()`. We're using `@overload`
    # to explain the situation to type checking.

    # pylint: disable=invalid-name,function-redefined
    @overload
    def _handle_failure_core(self, failure: gluetool.glue.Failure, do_quit: 'Literal[True]' = True) -> NoReturn:

        pass

    @overload  # noqa
    def _handle_failure_core(self, failure: gluetool.glue.Failure, do_quit: 'Literal[False]') -> None:  # noqa

        pass

    def _handle_failure_core(self, failure, do_quit=True):  # type: ignore  # noqa
        logger = self._exit_logger

        assert failure.exc_info is not None
        assert failure.exc_info[1] is not None

        # Handle simple 'sys.exit(0)' - no exception happened
        if failure.exc_info[0] == SystemExit:
            assert isinstance(failure.exc_info[1], SystemExit)  # collapse type to SystemExit to make mypy happy

            if failure.exc_info[1].code == 0:
                self._quit(0)

        # soft errors are up to users to fix, no reason to kill pipeline
        exit_status = 0 if failure.soft is True else -1

        if failure.module:
            msg = "Pipeline reported an exception in module '{}': {}".format(
                failure.module.unique_name,
                str(failure.exc_info[1]) or repr(failure.exc_info[1])
            )

        else:
            msg = "Pipeline reported an exception: {}".format(
                str(failure.exc_info[1]) or repr(failure.exc_info[1])
            )

        logger.error(msg, exc_info=failure.exc_info)

        # Submit what hasn't been submitted yet...
        if self.sentry and not failure.sentry_event_id:
            self.sentry.submit_exception(failure, logger=logger)

        if do_quit:
            self._quit(exit_status)

    # pylint: disable=invalid-name,function-redefined
    @overload
    def _handle_failure(self, failure: gluetool.glue.Failure, do_quit: 'Literal[True]' = True) -> NoReturn:
        pass

    @overload  # noqa
    def _handle_failure(self, failure: gluetool.glue.Failure, do_quit: 'Literal[False]' = False) -> None:  # noqa

        pass

    def _handle_failure(self, failure, do_quit=True):  # type: ignore  # noqa
        try:
            self._handle_failure_core(failure, do_quit=do_quit)

        # pylint: disable=broad-except
        except Exception:
            exc_info = sys.exc_info()

            # Don't trust anyone, the exception might have occured inside logging code, therefore
            # resorting to plain print.

            err_print = functools.partial(print, file=sys.stderr)

            err_print("""
!!! While handling an exception, another one appeared !!!

Will try to submit it to Sentry but giving up on everything else.
""")

            try:
                # pylint: disable=protected-access
                err_print(gluetool.log.LoggingFormatter._format_exception_chain(sys.exc_info()))

                # Anyway, try to submit this exception to Sentry, but be prepared for failure in case the original
                # exception was raised right in Sentry-related code.
                if self.sentry is not None:
                    self.sentry.submit_exception(Failure(None, exc_info))

            # pylint: disable=broad-except
            except Exception:
                # tripple error \o/

                err_print("""
!!! While submitting an exception to the Sentry, yet another exception appeared !!!
    Giving up on everything...
""")

                traceback.print_exc()

            # Don't use _quit() here - it might try to use complicated logger, and we don't trust
            # anythign at this point. Just die already.
            sys.exit(-1)

    @handle_exc
    def setup(self) -> None:

        self.sentry = gluetool.sentry.Sentry()
        self.tracer = gluetool.action.Tracer()

        # Python installs SIGINT handler that translates signal to
        # a KeyboardInterrupt exception. It's so good we want to use
        # it for SIGTERM as well, just wrap the handler with some logging.
        orig_sigint_handler = signal.getsignal(signal.SIGINT)
        sigmap = {getattr(signal, name): name for name in [name for name in dir(signal) if name.startswith('SIG')]}

        def _terminate_or_kill(child: psutil.Process, description: str, kill_only: bool = False) -> None:
            if kill_only:
                Glue.warn("Sending SIGKILL to {} process '{}' (PID {})".format(description, child.name(), child.pid))
                child.kill()
                return

            Glue.warn("Sending SIGTERM to {} process '{}' (PID {})".format(description, child.name(), child.pid))
            child.terminate()

            try:
                child.wait(timeout=DEFAULT_SIGTERM_TIMEOUT)

            except psutil.TimeoutExpired:
                Glue.warn("Sending SIGKILL to child process '{}' (PID {})".format(child.name(), child.pid))
                child.kill()

        def _terminate_children(kill_only: bool = False) -> None:
            process = psutil.Process()

            # Terminate child processes. For children marked by `--terminate-process-tree` terminate whole process tree.
            terminate_process_tree = gluetool.utils.normalize_multistring_option(Glue.option('terminate-process-tree'))
            for child in process.children():
                if child.name() in terminate_process_tree:
                    for process in sorted(child.children(recursive=True), key=lambda x: x.pid, reverse=True):
                        _terminate_or_kill(process, "grandchild", kill_only=kill_only)
                _terminate_or_kill(child, "child", kill_only=kill_only)

            # Terminate leftover processes in the same proccess group. For children marked by `--terminate-process-tree`
            # terminate whole process tree.
            if Glue.option('terminate-process-group-leftovers'):
                process_pgid = os.getpgid(process.pid)
                leftovers = [
                    proc for proc in psutil.process_iter(attrs=['pid'])
                    if os.getpgid(proc.pid) == process_pgid and proc.pid != process.pid
                ]
                for process in leftovers:
                    _terminate_or_kill(process, "process group leftover", kill_only=kill_only)

        def _signal_handler(signum: int,
                            frame: Optional[FrameType],
                            handler: Optional[Callable[[int, FrameType], None]] = None,
                            msg: Optional[str] = None,
                            kill_only: bool = False) -> Any:

            msg = msg or 'Signal {} received'.format(sigmap[signum])

            Glue.warn(msg)

            # Provide a flag for modules to check if they should try to finish as early as possible
            Glue.pipeline_cancelled = True

            _terminate_children(kill_only=kill_only)

            if handler is not None and frame is not None:
                return handler(signum, frame)

        def _sigusr1_handler(signum: int, frame: FrameType) -> None:
            # pylint: disable=unused-argument

            raise GlueError('Pipeline timeout expired.')

        def _sigusr2_handler(signum: int, frame: FrameType) -> None:
            # pylint: disable=unused-argument

            raise GlueError('Pipeline out-of-memory.')

        sigint_handler = functools.partial(_signal_handler,
                                           handler=orig_sigint_handler, msg='Interrupted by SIGINT (Ctrl+C?)')
        sigterm_handler = functools.partial(_signal_handler,
                                            handler=orig_sigint_handler, msg='Interrupted by SIGTERM')
        sigusr1_handler = functools.partial(_signal_handler, handler=_sigusr1_handler)
        sigusr2_handler = functools.partial(_signal_handler, handler=_sigusr2_handler, kill_only=True)

        # pylint: disable=invalid-name
        Glue = self.Glue = gluetool.glue.Glue(tool=self, sentry=self.sentry)

        # Glue is initialized, we can install our logging handlers
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigterm_handler)
        signal.signal(signal.SIGUSR1, sigusr1_handler)
        signal.signal(signal.SIGUSR2, sigusr2_handler)

        # process configuration
        Glue.parse_config(self.gluetool_config_paths)
        Glue.parse_args(sys.argv[1:])

        # store tool's configuration - everything till the start of "pipeline" (the first module)
        self.argv = [
            ensure_str(arg) for arg in sys.argv[1:len(sys.argv) - len(Glue.option('pipeline'))]
        ]

        if Glue.option('pid'):
            Glue.info('PID: {} PGID: {}'.format(os.getpid(), os.getpgrp()))

        # version
        if Glue.option('version'):
            Glue.info('gluetool {}'.format(self._version))
            sys.exit(0)

        GlueError.no_sentry_exceptions = normalize_multistring_option(Glue.option('no-sentry-exceptions'))

        Glue.modules = Glue.discover_modules()

    @handle_exc
    def check_options(self) -> None:

        Glue = self.Glue
        assert Glue is not None

        self.pipeline_desc = self._deduce_pipeline_desc(Glue.option('pipeline'), list(iterkeys(Glue.modules)))
        log_dict(Glue.debug, 'pipeline description', self.pipeline_desc)

        # list modules
        groups = Glue.option('list-modules')
        if groups == [True]:
            sys.stdout.write('%s\n' % Glue.modules_descriptions())
            sys.exit(0)

        elif groups:
            sys.stdout.write('%s\n' % Glue.modules_descriptions(groups=groups))
            sys.exit(0)

        if Glue.option('list-shared'):
            functions: List[List[str]] = []

            for mod_name in sorted(iterkeys(Glue.modules)):
                functions += [
                    [func_name, mod_name] for func_name in Glue.modules[mod_name].klass.shared_functions
                ]

            if functions:
                functions = sorted(functions, key=lambda row: row[0])
            else:
                functions = [['-- no shared functions available --', '']]

            sys.stdout.write("""Available shared functions

{}
            """.format(tabulate.tabulate(functions, ['Shared function', 'Module name'], tablefmt='simple')))

            sys.exit(0)

        if Glue.option('list-eval-context'):
            variables = []

            def _add_variables(source: gluetool.glue.Configurable) -> None:
                assert source.name is not None

                info = extract_eval_context_info(source)

                for name, description in iteritems(info):
                    variables.append([
                        name, source.name, docstring_to_help(description, line_prefix='')
                    ])

            for mod_name in sorted(iterkeys(Glue.modules)):
                _add_variables(Glue.init_module(mod_name))

            _add_variables(Glue)

            if variables:
                variables = sorted(variables, key=lambda row: row[0])

            else:
                variables = [['-- no variables available --', '', '']]

            table = tabulate.tabulate(variables, ['Variable', 'Module name', 'Description'], tablefmt='simple')

            print(render_template("""
{{ '** Variables available in eval context **' | style(fg='yellow') }}

{{ TABLE }}
            """, TABLE=table))

            sys.exit(0)

    @handle_exc
    def run_pipeline(self) -> PipelineReturnType:

        Glue = self.Glue
        assert Glue is not None

        # no modules
        if not self.pipeline_desc:
            raise GlueError('No module specified, use -l to list available')

        # command-line info
        if Glue.option('info'):
            assert self.argv is not None

            self.log_cmdline(self.argv, self.pipeline_desc)

        # actually the execution loop is retries+1
        # there is always one execution
        retries = Glue.option('retries')

        for loop_number in range(retries + 1):
            # Print retry info
            if loop_number:
                Glue.warning('retrying execution (attempt #{} out of {})'.format(loop_number, retries))

            # Run the pipeline
            failure, destroy_failure = Glue.run_modules(self.pipeline_desc)

            if destroy_failure:
                return failure, destroy_failure

            if failure and isinstance(failure.exception, GlueRetryError):
                Glue.error(str(failure.exception))
                continue

            return failure, destroy_failure

        return None, None

    def main(self) -> None:

        self.setup()
        self.check_options()

        failure, destroy_failure = self.run_pipeline()

        if destroy_failure:
            if failure:
                self._handle_failure(failure, do_quit=False)

            self._exit_logger.warning('Exception raised when destroying modules, overriding exit status')

            self._handle_failure(destroy_failure)

        if failure:
            self._handle_failure(failure)

        self._quit(0)


def main() -> None:

    app = Gluetool()
    app.main()
