from collections import deque
import json
import os
from pathlib import Path
import traceback
import time
from typing import Callable, Any, Deque, Dict, List, Literal, NewType, Union
from unittest import TextTestRunner, registerResult, TestSuite, TestCase, TextTestResult
import random
import warnings
from dataclasses import dataclass, asdict
from kea2.absDriver import AbstractDriver
from functools import wraps
from kea2.bug_report_generator import BugReportGenerator
from kea2.resultSyncer import ResultSyncer
from kea2.logWatcher import LogWatcher
from kea2.utils import TimeStamp, catchException, getProjectRoot, getLogger, timer
from kea2.u2Driver import StaticU2UiObject, StaticXpathUiObject
from kea2.fastbotManager import FastbotManager
from kea2.adbUtils import ADBDevice
import uiautomator2 as u2
import types

PRECONDITIONS_MARKER = "preconds"
PROP_MARKER = "prop"
MAX_TRIES_MARKER = "max_tries"

logger = getLogger(__name__)


# Class Typing
PropName = NewType("PropName", str)
PropertyStore = NewType("PropertyStore", Dict[PropName, TestCase])


STAMP = TimeStamp().getTimeStamp()
LOGFILE: str
RESFILE: str
PROP_EXEC_RESFILE: str

def precondition(precond: Callable[[Any], bool]) -> Callable:
    """the decorator @precondition

    @precondition specifies when the property could be executed.
    A property could have multiple preconditions, each of which is specified by @precondition.
    """
    def accept(f):
        @wraps(f)
        def precondition_wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        preconds = getattr(f, PRECONDITIONS_MARKER, tuple())

        setattr(precondition_wrapper, PRECONDITIONS_MARKER, preconds + (precond,))

        return precondition_wrapper

    return accept

def prob(p: float):
    """the decorator @prob

    @prob specify the propbability of execution when a property is satisfied.
    """
    p = float(p)
    if not 0 < p <= 1.0:
        raise ValueError("The propbability should between 0 and 1")
    def accept(f):
        @wraps(f)
        def precondition_wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        setattr(precondition_wrapper, PROP_MARKER, p)

        return precondition_wrapper

    return accept


def max_tries(n: int):
    """the decorator @max_tries

    @max_tries specify the maximum tries of executing a property.
    """
    n = int(n)
    if not n > 0:
        raise ValueError("The maxium tries should be a positive integer.")
    def accept(f):
        @wraps(f)
        def precondition_wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        setattr(precondition_wrapper, MAX_TRIES_MARKER, n)

        return precondition_wrapper

    return accept


@dataclass
class Options:
    """
    Kea and Fastbot configurations
    """
    # the driver_name in script (if self.d, then d.) 
    driverName: str
    # the driver (only U2Driver available now)
    Driver: AbstractDriver
    # list of package names. Specify the apps under test
    packageNames: List[str]
    # target device
    serial: str = None
    # target device with transport_id
    transport_id: str = None
    # test agent. "native" for stage 1 and "u2" for stage 1~3
    agent: Literal["u2", "native"] = "u2"
    # max step in exploration (availble in stage 2~3)
    maxStep: Union[str, float] = float("inf")
    # time(mins) for exploration
    running_mins: int = 10
    # time(ms) to wait when exploring the app
    throttle: int = 200
    # the output_dir for saving logs and results
    output_dir: str = "output"
    # the stamp for log file and result file, default: current time stamp
    log_stamp: str = None
    # the profiling period to get the coverage result.
    profile_period: int = 25
    # take screenshots for every step
    take_screenshots: bool = False
    # The root of output dir on device
    device_output_root: str = "/sdcard"
    # the debug mode
    debug: bool = False
    # Activity WhiteList File
    act_whitelist_file: str = None
    # Activity BlackList File
    act_blacklist_file: str = None
    # Extra args
    extra_args: List[str] = None

    def __setattr__(self, name, value):
        if value is None:
            return
        super().__setattr__(name, value)

    def __post_init__(self):
        import logging
        logging.basicConfig(level=logging.DEBUG if self.debug else logging.INFO)
        
        if self.Driver:
            target_device = dict()
            if self.serial:
                target_device["serial"] = self.serial
            if self.transport_id:
                target_device["transport_id"] = self.transport_id
            self.Driver.setDevice(target_device)
            ADBDevice.setDevice(self.serial, self.transport_id)
            
        global LOGFILE, RESFILE, PROP_EXEC_RESFILE, STAMP
        if self.log_stamp:
            illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\n', '\r', '\t', '\0']
            for char in illegal_chars:
                if char in self.log_stamp:
                    raise ValueError(
                        f"char: `{char}` is illegal in --log-stamp. current stamp: {self.log_stamp}"
                    )
            STAMP = self.log_stamp
        
        self.log_stamp = STAMP
            
        self.output_dir = Path(self.output_dir).absolute() / f"res_{STAMP}"
        LOGFILE = f"fastbot_{STAMP}.log"
        RESFILE = f"result_{STAMP}.json"
        PROP_EXEC_RESFILE = f"property_exec_info_{STAMP}.json"

        self.profile_period = int(self.profile_period)
        if self.profile_period < 1:
            raise ValueError("--profile-period should be greater than 0")

        self.throttle = int(self.throttle)
        if self.throttle < 0:
            raise ValueError("--throttle should be greater than or equal to 0")

        _check_package_installation(self.packageNames)


def _check_package_installation(packageNames):
    installed_packages = set(ADBDevice().list_packages())

    for package in packageNames:
        if package not in installed_packages:
            logger.error(f"package {package} not installed. Abort.")
            raise ValueError("package not installed")


@dataclass
class PropStatistic:
    precond_satisfied: int = 0
    executed: int = 0
    fail: int = 0
    error: int = 0
    

PBTTestResult = NewType("PBTTestResult", Dict[PropName, PropStatistic])


PropertyExecutionInfoStore = NewType("PropertyExecutionInfoStore", Deque["PropertyExecutionInfo"])
@dataclass
class PropertyExecutionInfo:
    startStepsCount: int
    propName: PropName
    state: Literal["start", "pass", "fail", "error"]
    tb: str


def getFullPropName(testCase: TestCase):
    return ".".join([
        testCase.__module__,
        testCase.__class__.__name__,
        testCase._testMethodName
    ])


class JsonResult(TextTestResult):
    
    res: PBTTestResult
    lastExecutedInfo: PropertyExecutionInfo
    executionInfoStore: PropertyExecutionInfoStore = deque()

    @classmethod
    def setProperties(cls, allProperties: Dict):
        cls.res = dict()
        for testCase in allProperties.values():
            cls.res[getFullPropName(testCase)] = PropStatistic()

    def flushResult(self):
        global RESFILE, PROP_EXEC_RESFILE
        json_res = dict()
        for propName, propStatitic in self.res.items():
            json_res[propName] = asdict(propStatitic)
        with open(RESFILE, "w", encoding="utf-8") as fp:
            json.dump(json_res, fp, indent=4)

        while self.executionInfoStore:
            execInfo = self.executionInfoStore.popleft()
            with open(PROP_EXEC_RESFILE, "a", encoding="utf-8") as fp:
                fp.write(f"{json.dumps(asdict(execInfo))}\n")

    def addExcuted(self, test: TestCase, stepsCount: int):
        self.res[getFullPropName(test)].executed += 1

        self.lastExecutedInfo = PropertyExecutionInfo(
            propName=getFullPropName(test),
            state="start",
            tb="",
            startStepsCount=stepsCount
        )

    def addPrecondSatisfied(self, test: TestCase):
        self.res[getFullPropName(test)].precond_satisfied += 1

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.res[getFullPropName(test)].fail += 1
        self.lastExecutedInfo.state = "fail"
        self.lastExecutedInfo.tb = self._exc_info_to_string(err, test)

    def addError(self, test, err):
        super().addError(test, err)
        self.res[getFullPropName(test)].error += 1
        self.lastExecutedInfo.state = "error"
        self.lastExecutedInfo.tb = self._exc_info_to_string(err, test)

    def updateExectedInfo(self):
        if self.lastExecutedInfo.state == "start":
            self.lastExecutedInfo.state = "pass"

        self.executionInfoStore.append(self.lastExecutedInfo)

    def getExcuted(self, test: TestCase):
        return self.res[getFullPropName(test)].executed
    
    def logSummary(self):
        fails = sum(_.fail for _ in self.res.values())
        errors = sum(_.error for _ in self.res.values())

        logger.info(f"[Property Exectution Summary] Errors:{errors}, Fails:{fails}")


class KeaTestRunner(TextTestRunner):

    resultclass: JsonResult
    allProperties: PropertyStore
    options: Options = None
    _block_funcs: Dict[Literal["widgets", "trees"], List[Callable]] = None

    @classmethod
    def setOptions(cls, options: Options):
        if not isinstance(options.packageNames, list) and len(options.packageNames) > 0:
            raise ValueError("packageNames should be given in a list.")
        if options.Driver is not None and options.agent == "native":
            logger.warning("[Warning] Can not use any Driver when runing native mode.")
            options.Driver = None
        cls.options = options

    def _setOuputDir(self):
        output_dir = Path(self.options.output_dir).absolute()
        output_dir.mkdir(parents=True, exist_ok=True)
        global LOGFILE, RESFILE, PROP_EXEC_RESFILE
        LOGFILE = output_dir / Path(LOGFILE)
        RESFILE = output_dir / Path(RESFILE)
        PROP_EXEC_RESFILE = output_dir / Path(PROP_EXEC_RESFILE)
        logger.info(f"Log file: {LOGFILE}")
        logger.info(f"Result file: {RESFILE}")
        logger.info(f"Property execution info file: {PROP_EXEC_RESFILE}")

    def run(self, test):

        self.allProperties = dict()
        self.collectAllProperties(test)

        if len(self.allProperties) == 0:
            logger.warning("[Warning] No property has been found.")

        self._setOuputDir()

        JsonResult.setProperties(self.allProperties)
        self.resultclass = JsonResult

        result: JsonResult = self._makeResult()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        result.tb_locals = self.tb_locals

        with warnings.catch_warnings():
            if self.warnings:
                # if self.warnings is set, use it to filter all the warnings
                warnings.simplefilter(self.warnings)
                # if the filter is 'default' or 'always', special-case the
                # warnings from the deprecated unittest methods to show them
                # no more than once per module, because they can be fairly
                # noisy.  The -Wd and -Wa flags can be used to bypass this
                # only when self.warnings is None.
                if self.warnings in ["default", "always"]:
                    warnings.filterwarnings(
                        "module",
                        category=DeprecationWarning,
                        message=r"Please use assert\w+ instead.",
                    )

            fb = FastbotManager(self.options, LOGFILE)
            fb.start()

            log_watcher = LogWatcher(LOGFILE)
            
            if self.options.agent == "u2":
                # initialize the result.json file
                result.flushResult()
                # setUp for the u2 driver
                self.scriptDriver = self.options.Driver.getScriptDriver()
                fb.check_alive()
                
                fb.init(options=self.options, stamp=STAMP)

                resultSyncer = ResultSyncer(fb.device_output_dir, self.options)
                resultSyncer.run()

                end_by_remote = False
                self.stepsCount = 0
                while self.stepsCount < self.options.maxStep:

                    self.stepsCount += 1
                    logger.info("Sending monkeyEvent {}".format(
                        f"({self.stepsCount} / {self.options.maxStep})" if self.options.maxStep != float("inf")
                        else f"({self.stepsCount})"
                        )
                    )

                    try:
                        xml_raw = fb.stepMonkey(self._monkeyStepInfo)
                        propsSatisfiedPrecond = self.getValidProperties(xml_raw, result)
                    except u2.HTTPError:
                        logger.info("Connection refused by remote.")
                        if fb.get_return_code() == 0:
                            logger.info("Exploration times up (--running-minutes).")
                            end_by_remote = True
                            break
                        raise RuntimeError("Fastbot Aborted.")

                    if self.options.profile_period and self.stepsCount % self.options.profile_period == 0:
                        resultSyncer.sync_event.set()

                    # Go to the next round if no precond satisfied
                    if len(propsSatisfiedPrecond) == 0:
                        continue

                    # get the random probability p
                    p = random.random()
                    propsNameFilteredByP = []
                    # filter the properties according to the given p
                    for propName, test in propsSatisfiedPrecond.items():
                        result.addPrecondSatisfied(test)
                        if getattr(test, "p", 1) >= p:
                            propsNameFilteredByP.append(propName)

                    if len(propsNameFilteredByP) == 0:
                        print("Not executed any property due to probability.", flush=True)
                        continue

                    execPropName = random.choice(propsNameFilteredByP)
                    test = propsSatisfiedPrecond[execPropName]
                    # Dependency Injection. driver when doing scripts
                    self.scriptDriver = self.options.Driver.getScriptDriver()
                    setattr(test, self.options.driverName, self.scriptDriver)
                    print("execute property %s." % execPropName, flush=True)

                    result.addExcuted(test, self.stepsCount)
                    fb.logScript(result.lastExecutedInfo)
                    try:
                        test(result)
                    finally:
                        result.printErrors()

                    result.updateExectedInfo()
                    fb.logScript(result.lastExecutedInfo)
                    result.flushResult()

                if not end_by_remote:
                    fb.stopMonkey()
                result.flushResult()
                resultSyncer.close()
                
            fb.join()
            print(f"Finish sending monkey events.", flush=True)
            log_watcher.close()

        # Source code from unittest Runner
        # process the result
        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(
                len,
                (result.expectedFailures, result.unexpectedSuccesses, result.skipped),
            )
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        if not result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = len(result.failures), len(result.errors)
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        self.stream.flush()
        
        result.logSummary()
        return result

    @property
    def _monkeyStepInfo(self):
        r = self._get_block_widgets()
        r["steps_count"] = self.stepsCount
        return r
    
    def _get_block_widgets(self):
        block_dict = self._getBlockedWidgets()
        block_widgets: List[str] = block_dict['widgets']
        block_trees: List[str] = block_dict['trees']
        logger.debug(f"Blocking widgets: {block_widgets}")
        logger.debug(f"Blocking trees: {block_trees}")
        return {
            "block_widgets": block_widgets,
            "block_trees": block_trees
        }

    def getValidProperties(self, xml_raw: str, result: JsonResult) -> PropertyStore:

        staticCheckerDriver = self.options.Driver.getStaticChecker(hierarchy=xml_raw)

        validProps: PropertyStore = dict()
        for propName, test in self.allProperties.items():
            valid = True
            prop = getattr(test, propName)
            # check if all preconds passed
            for precond in prop.preconds:
                # Dependency injection. Static driver checker for precond
                setattr(test, self.options.driverName, staticCheckerDriver)
                # excecute the precond
                try:
                    if not precond(test):
                        valid = False
                        break
                except u2.UiObjectNotFoundError as e:
                    valid = False
                    break
                except Exception as e:
                    logger.error(f"Error when checking precond: {getFullPropName(test)}")
                    traceback.print_exc()
                    valid = False
                    break
            # if all the precond passed. make it the candidate prop.
            if valid:
                if result.getExcuted(test) >= getattr(prop, MAX_TRIES_MARKER, float("inf")):
                    print(f"{getFullPropName(test)} has reached its max_tries. Skip.", flush=True)
                    continue
                validProps[propName] = test

        print(f"{len(validProps)} precond satisfied.", flush=True)
        if len(validProps) > 0:
            print("[INFO] Valid properties:",flush=True)
            print("\n".join([f'                - {getFullPropName(p)}' for p in validProps.values()]), flush=True)
        return validProps

    def collectAllProperties(self, test: TestSuite):
        """collect all the properties to prepare for PBT
        """

        def remove_setUp(testCase: TestCase):
            """remove the setup function in PBT
            """
            def setUp(self): ...
            testCase.setUp = types.MethodType(setUp, testCase)

        def remove_tearDown(testCase: TestCase):
            """remove the tearDown function in PBT
            """
            def tearDown(self): ...
            testCase.tearDown = types.MethodType(tearDown, testCase)

        def iter_tests(suite):
            for test in suite:
                if isinstance(test, TestSuite):
                    yield from iter_tests(test)
                else:
                    yield test

        # Traverse the TestCase to get all properties
        for t in iter_tests(test):
            testMethodName = t._testMethodName
            # get the test method name and check if it's a property
            testMethod = getattr(t, testMethodName)
            if hasattr(testMethod, PRECONDITIONS_MARKER):
                # remove the hook func in its TestCase
                remove_setUp(t)
                remove_tearDown(t)
                # save it into allProperties for PBT
                self.allProperties[testMethodName] = t
                print(f"[INFO] Load property: {getFullPropName(t)}", flush=True)

    @property
    def _blockWidgetFuncs(self):
        """
        load and process blocking functions from widget.block.py configuration file.

        Returns:
            dict: A dictionary containing two lists:
                - 'widgets': List of functions that block individual widgets
                - 'trees': List of functions that block widget trees
        """
        if self._block_funcs is None:
            self._block_funcs = {"widgets": list(), "trees": list()}
            root_dir = getProjectRoot()
            if root_dir is None or not os.path.exists(
                    file_block_widgets := root_dir / "configs" / "widget.block.py"
            ):
                print(f"[WARNING] widget.block.py not find", flush=True)

            def __get_block_widgets_module():
                import importlib.util
                module_name = "block_widgets"
                spec = importlib.util.spec_from_file_location(module_name, file_block_widgets)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod

            mod = __get_block_widgets_module()

            import inspect
            for func_name, func in inspect.getmembers(mod, inspect.isfunction):
                if func_name == "global_block_widgets":
                    self._block_funcs["widgets"].append(func)
                    setattr(func, PRECONDITIONS_MARKER, (lambda d: True,))
                    continue
                if func_name == "global_block_tree":
                    self._block_funcs["trees"].append(func)
                    setattr(func, PRECONDITIONS_MARKER, (lambda d: True,))
                    continue
                if func_name.startswith("block_") and not func_name.startswith("block_tree_"):
                    if getattr(func, PRECONDITIONS_MARKER, None) is None:
                        logger.warning(f"No precondition in block widget function: {func_name}. Default globally active.")
                        setattr(func, PRECONDITIONS_MARKER, (lambda d: True,))
                    self._block_funcs["widgets"].append(func)
                    continue
                if func_name.startswith("block_tree_"):
                    if getattr(func, PRECONDITIONS_MARKER, None) is None:
                        logger.warning(f"No precondition in block tree function: {func_name}. Default globally active.")
                        setattr(func, PRECONDITIONS_MARKER, (lambda d: True,))
                    self._block_funcs["trees"].append(func)

        return self._block_funcs


    def _getBlockedWidgets(self):
        """
           Executes all blocking functions to get lists of widgets and trees to be blocked during testing.

           Returns:
               dict: A dictionary containing:
                   - 'widgets': List of XPath strings for individual widgets to block
                   - 'trees': List of XPath strings for widget trees to block
           """
        def _get_xpath_widgets(func):
            blocked_set = set()
            script_driver = self.options.Driver.getScriptDriver()
            preconds = getattr(func, PRECONDITIONS_MARKER, [])

            def preconds_pass(preconds):
                try:
                    return all(precond(script_driver) for precond in preconds)
                except u2.UiObjectNotFoundError as e:
                    return False
                except Exception as e:
                    logger.error(f"Error processing precond. Check if precond: {e}")
                    traceback.print_exc()
                    return False

            if preconds_pass(preconds):
                try:
                    _widgets = func(self.options.Driver.getStaticChecker())
                    _widgets = _widgets if isinstance(_widgets, list) else [_widgets]
                    for w in _widgets:
                        if isinstance(w, (StaticU2UiObject, StaticXpathUiObject)):
                            xpath = w.selector_to_xpath(w.selector)
                            if xpath != '//error':
                                blocked_set.add(xpath)
                        else:
                            logger.error(f"block widget defined in {func.__name__} Not supported.")
                except Exception as e:
                    logger.error(f"Error processing blocked widgets in: {func}")
                    logger.error(e)
                    traceback.print_exc()
            return blocked_set

        result = {
            "widgets": set(),
            "trees": set()
        }

        for func in self._blockWidgetFuncs["widgets"]:
            widgets = _get_xpath_widgets(func)
            result["widgets"].update(widgets)

        for func in self._blockWidgetFuncs["trees"]:
            trees = _get_xpath_widgets(func)
            result["trees"].update(trees)

        result["widgets"] = list(result["widgets"] - result["trees"])
        result["trees"] = list(result["trees"])

        return result

    @timer(r"Generating bug report cost %cost_time seconds.")
    @catchException("Error when generating bug report")
    def _generate_bug_report(self):
        logger.info("Generating bug report")
        report_generator = BugReportGenerator(self.options.output_dir)
        report_generator.generate_report()

    def __del__(self):
        """tearDown method. Cleanup the env.
        """
        if self.options.Driver:
            self.options.Driver.tearDown()

        self._generate_bug_report()
