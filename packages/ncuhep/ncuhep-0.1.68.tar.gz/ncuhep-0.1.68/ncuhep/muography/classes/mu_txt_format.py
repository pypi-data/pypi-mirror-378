import numpy as np
import pandas as pd
import json


class MuTxtFormat:
    def __init__(self):
        self.data = None

        self.column = None
        self.dict_key = None
        self.bit_size = None
        self.dtype = None

        self.names = None

        self.cols = None
        self.dtypes = None

        self.sep = None
        self.header = None
        self.comment = None
        self.engine = None
        self.memory_map = None
        self.na_filter = None
        self.skip_blank_lines = None

        self.TCNT_bit_size = None
        self.PCNT_bit_size = None


    def _import(self, path):
        self.data = pd.read_csv(path, delimiter=",")

        self.column = self.data["column"].to_numpy(copy=False).astype(np.int16)
        self.dict_key = self.data["python dictionary key"].to_numpy(copy=False)
        self.bit_size = self.data["bit size"].to_numpy(copy=False).astype(np.int16)
        self.dtype = self.data["python dtype"].to_numpy(copy=False)

        self.names = ["BOARDID", "CHANNELID", "TIMESTAMP", "PCNT", "TCNT", "PWIDTH"]

        self.cols = []
        self.dtypes = {}

        self.sep = "\t"
        self.header = None
        self.comment = "#"
        self.engine = "c"
        self.memory_map = True
        self.na_filter = False
        self.skip_blank_lines = False

        for i in range(len(self.column)):
            if self.dict_key[i] in self.names:
                self.cols.append(int(self.column[i]))
                self.dtypes[self.dict_key[i]] = self.dtype[i]

        self.TCNT_bit_size = self.bit_size[self.dict_key == "TCNT"][0]
        self.PCNT_bit_size = self.bit_size[self.dict_key == "PCNT"][0]

