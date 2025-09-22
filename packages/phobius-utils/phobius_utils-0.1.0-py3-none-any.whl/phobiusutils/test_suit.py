from metautils import Log
import concurrent.futures
import time


class TestSuit:
    _LOG = Log("TestSuit")  # no change

    def __init__(self):
        self._cases = []
    """
    Executes all added test cases in the suite.

    This method runs each test sequentially, invoking the associated function or code block 
    with its specified arguments and comparing the result to the expected output.

    If a timeout is defined for a test case, execution will be limited to that duration. 
    Any exceptions or mismatches will be captured and reported accordingly.

    Returns
    -------
    None
    """
    def run(self):
        for test_case in self._cases:
            test_case.run()

    def add(
        self,
        name: str,
        func: callable,
        expect,
        args: tuple = (),
        kwargs={},
        timeout: float | None = None,
    ):
        """
        Adds a test case to the TestSuite.

        Parameters
        ----------
        name : str
            A descriptive name for the test case. Used for reporting and logging purposes.

        func : callable or str
            The function or code block to be tested. Can be:
            - A regular function, lambda, class method, or any callable object.
            - A string of Python code (multi-line allowed), which will be automatically wrapped and executed.

        expect : Any
            The expected result. It will be compared against the actual return value of `func`
            to determine if the test passes.

        args : tuple, optional
            Positional arguments to pass to the function. Defaults to an empty tuple.

        kwargs : dict, optional
            Keyword arguments to pass to the function. Defaults to an empty dictionary.

        timeout : float or None, optional
            Maximum number of seconds to allow the function to run. If exceeded, the test will fail
            with a timeout error. If None, no timeout is applied.

        Returns
        -------
        None

        Notes
        -----
        This method does not run the test immediately. All added tests will be executed when
        `TestSuite.run()` is called.
        """
        try:
            self._cases.append(
                self.TestCase(
                    name=name,
                    func=func,
                    expect=expect,
                    args=args,
                    kwargs=kwargs,
                    timeout=timeout,
                    log=self._LOG,
                )
            )
        except Exception as e:
            self._LOG.critical(
                f"TestSuit.add> Failed when adding function {name} [because: {e}]"
            )
    #
    class TestCase:
        def __init__(self, name, func, expect, args, kwargs, timeout, log: Log):
            self.name = name
            self.func = func
            self.expect = expect
            self.args = args
            self.kwargs = kwargs
            self.timeout = timeout
            self.log = log

        def run(self):
            start_time = time.time()
            passed = False
            result = None
            try:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self.func, *self.args, **self.kwargs)
                    result = future.result(timeout=self.timeout)
                    passed = result == self.expect
                #
                self.log.info(
                    f"Function {self.name} [success: {passed}] with [result: {result}] in {time.time() - start_time:.3f} seconds"
                )
            except concurrent.futures.TimeoutError:
                self.log.error(
                    f"Function {self.name} timeout when running after {self.timeout} seconds"
                )
            except Exception as e:
                self.log.error(f"Function {self.name} has exeption {e} when running")
