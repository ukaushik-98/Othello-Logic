# project4_sanitycheck.py
# (Last Updated: 2017-11-14)
#
# ICS 32 Fall 2017
# Project #4: The Width of a Circle (Part 1)
#
# This is a sanity checker for your Project #4 solution, which checks whether
# your solution meets some basic requirements with respect to reading input
# and formatting its output, as well as verifying that at least one game can
# be played all the way to completion.
#
# In order for the sanity check to run successfully, you'll need to meet
# these requirements:
#
# * Exactly one of your modules is executable (i.e., contains an "if __name__
#   == '__main__':" block).
# * It's possible to run the program by executing that module
# * Your program begins by printing the word FULL or the word SIMPLE, alone
#   on a line, before it does anything else
# * Your program generates the correct output for one scenario, similar to
#   the one shown in the project write-up
#
# If your program is unable to pass this sanity checker, it will certainly be
# unable to pass all of our automated tests (and it may well fail all of them).
# On the other hand, there are other tests you'll want to run besides the one
# scenario here, because we'll be testing more than just one when we grade
# your work.
#
# YOU DO NOT NEED TO READ OR UNDERSTAND THIS CODE, though you can certainly
# feel free to take a look at it.

import pathlib
import queue
import subprocess
import sys
import threading
import time
import traceback
import typing



SANITY_CHECK_FILENAME = 'project4_sanitycheck.py'



class TextProcessReadTimeout(Exception):
    pass



class TextProcess:
    _READ_INTERVAL_IN_SECONDS = 0.025


    def __init__(self, args: [str], working_directory: str):
        self._process = subprocess.Popen(
            args, cwd = working_directory, bufsize = 0,
            stdin = subprocess.PIPE, stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT)

        self._stdout_read_trigger = queue.Queue()
        self._stdout_buffer = queue.Queue()

        self._stdout_thread = threading.Thread(
            target = self._stdout_read_loop, daemon = True)

        self._stdout_thread.start()


    def __enter__(self):
        return self


    def __exit__(self, tr, exc, val):
        self.close()


    def close(self):
        self._stdout_read_trigger.put('stop')
        self._process.terminate()
        self._process.wait()
        self._process.stdout.close()
        self._process.stdin.close()


    def write_line(self, line: str) -> None:
        try:
            self._process.stdin.write((line + '\n').encode(encoding = 'utf-8'))
            self._process.stdin.flush()

        except OSError:
            pass


    def read_line(self, timeout: float = None) -> str or None:
        self._stdout_read_trigger.put('read')
        
        sleep_time = 0
        
        while timeout == None or sleep_time < timeout:
            try:
                next_result = self._stdout_buffer.get_nowait()

                if next_result == None:
                    return None
                elif isinstance(next_result, Exception):
                    raise next_result
                else:
                    return next_result.decode(encoding = 'utf-8')

            except queue.Empty:
                time.sleep(TextProcess._READ_INTERVAL_IN_SECONDS)
                sleep_time += TextProcess._READ_INTERVAL_IN_SECONDS

        raise TextProcessReadTimeout()


    def _stdout_read_loop(self):
        try:
            while self._process.returncode == None:
                if self._stdout_read_trigger.get() == 'read':
                    line = self._process.stdout.readline()

                    if line == b'':
                        self._stdout_buffer.put(None)
                    else:
                        self._stdout_buffer.put(line)
                else:
                    break

        except Exception as e:
            self._stdout_buffer.put(e)



class TestFailure(Exception):
    pass



class TestInputLine:
    def __init__(self, text: str):
        self._text = text

    
    def execute(self, process: TextProcess) -> None:
        try:
            process.write_line(self._text)

        except Exception as e:
            print_labeled_output(
                'EXCEPTION',
                *[tb_line.rstrip() for tb_line in traceback.format_exc().split('\n')])

            raise TestFailure()

        print_labeled_output('INPUT', self._text)



class TestOutputLine:
    def __init__(self, text: str, timeout_in_seconds: float):
        self._text = text
        self._timeout_in_seconds = timeout_in_seconds


    def execute(self, process: TextProcess) -> None:
        try:
            output_line = process.read_line(self._timeout_in_seconds)

        except TextProcessReadTimeout:
            output_line = None

        except Exception as e:
            print_labeled_output(
                'EXCEPTION',
                [tb_line.rstrip() for tb_line in traceback.format_exc().split('\n')])

            raise TestFailure()

        if output_line != None:
            if output_line.endswith('\r\n'):
                output_line = output_line[:-2]
            elif output_line.endswith('\n'):
                output_line = output_line[:-1]

            print_labeled_output('OUTPUT', output_line)

            if output_line != self._text:
                print_labeled_output('EXPECTED', self._text)

                index = min(len(output_line), len(self._text))

                for i in range(min(len(output_line), len(self._text))):
                    if output_line[i] != self._text[i]:
                        index = i
                        break

                print_labeled_output('', (' ' * index) + '^')

                print_labeled_output(
                    'ERROR',
                    'This line of output did not match what was expected.  The first',
                    'incorrect character is marked with a ^ above.',
                    '(If you don\'t see a difference, perhaps your program printed',
                    'extra whitespace on the end of this line.)')

                raise TestFailure()

        else:
            print_labeled_output('EXPECTED', self._text)

            print_labeled_output(
                'ERROR',
                'This line of output was expected, but the program did not generate',
                'any additional output after waiting for {} second(s).'.format(self._timeout_in_seconds))

            raise TestFailure()



class TestEndOfOutput:
    def __init__(self, timeout_in_seconds: float):
        self._timeout_in_seconds = timeout_in_seconds


    def execute(self, process: TextProcess) -> None:
        output_line = process.read_line(self._timeout_in_seconds)

        if output_line != None:
            print_labeled_output('OUTPUT', output_line)

            print_labeled_output(
                'ERROR',
                'Extra output was printed after the program should not have generated',
                'any additional output')

            raise TestFailure()



def run_test() -> None:
    process = None

    try:
        process = start_process()
        test_lines = make_test_lines(process)
        run_test_lines(process, test_lines)

        print_labeled_output(
            'PASSED',
            'Your Project #4 implementation passed the sanity checker.  Note that',
            'there are many other tests you\'ll want to run on your own, because',
            'a number of other scenarios exist that are legal and interesting.')

    except TestFailure:
        print_labeled_output(
            'FAILED',
            'The sanity checker has failed, for the reasons described above.')

    finally:
        if process != None:
            process.close()



def start_process() -> TextProcess:
    executable_modules = find_executable_modules()

    if len(executable_modules) == 0:
        print_labeled_output(
            'ERROR',
            'Cannot find an executable module in this directory',
            '(i.e., no modules contain an if __name__ == \'__main__\' block).',
            'Make sure that the sanity checker is in the same directory as the',
            'files that comprise your Project #4 solution.')

        raise TestFailure()

    elif len(executable_modules) > 1:
        print_labeled_output(
            'ERROR',
            'Found more than one executable module in this directory,',
            'but there needs to be exactly one, or else the sanity checker',
            '(and our test automation) will not be able to determine which',
            'one to execute.')

        raise TestFailure()

    else:
        print_labeled_output(
            'FOUND',
            'Found executable module: {}'.format(str(executable_modules[0].name)))
        
        return TextProcess(
            [sys.executable, str(executable_modules[0])],
            str(pathlib.Path.cwd()))



def find_executable_modules() -> [pathlib.Path]:
    modules = []

    for path_in_cwd in pathlib.Path.cwd().iterdir():
        if path_in_cwd.is_file() and path_in_cwd.name != SANITY_CHECK_FILENAME \
                and path_in_cwd.name.endswith('.py'):
            try:
                with path_in_cwd.open('r', encoding = 'utf-8') as file_in_cwd:
                    for line in file_in_cwd:
                        line = line.replace(' ', '')
                        if ('if__name__==\'__main__\'' in line) or ('if__name__=="__main__"' in line):
                            modules.append(path_in_cwd)
                            break
            except UnicodeDecodeError:
                pass

    return modules



def print_labeled_output(label: str, *msg_lines: typing.Iterable[str]) -> None:
    showed_first = False

    for msg_line in msg_lines:
        if not showed_first:
            print('{:10}|{}'.format(label, msg_line))
            showed_first = True
        else:
            print('{:10}|{}'.format(' ', msg_line))

    if not showed_first:
        print(label)



def make_test_lines(process: TextProcess) -> ['TestLine']:
    try:
        output_line = process.read_line(1.0)

    except TextProcessReadTimeout:
        output_line = None

    except Exception as e:
        print_labeled_output(
            'EXCEPTION',
            *[tb_line.rstrip() for tb_line in traceback.format_exc().split('\n')])

        raise TestFailure()

    if output_line != None and output_line.endswith('\r\n'):
        output_line = output_line[:-2]
    elif output_line != None and output_line.endswith('\n'):
        output_line = output_line[:-1]

    if output_line == None:
        print_labeled_output('NO OUTPUT', '')
    else:
        print_labeled_output('OUTPUT', output_line)

    if output_line == 'FULL':
        return make_full_test_lines()
    elif output_line == 'SIMPLE':
        return make_simple_test_lines()
    else:
        print_labeled_output(
            'ERROR',
            'The program must begin by printing one line of output that',
            'must be either FULL or SIMPLE.  This is necessary so that',
            'this sanity checker (and our automated tests) will know',
            'which rules you chose to implement.')

        raise TestFailure()



def make_full_test_lines() -> ['TestLine']:
    test_lines = []

    test_lines.append(TestInputLine('4'))
    test_lines.append(TestInputLine('4'))
    test_lines.append(TestInputLine('B'))
    test_lines.append(TestInputLine('>'))
    test_lines.append(TestInputLine('. . . .'))
    test_lines.append(TestInputLine('. B W .'))
    test_lines.append(TestInputLine('. W B .'))
    test_lines.append(TestInputLine('. . . .'))
    test_lines.append(TestOutputLine('B: 2  W: 2', 10.0))
    test_lines.append(TestOutputLine('. . . .', 10.0))
    test_lines.append(TestOutputLine('. B W .', 10.0))
    test_lines.append(TestOutputLine('. W B .', 10.0))
    test_lines.append(TestOutputLine('. . . .', 10.0))
    test_lines.append(TestOutputLine('TURN: B', 10.0))
    test_lines.append(TestInputLine('2 4'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 4  W: 1', 10.0))
    test_lines.append(TestOutputLine('. . . .', 10.0))
    test_lines.append(TestOutputLine('. B B B', 10.0))
    test_lines.append(TestOutputLine('. W B .', 10.0))
    test_lines.append(TestOutputLine('. . . .', 10.0))
    test_lines.append(TestOutputLine('TURN: W', 10.0))
    test_lines.append(TestInputLine('1 2'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 3  W: 3', 10.0))
    test_lines.append(TestOutputLine('. W . .', 10.0))
    test_lines.append(TestOutputLine('. W B B', 10.0))
    test_lines.append(TestOutputLine('. W B .', 10.0))
    test_lines.append(TestOutputLine('. . . .', 10.0))
    test_lines.append(TestOutputLine('TURN: B', 10.0))
    test_lines.append(TestInputLine('1 4'))
    test_lines.append(TestOutputLine('INVALID', 10.0))
    test_lines.append(TestInputLine('1 1'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 5  W: 2', 10.0))
    test_lines.append(TestOutputLine('B W . .', 10.0))
    test_lines.append(TestOutputLine('. B B B', 10.0))
    test_lines.append(TestOutputLine('. W B .', 10.0))
    test_lines.append(TestOutputLine('. . . .', 10.0))
    test_lines.append(TestOutputLine('TURN: W', 10.0))
    test_lines.append(TestInputLine('1 4'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 4  W: 4', 10.0))
    test_lines.append(TestOutputLine('B W . W', 10.0))
    test_lines.append(TestOutputLine('. B W B', 10.0))
    test_lines.append(TestOutputLine('. W B .', 10.0))
    test_lines.append(TestOutputLine('. . . .', 10.0))
    test_lines.append(TestOutputLine('TURN: B', 10.0))
    test_lines.append(TestInputLine('1 3'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 7  W: 2', 10.0))
    test_lines.append(TestOutputLine('B B B W', 10.0))
    test_lines.append(TestOutputLine('. B B B', 10.0))
    test_lines.append(TestOutputLine('. W B .', 10.0))
    test_lines.append(TestOutputLine('. . . .', 10.0))
    test_lines.append(TestOutputLine('TURN: W', 10.0))
    test_lines.append(TestInputLine('3 4'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 5  W: 5', 10.0))
    test_lines.append(TestOutputLine('B B B W', 10.0))
    test_lines.append(TestOutputLine('. B B W', 10.0))
    test_lines.append(TestOutputLine('. W W W', 10.0))
    test_lines.append(TestOutputLine('. . . .', 10.0))
    test_lines.append(TestOutputLine('TURN: B', 10.0))
    test_lines.append(TestInputLine('4 2'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 7  W: 4', 10.0))
    test_lines.append(TestOutputLine('B B B W', 10.0))
    test_lines.append(TestOutputLine('. B B W', 10.0))
    test_lines.append(TestOutputLine('. B W W', 10.0))
    test_lines.append(TestOutputLine('. B . .', 10.0))
    test_lines.append(TestOutputLine('TURN: W', 10.0))
    test_lines.append(TestInputLine('2 1'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 5  W: 7', 10.0))
    test_lines.append(TestOutputLine('B B B W', 10.0))
    test_lines.append(TestOutputLine('W W W W', 10.0))
    test_lines.append(TestOutputLine('. B W W', 10.0))
    test_lines.append(TestOutputLine('. B . .', 10.0))
    test_lines.append(TestOutputLine('TURN: B', 10.0))
    test_lines.append(TestInputLine('4 4'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 8  W: 5', 10.0))
    test_lines.append(TestOutputLine('B B B W', 10.0))
    test_lines.append(TestOutputLine('W B W W', 10.0))
    test_lines.append(TestOutputLine('. B B W', 10.0))
    test_lines.append(TestOutputLine('. B . B', 10.0))
    test_lines.append(TestOutputLine('TURN: W', 10.0))
    test_lines.append(TestInputLine('4 1'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 7  W: 7', 10.0))
    test_lines.append(TestOutputLine('B B B W', 10.0))
    test_lines.append(TestOutputLine('W B W W', 10.0))
    test_lines.append(TestOutputLine('. W B W', 10.0))
    test_lines.append(TestOutputLine('W B . B', 10.0))
    test_lines.append(TestOutputLine('TURN: B', 10.0))
    test_lines.append(TestInputLine('3 1'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 10  W: 5', 10.0))
    test_lines.append(TestOutputLine('B B B W', 10.0))
    test_lines.append(TestOutputLine('B B W W', 10.0))
    test_lines.append(TestOutputLine('B B B W', 10.0))
    test_lines.append(TestOutputLine('W B . B', 10.0))
    test_lines.append(TestOutputLine('TURN: W', 10.0))
    test_lines.append(TestInputLine('4 3'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 8  W: 8', 10.0))
    test_lines.append(TestOutputLine('B B B W', 10.0))
    test_lines.append(TestOutputLine('B B W W', 10.0))
    test_lines.append(TestOutputLine('B B W W', 10.0))
    test_lines.append(TestOutputLine('W W W B', 10.0))
    test_lines.append(TestOutputLine('WINNER: NONE', 10.0))
    test_lines.append(TestEndOfOutput(2.0))

    return test_lines



def make_simple_test_lines() -> ['TestLine']:
    test_lines = []

    test_lines.append(TestInputLine('4'))
    test_lines.append(TestInputLine('4'))
    test_lines.append(TestInputLine('B'))
    test_lines.append(TestInputLine('>'))
    test_lines.append(TestInputLine('. . . .'))
    test_lines.append(TestInputLine('. B W .'))
    test_lines.append(TestInputLine('. W B .'))
    test_lines.append(TestInputLine('. . . .'))
    test_lines.append(TestOutputLine('B: 2  W: 2', 10.0))
    test_lines.append(TestOutputLine('. . . .', 10.0))
    test_lines.append(TestOutputLine('. B W .', 10.0))
    test_lines.append(TestOutputLine('. W B .', 10.0))
    test_lines.append(TestOutputLine('. . . .', 10.0))
    test_lines.append(TestOutputLine('TURN: B', 10.0))
    test_lines.append(TestInputLine('1 3'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 4  W: 1', 10.0))
    test_lines.append(TestOutputLine('. . B .', 10.0))
    test_lines.append(TestOutputLine('. B B .', 10.0))
    test_lines.append(TestOutputLine('. W B .', 10.0))
    test_lines.append(TestOutputLine('. . . .', 10.0))
    test_lines.append(TestOutputLine('TURN: W', 10.0))
    test_lines.append(TestInputLine('3 4'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 2  W: 4', 10.0))
    test_lines.append(TestOutputLine('. . B .', 10.0))
    test_lines.append(TestOutputLine('. B W .', 10.0))
    test_lines.append(TestOutputLine('. W W W', 10.0))
    test_lines.append(TestOutputLine('. . . .', 10.0))
    test_lines.append(TestOutputLine('TURN: B', 10.0))
    test_lines.append(TestInputLine('4 3'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 6  W: 1', 10.0))
    test_lines.append(TestOutputLine('. . B .', 10.0))
    test_lines.append(TestOutputLine('. B W .', 10.0))
    test_lines.append(TestOutputLine('. B B B', 10.0))
    test_lines.append(TestOutputLine('. . B .', 10.0))
    test_lines.append(TestOutputLine('TURN: W', 10.0))
    test_lines.append(TestInputLine('4 4'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 3  W: 5', 10.0))
    test_lines.append(TestOutputLine('. . B .', 10.0))
    test_lines.append(TestOutputLine('. B W .', 10.0))
    test_lines.append(TestOutputLine('. B W W', 10.0))
    test_lines.append(TestOutputLine('. . W W', 10.0))
    test_lines.append(TestOutputLine('TURN: B', 10.0))
    test_lines.append(TestInputLine('2 4'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 7  W: 2', 10.0))
    test_lines.append(TestOutputLine('. . B .', 10.0))
    test_lines.append(TestOutputLine('. B B B', 10.0))
    test_lines.append(TestOutputLine('. B B B', 10.0))
    test_lines.append(TestOutputLine('. . W W', 10.0))
    test_lines.append(TestOutputLine('TURN: W', 10.0))
    test_lines.append(TestInputLine('2 4'))
    test_lines.append(TestOutputLine('INVALID', 10.0))
    test_lines.append(TestInputLine('1 4'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 4  W: 6', 10.0))
    test_lines.append(TestOutputLine('. . W W', 10.0))
    test_lines.append(TestOutputLine('. B W W', 10.0))
    test_lines.append(TestOutputLine('. B B B', 10.0))
    test_lines.append(TestOutputLine('. . W W', 10.0))
    test_lines.append(TestOutputLine('TURN: B', 10.0))
    test_lines.append(TestInputLine('1 2'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 7  W: 4', 10.0))
    test_lines.append(TestOutputLine('. B B W', 10.0))
    test_lines.append(TestOutputLine('. B B W', 10.0))
    test_lines.append(TestOutputLine('. B B B', 10.0))
    test_lines.append(TestOutputLine('. . W W', 10.0))
    test_lines.append(TestOutputLine('TURN: W', 10.0))
    test_lines.append(TestInputLine('4 2'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 5  W: 7', 10.0))
    test_lines.append(TestOutputLine('. B B W', 10.0))
    test_lines.append(TestOutputLine('. B B W', 10.0))
    test_lines.append(TestOutputLine('. W W B', 10.0))
    test_lines.append(TestOutputLine('. W W W', 10.0))
    test_lines.append(TestOutputLine('TURN: B', 10.0))
    test_lines.append(TestInputLine('3 1'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 8  W: 5', 10.0))
    test_lines.append(TestOutputLine('. B B W', 10.0))
    test_lines.append(TestOutputLine('. B B W', 10.0))
    test_lines.append(TestOutputLine('B B W B', 10.0))
    test_lines.append(TestOutputLine('. B W W', 10.0))
    test_lines.append(TestOutputLine('TURN: W', 10.0))
    test_lines.append(TestInputLine('4 1'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 5  W: 9', 10.0))
    test_lines.append(TestOutputLine('. B B W', 10.0))
    test_lines.append(TestOutputLine('. B B W', 10.0))
    test_lines.append(TestOutputLine('W W W B', 10.0))
    test_lines.append(TestOutputLine('W W W W', 10.0))
    test_lines.append(TestOutputLine('TURN: B', 10.0))
    test_lines.append(TestInputLine('2 1'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 8  W: 7', 10.0))
    test_lines.append(TestOutputLine('. B B W', 10.0))
    test_lines.append(TestOutputLine('B B B W', 10.0))
    test_lines.append(TestOutputLine('B B W B', 10.0))
    test_lines.append(TestOutputLine('W W W W', 10.0))
    test_lines.append(TestOutputLine('TURN: W', 10.0))
    test_lines.append(TestInputLine('1 1'))
    test_lines.append(TestOutputLine('VALID', 10.0))
    test_lines.append(TestOutputLine('B: 5  W: 11', 10.0))
    test_lines.append(TestOutputLine('W W B W', 10.0))
    test_lines.append(TestOutputLine('W W B W', 10.0))
    test_lines.append(TestOutputLine('B B W B', 10.0))
    test_lines.append(TestOutputLine('W W W W', 10.0))
    test_lines.append(TestOutputLine('WINNER: W', 10.0))
    test_lines.append(TestEndOfOutput(2.0))

    return test_lines



def run_test_lines(process: TextProcess, test_lines: 'TestLine') -> None:
    for line in test_lines:
        line.execute(process)



if __name__ == '__main__':
    run_test()
