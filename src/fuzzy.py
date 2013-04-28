import cmd
import zoe

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

commands = ["send memo to USER", "add AMOUNT to raid"]

#for text, score in process.extract(received, commands):
#    print (text, score)

class Lexer:
    def __init__(self):
        self._users = zoe.Users()

    def analyze(self, cmd):
        substitutions = []
        substitutions.append(self.usersubs())

        for word in cmd.split():
            print(word)

    def usersubs(self):
        substitutions = []
        users = zoe.Users().subjects().keys()
        for id in users:
            substitutions.append((id, 'USERS'))
        return substitutions

class FuzzyShell(cmd.Cmd):

    prompt = "zoe> "

    def default(self, line):
        lex = Lexer()
        lex.analyze(line)

    def do_EOF(self, line):
        return True

FuzzyShell().cmdloop()


