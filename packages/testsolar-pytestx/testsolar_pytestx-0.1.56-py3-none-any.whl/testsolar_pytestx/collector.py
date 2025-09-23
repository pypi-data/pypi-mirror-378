import os
import sys
import traceback
from collections import defaultdict
from pathlib import Path
from typing import BinaryIO, Sequence, Optional, List, Dict, Union, Callable

from pytest import Item, Collector

try:
    from pytest import CollectReport
except ImportError:
    from _pytest.reports import CollectReport  # 兼容pytest低版本

from testsolar_testtool_sdk.model.load import LoadResult, LoadError
from testsolar_testtool_sdk.model.param import EntryParam
from testsolar_testtool_sdk.model.test import TestCase
from testsolar_testtool_sdk.reporter import Reporter

from .converter import selector_to_pytest, pytest_to_selector, CASE_DRIVE_SEPARATOR
from .filter import filter_invalid_selector_path
from .parser import parse_case_attributes
from .util import append_extra_args
from .stream import pytest_main_with_output


class PytestCollector:
    def __init__(self, pipe_io: Optional[BinaryIO] = None):
        self.collected: List[Item] = []
        self.errors: Dict[str, str] = {}
        self.reporter: Reporter = Reporter(pipe_io=pipe_io)

    def pytest_collection_modifyitems(self, items: Sequence[Union[Item, Collector]]) -> None:
        for item in items:
            if isinstance(item, Item):
                self.collected.append(item)

    def pytest_collectreport(self, report: CollectReport) -> None:
        if report.failed:
            path = report.fspath
            if path in self.errors:
                return
            path = os.path.splitext(path)[0].replace(os.path.sep, ".")
            try:
                __import__(path)
            except Exception as e:
                print(e)
                self.errors[report.fspath] = traceback.format_exc()

    def pytest_collection_finish(self, session) -> None:  # type: ignore
        """
        在pytest_collection_modifyitems没有被调用的情况下兜底执行.
        """
        if not self.collected:
            for item in session.items:
                if isinstance(item, Item):
                    self.collected.append(item)

    def pytest_internalerror(self, excrepr) -> None:  # type: ignore
        if (
            excrepr.reprcrash
            and excrepr.reprcrash.path
            and excrepr.reprtraceback
            and excrepr.reprtraceback.reprentries
        ):
            self.errors[excrepr.reprcrash.path] = "\n".join(
                excrepr.reprtraceback.reprentries[0].lines
            )


def collect_testcases(
    entry_param: EntryParam,
    pipe_io: Optional[BinaryIO] = None,
    case_comment_fields: Optional[List[str]] = None,
    extra_load_function: Optional[Callable[[str, LoadResult, Dict[str, List[str]]], None]] = None,
) -> None:
    if entry_param.ProjectPath not in sys.path:
        sys.path.insert(0, entry_param.ProjectPath)

    show_workspace_files(entry_param.ProjectPath)

    load_result: LoadResult = LoadResult(
        Tests=[],
        LoadErrors=[],
    )

    valid_selectors, load_errors = filter_invalid_selector_path(
        workspace=entry_param.ProjectPath,
        selectors=entry_param.TestSelectors,
    )

    load_result.LoadErrors.extend(load_errors)

    case_drive_records: Dict[str, List[str]] = defaultdict(list)
    pytest_paths: List[str] = []
    for selector in valid_selectors:
        # 扫描用例是否是基础用例，如果是存入 case_drive_records，方便后续扩展
        if CASE_DRIVE_SEPARATOR in selector:
            case_name, _, drive_key = selector.partition(CASE_DRIVE_SEPARATOR)
            case_drive_records[case_name].append(drive_key)

            pytest_paths.append(selector_to_pytest(test_selector=case_name))
        else:
            pytest_paths.append(selector_to_pytest(test_selector=selector))

    testcase_list = [os.path.join(entry_param.ProjectPath, it) for it in pytest_paths if it]

    my_plugin = PytestCollector(pipe_io)
    args = [
        f"--rootdir={entry_param.ProjectPath}",
        "--collect-only",
        "--continue-on-collection-errors",
        "-v",
        "--trace-config",
    ]
    append_extra_args(args)

    args.extend(testcase_list)
    print(f"[Load] try to collect testcases: {args}")
    _, captured_stderr, exit_code = pytest_main_with_output(args=args, plugin=my_plugin)
    if exit_code != 0:
        # 若加载用例失败，则将本批次的用例结果统一作为loaderror上报，并将标准错误流作为用例错误日志上报
        print(f"[Warn][Load] collect testcases exit_code: {exit_code}")
        if len(my_plugin.collected) == 0 and len(my_plugin.errors.items()) == 0:
            for selector in valid_selectors:
                load_result.LoadErrors.append(
                    LoadError(
                        name=selector,
                        message=captured_stderr,
                    )
                )

    for item in my_plugin.collected:
        full_name = pytest_to_selector(item, entry_param.ProjectPath)
        attributes = parse_case_attributes(item, case_comment_fields)
        load_result.Tests.append(TestCase(Name=full_name, Attributes=attributes))

    # 增加额外功能，方便外部接入
    if extra_load_function:
        extra_load_function(entry_param.ProjectPath, load_result, case_drive_records)

    for k, v in my_plugin.errors.items():
        load_result.LoadErrors.append(
            LoadError(
                name=k,
                message=v,
            )
        )

    print(f"[Load] collect testcase count: {len(load_result.Tests)}")
    print(f"[Load] collect load error count: {len(load_result.LoadErrors)}")

    reporter = Reporter(pipe_io=pipe_io)
    reporter.report_load_result(load_result)


def show_workspace_files(workdir: str) -> None:
    print()
    print(f"Workspace [{workdir}] files:")
    for item in Path(workdir).iterdir():
        if item.is_file():
            print(f" - {item}")

    print()
