class FileReadWrite:

    def __init__(self,infile=None,outfile=None,
                 append=True,numberlines=False):
        self.infile = infile
        self.outfile = outfile
        self.append = append
        self.numberlines = numberlines
        self.write_handle = None
        self.read_handle = None
        
    def open_infile(self,infile=None):
        if infile is None:
            infile = self.infile

        try:
            self.read_handle = open(infile)
            return True
        except Exception as e:
            return False

    def open_outfile(self,outfile=None,append=None):
        if outfile is None:
            outfile = self.outfile
        if append is None:
            append = self.append

        try:
            if append:
                self.write_handle = open(outfile,'a')
            else:
                self.write_handle = open(outfile,'w')
            return True
        except Exception as e:
            return False

    def read_line(self,seek_offset=0,numberlines=None):
        if self.read_handle is None:
            raise StopIteration('unopened file')
            
        if numberlines is None:
            numberlines = self.numberlines
        for l_no, line in enumerate(self.read_handle):
            if l_no < seek_offset:
                continue
            if numberlines:
                yield "{}\t{}".format(l_no,line.strip())
            else:
                yield line.strip()

    def write_line(self,line):
        if self.write_handle is not None:
            self.write_handle.write(line)
            return True
        else:
            return False

    def close_handles(self):
        if self.write_handle is not None:
            self.write_handle.close()
            self.write_handle = None
        if self.read_handle is not None:
            self.read_handle.close()
            self.read_handle = None
