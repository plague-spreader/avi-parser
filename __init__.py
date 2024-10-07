from _io import BufferedReader

def read_avi_file(filename: str):
    with open(filename, mode="rb") as f:
        ret = RiffFile()
        ret.read(f)
        return ret


class AviStruct:
    block_size: int

    def read(self, f: BufferedReader):
        return NotImplemented


class AviChildrenStruct(AviStruct):
    children: list[AviStruct]

    def read_children(self, f: BufferedReader):
        start = f.tell()
        while f.tell() - start < self.block_size - 4:
            next_fourcc = f.read(4).decode()
            if next_fourcc == "LIST":
                to_add = List(next_fourcc)
            else:
                to_add = Chunk(next_fourcc)
            to_add.read(f)
            self.children.append(to_add)


class RiffFile(AviChildrenStruct):
    riff_fourcc: str
    riff_type: str

    def __init__(self):
        self.children = []

    def read(self, f: BufferedReader):
        self.riff_fourcc = f.read(4).decode()
        assert self.riff_fourcc == "RIFF"
        self.block_size = int.from_bytes(f.read(4), byteorder="little")
        self.riff_type = f.read(4).decode()

        self.read_children(f)

    def __str__(self):
        s = ['RIFF "{}" ({} bytes) ['.format(self.riff_type, self.block_size)]
        for child in self.children:
             s.append("\t" + str(child).replace("\n", "\n\t"))
        s.append("]")
        return "\n".join(s);


class List(AviChildrenStruct):
    list_fourcc: str
    list_type: str

    def __init__(self, list_fourcc):
        assert list_fourcc == "LIST"
        self.list_fourcc = "LIST"
        self.children = []

    def read(self, f: BufferedReader):
        self.block_size = int.from_bytes(f.read(4), byteorder="little")
        self.list_type = f.read(4).decode()

        self.read_children(f)

    def __str__(self):
        s = ['LIST "{}" ({} bytes) ['.format(self.list_type, self.block_size)]
        for child in self.children:
             s.append("\t" + str(child).replace("\n", "\n\t"))
        s.append("]")
        return "\n".join(s);


class Chunk(AviStruct):
    chunk_fourcc: str
    data: bytes

    def __init__(self, chunk_fourcc):
        assert chunk_fourcc != "LIST" and chunk_fourcc != "RIFF"
        self.chunk_fourcc = chunk_fourcc

    def read(self, f: BufferedReader):
        self.block_size = int.from_bytes(f.read(4), byteorder="little")
        self.data = f.read(self.block_size)
        # set the file to the nearest word boundary
        if f.tell()%2 == 1:
            f.read(1)

    def __str__(self):
        return 'CHUNK "{}" ({} bytes)'.format(self.chunk_fourcc,
                                              self.block_size)
