import uos
import ure


class CLI:
    HEADER = 'MicroPythonShell'
    VERSION = 'v0.2a'

    OPTIONAL = '-o'
    POSITIONAL = '-p'
    INVALID = '-i'

    def __init__(self):
        self.user = 'root'
        self.hostname = ''
        self.directory = ''
        self.user_type = '#'
        self.prompt = None
        self.commands = ['pwd', 'ls', 'hostname', 'cat', 'rm', 'stat']
        self.options = {}
        print('{} {}'.format(CLI.HEADER, CLI.VERSION))

    def set_prompt(self):
        self.directory = uos.getcwd()
        self.prompt = '{}@{} {}{} '.format(self.user, self.hostname, self.directory, self.user_type)

    def shell(self):
        self.cmd_hostname(None, buffered=False)
        self.set_prompt()
        while True:
            command_string = input(self.prompt).strip()
            if command_string == '':
                continue
            index = command_string.find(' ')
            if index == -1:
                command = command_string
                arguments = None
            else:
                command = command_string[:index]
                arguments = command_string[index+1:]
            if command == 'exit':
                break
            self.command_processor(command, arguments)

    def command_processor(self, command, arguments):
        if command in self.commands:
            getattr(self, 'cmd_{}'.format(command))(arguments)

    def options_preprocessor(self, supported_options, arguments):
        self.options = {}
        if arguments is None:
            return
        index = 0
        BOF = not(index < len(arguments))
        if BOF:
            return
        char = None
        value = ''
        state = 0
        position = 0
        while True:
            EOF = not(index < len(arguments))
            if not EOF:
                char = arguments[index]
                if char == '-':
                    if state == 0:
                        state = 10      # enter optional arguments
                elif char == ' ':
                    if state == 0:
                        pass
                    elif state == 11:
                        state = 19      # exit optional arguments
                    elif state == 31:
                        state = 39      # exit positional arguments
                elif char in ['"', "'"]:
                    if state == 0:
                        state = 20      # enter positional arguments
                    elif state == 21:
                        state = 29      # exit positional arguments
                    elif state == 31:
                        state = 39      # exit positional arguments
                else:
                    if state == 0:
                        state = 31      # enter positional arguments
            else:
                if state == 0:
                    break
                if state in [10, 11]:
                    state = 19          # exit all states
                elif state in [20, 21]:
                    state = 29          # exit all states
                elif state in [30, 31]:
                    state = 39          # exit all states
            if state in [0]:
                index += 1
            elif state in [10, 20, 30]:
                index += 1
                state += 1
            elif state in [11]:         # load optional arguments
                value += char
                if value in supported_options:
                    if CLI.OPTIONAL in self.options:
                        self.options[CLI.OPTIONAL][value] = position
                    else:
                        self.options[CLI.OPTIONAL] = {value: position}
                    value = ''
                    position += 1
                index += 1
            elif state in [19]:         # finish optional arguments
                if value:
                    if value in supported_options:
                        if CLI.OPTIONAL in self.options:
                            self.options[CLI.OPTIONAL][value] = position
                        else:
                            self.options[CLI.OPTIONAL] = {value: position}
                        position += 1
                    else:
                        self.options[CLI.INVALID] = value
                        EOF = True
                index += 1
                value = ''
                state = 0
            elif state in [21, 31]:
                index += 1
                value += char
            elif state in [29, 39]:     # finish positional arguments
                if CLI.POSITIONAL in self.options:
                    self.options[CLI.POSITIONAL].append(value)
                else:
                    self.options[CLI.POSITIONAL] = [value]
                value = ''
                state = 0
                position += 1
                index += 1
            if EOF or index > 256:
                break

    @staticmethod
    def find(filename):
        if type(filename) != str:
            return False
        return filename in uos.listdir()

    def cmd_pwd(self, arguments):
        if arguments:
            print('pwd: expected 0 args, got 1')
        else:
            print(uos.getcwd())

    def cmd_ls(self, arguments):
        self.options_preprocessor(['l', '1'], arguments)
        if CLI.OPTIONAL not in self.options:
            buffered = False
            for filename in uos.listdir():
                if CLI.POSITIONAL not in self.options or filename in self.options[CLI.POSITIONAL]:
                    print('{} '.format(filename), end='')
                    buffered = True
            if buffered:
                print()
        elif CLI.INVALID in self.options:
            print("ls: invalid option -- '{}'".format(self.options[CLI.INVALID]))
        elif 'l' in self.options[CLI.OPTIONAL]:
            info = []
            max_inode = 0
            max_size = 0
            for stats in uos.ilistdir():
                add = True
                if CLI.POSITIONAL in self.options:
                    if stats[0] not in self.options[CLI.POSITIONAL]:
                        add = False
                if not add:
                    continue
                info.append((
                    'd' if stats[1] == 0x4000 else '-', stats[2], stats[3], stats[0], '/' if stats[1] == 0x4000 else ''
                ))
                if stats[3] > max_size:
                    max_size = stats[3]
                if stats[2] > max_inode:
                    max_inode = stats[2]
            mask = '{}rw-r--r-- {:' + str(len(str(max_inode))) + '} root root {:' + str(len(str(max_size))) + '} Jan 1 2000 {}{}'
            for i, stats in enumerate(info):
                print(mask.format(*stats), end='')
                if i < len(info):
                    print()
        elif '1' in self.options[CLI.OPTIONAL]:
            for stats in uos.ilistdir():
                add = True
                if CLI.POSITIONAL in self.options:
                    if stats[0] not in self.options[CLI.POSITIONAL]:
                        add = False
                if not add:
                    continue
                print('{}{}'.format(stats[0], '/' if stats[1] == 0x4000 else ''))

    def cmd_hostname(self, arguments, buffered=True):
        self.options_preprocessor([], arguments)
        if CLI.INVALID in self.options:
            print("hostname: invalid option -- '{}'".format(self.options[CLI.INVALID]))
        elif CLI.POSITIONAL not in self.options and CLI.find('hostname'):
            file = open('hostname', 'r')
            self.hostname = file.read()
            file.close()
            if buffered:
                print(self.hostname)
        elif CLI.POSITIONAL in self.options:
            hostname = self.options[CLI.POSITIONAL][0]
            result = ure.match('^[a-zA-Z][a-z0-9-]*[a-z0-9]', hostname)
            if result is not None:
                file = open('hostname', 'w')
                file.write(hostname)
                file.close()
                self.hostname = hostname
                self.set_prompt()
            elif buffered:
                print('hostname: the specified hostname is invalid')

    def cmd_cat(self, arguments):
        self.options_preprocessor(['n'], arguments)
        if CLI.INVALID in self.options:
            print("cat: invalid option -- '{}'".format(self.options[CLI.INVALID]))
        elif CLI.POSITIONAL not in self.options:
            print('Copy standard input to standard output not yet implemented.')
        elif CLI.find(self.options[CLI.POSITIONAL][0]):
            line_number = CLI.OPTIONAL in self.options and 'n' in self.options[CLI.OPTIONAL]
            file = open(self.options[CLI.POSITIONAL][0], 'r')
            if line_number:
                i = 1
                for line in file.readlines():
                    print('{: 5}  {}'.format(i, line), end='')
                    i += 1
            else:
                print(file.read())
            file.close()
        else:
            print('cat: {}: No such file or directory'.format(arguments))

    def cmd_rm(self, arguments):
        self.options_preprocessor([], arguments)
        if CLI.INVALID in self.options:
            print("rm: invalid option -- '{}'".format(self.options[CLI.INVALID]))
        elif CLI.POSITIONAL not in self.options:
            print("rm: missing operand")
        else:
            for filename in self.options[CLI.POSITIONAL]:
                if CLI.find(filename):
                    uos.remove(filename)
                else:
                    print("rm: cannot remove '{}': No such file or directory".format(filename))

    def cmd_stat(self, arguments):
        """
        st_mode: It represents file type and file mode bits (permissions).
        st_ino: It represents the inode number on Unix and the file index on Windows platform.
        st_dev: It represents the identifier of the device on which this file resides.
        st_nlink: It represents the number of hard links.
        st_uid: It represents the user identifier of the file owner.
        st_gid: It represents the group identifier of the file owner.
        st_size: It represents the size of the file in bytes.
        st_atime: It represents the time of most recent access. Expressed in seconds.
        st_mtime: It represents the time of most recent content modification. Expressed in seconds.
        st_ctime: It represents the time of most recent metadata change on Unix and creation time on Windows. Expressed in seconds.
        """
        self.options_preprocessor([], arguments)
        if CLI.INVALID in self.options:
            print("stat: invalid option -- '{}'".format(self.options[CLI.INVALID]))
        elif CLI.POSITIONAL not in self.options:
            print("stat: missing operand")
        else:
            for filename in self.options[CLI.POSITIONAL]:
                if CLI.find(filename):
                    stats = uos.stat(filename)
                    print('  File: {}'.format(filename))
                    print('  Size: {}  {}'.format(stats[6], 'directory' if stats[0] == 0x4000 else 'regular file'))
                    print('Device: {}  Inode: {}  Links: {}'.format(stats[2], stats[1], stats[3]))
                    print('Access: (0600/-rw-------)  Uid: ({}/root)  Gid: ({}/root)'.format(*stats[4:6]))
                    print('Access: 2000-01-01 00:00:00')
                    print('Modify: 2000-01-01 00:00:00')
                    print('Change: 2000-01-01 00:00:00')
                else:
                    print("stat: cannot stat '{}': No such file or directory".format(filename))

cli = CLI()
cli.shell()
