#!/usr/bin python
class BeerData:
    def __init__(self):
        self.name = "empty"
        self.data = dict()
        self.children = dict()
        self.subdata = list()
        self.parent = None


class BeerParser():
    T_NONE = 0
    T_OPEN = 1
    T_CLOSE = 2
    T_DATA = 3
    T_EOF = 4
    T_SKIP = 5

    @staticmethod
    def nc(f):
        c = f.read(1)
        # print "'",c,"'"
        return c

    def find_recipes(self, f):
        # Jump over formatting BOM
        c = '?'
        while c != '<':
            c = self.nc(f)
            if not c:
                return
        f.seek(f.tell() - 1)
        # Find <Data><Recipe>
        found = False
        while not found:
            self.next(f)
            if self.data == "Data":
                self.next(f)
                if self.data == "Recipe":
                    f.seek(f.tell() - 8)  # Back up before recipe node
                    found = True

    def next(self, f):
        # print "at depth", self.depth
        c = self.nc(f)
        if not c:
            self.token = self.T_EOF
            return
        while c == ' ' or c == '\n' or c == '\t' or c == '\r':
            c = self.nc(f)
            if not c:
                break
        if not c:
            self.token = self.T_EOF
            return
        self.data = ""

        if c == '<':
            c = self.nc(f)
            if c != '/':
                self.token = self.T_OPEN
                self.data += c
            else:
                self.token = self.T_CLOSE
            c = self.nc(f)
            while c != '>':
                self.data += c
                c = self.nc(f)
        else:
            self.token = self.T_DATA
            self.data += c
            c = self.nc(f)
            while c != '<':
                self.data += c
                c = self.nc(f)
            f.seek(f.tell() - 1)

    def open_tag(self):
        # Ignore <Data> tags
        if self.data == "Data":
            self.token = self.T_SKIP
            return
        lasttag = self.tag
        self.tag = self.data
        if self.last == self.T_OPEN:
            temp = BeerData()
            temp.name = lasttag
            temp.parent = self.current
            if self.current.parent is not None:
                self.current.children[lasttag] = temp
            self.current.subdata.append(temp)
            self.current = temp
            self.depth += 1
        elif self.last == self.T_NONE:
            self.depth = 1
        self.last = self.T_OPEN

        # print "<OPEN>"

    def close_tag(self):
        if self.data == "Data":
            self.token = self.T_SKIP
            return
        if self.last == self.T_CLOSE:
            self.current = self.current.parent
            self.depth -= 1
        self.last = self.T_CLOSE

    # print "<CLOSE>"

    def data_field(self):
        self.current.data[self.tag] = self.data
        self.last = self.T_DATA

    # print "data[", self.tag, " ] =", self.data, " (", len(self.current.data), " )"

    def get_recipes(self, recipefile):
        if self.tag != "root":
            self.init()
        f = open(recipefile, "r")
        self.find_recipes(f)
        self.next(f)
        if self.token == self.T_OPEN:
            self.open_tag()
            while self.depth > 0:
                self.next(f)
                if self.token == self.T_EOF:
                    break
                elif self.token == self.T_SKIP:
                    continue
                elif self.token == self.T_OPEN:
                    self.open_tag()
                elif self.token == self.T_CLOSE:
                    self.close_tag()
                else:  # self.token == self.T_DATA):
                    self.data_field()
        else:
            print
            "Recipe list not found!"
        f.close()
        return self.recipes.subdata

    def init(self):
        self.recipes = BeerData()
        self.current = self.recipes
        self.tag = "root"
        self.current.name = self.tag
        self.last = self.T_NONE
        self.token = self.T_NONE
        self.data = ""
        self.depth = 0

    def __init__(self):
        self.recipes = BeerData()
        self.current = self.recipes
        self.tag = "root"
        self.current.name = self.tag
        self.last = self.T_NONE
        self.token = self.T_NONE
        self.data = ""
        self.depth = 0
