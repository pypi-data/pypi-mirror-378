# Copyright (c) 2021-2024, NakaMetPy Develoers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause
from .constants import LATEST_MASTER_TABLE_VERSION, OLDEST_MASTER_TABLE_VERSION


class MyException(Exception):
    def __init__(self, arg=""):
        self.arg = arg

class MyException2(Exception):
    def __init__(self, arg='', array1=None, array2=None):
        self.arg = arg
        self.array1 = array1
        self.array2 = array2

class MyException3(Exception):
    def __init__(self, *kargs):
        self.kargs = kargs

class MyWarning(UserWarning):
    def __init__(self, *kargs):
        self.kargs = kargs

class NotHaveEnoughDimsError(MyException):
    def __str__(self):
        # print(f"NotHaveEnoughDimsError: 変数 {self.arg} は1次元配列です.この変数は最低でも2次元である必要があります.")
        return (
            f"変数 {self.arg} は1次元配列です.この変数は最低でも2次元である必要があります.\n"+\
            f"The variable {self.arg} is 1D array. This variable must be at least 2D array."
        )

class NotAllowedDxShapeError(MyException2):
    def __str__(self):
        return (
            f"配列 dx の形が適切ではありません.\n{self.arg} の経度緯度方向は({self.array1.shape[-2]}, {self.array1.shape[-1]}), dx の緯度経度方向は({self.array1.shape[-2]}, {self.array1.shape[-1]-1})またはintかfloatの一定値である必要があります.しかし実際には({self.array2.shape[-2]}, {self.array2.shape[-1]})となっています.\n"+\
            f"The shape of array dx is not correct. The shape of \n{self.arg} on longitude is ({self.array1.shape[-2]}, {self.array1.shape[-1]}) and The shape of dx ({self.array1.shape[-2]}, {self.array1.shape[-1]-1}), OR they should be constant of int or float. However in your script, the shape is ({self.array2.shape[-2]}, {self.array2.shape[-1]})"
        )

class NotAllowedDyShapeError(MyException2):
    def __str__(self):
        return (
            f"配列 dx の形が適切ではありません.\n{self.arg} の経度緯度方向は({self.array1.shape[-2]}, {self.array1.shape[-1]}), dy の緯度経度方向は({self.array1.shape[-2]-1}, {self.array1.shape[-1]})またはintかfloatの一定値である必要があります.しかし実際には({self.array2.shape[-2]}, {self.array2.shape[-1]})となっています.\n"+\
            f"The shape of array dy is not correct. The shape of \n{self.arg} on latitude is ({self.array1.shape[-2]}, {self.array1.shape[-1]}) and The shape of dy ({self.array1.shape[-2]}, {self.array1.shape[-1]-1}), OR they should be constant of int or float. However in your script, the shape is ({self.array2.shape[-2]}, {self.array2.shape[-1]})"
        )

class InvalidDxValueError(Exception):
    def __str__(self):
        return (
            f"dx が0以下、または0以下の要素を含んでいます.値は必ず正でなければなりません.\n"+\
            f"dx includes the values which < or <= 0 . The values must be positive."
        )

class InvalidDyValueError(Exception):
    def __str__(self):
        return (
            f"dy が0以下、または0以下の要素を含んでいます.値は必ず正でなければなりません.\n"+\
            f"dy includes the values which < or <= 0 . The values must be positive."
        )

class ExceedTidxError(MyException3):
    def __str__(self):
        if self.kargs[1][0]==1:
          return (
              f"変数 {self.kargs[0]} の shape は {self.kargs[1]} です. tidx は {self.kargs[2]} が指定されており {self.kargs[1][0]-1} である必要があります.\n"+\
              f"The shape of variable {self.kargs[0]} is {self.kargs[1]}. You set tidx = {self.kargs[2]} but the tidx must be {self.kargs[1][0]-1}."
          )
        else:
          return (
              f"変数 {self.kargs[0]} の shape は {self.kargs[1]} です. tidx は {self.kargs[2]} が指定されており {self.kargs[1][0]-1} 以下である必要があります.\n"+\
              f"The shape of variable {self.kargs[0]} is {self.kargs[1]}. You set tidx = {self.kargs[2]} but the tidx must be less than or equal {self.kargs[1][0]-1}."
          )

class ExceedZidxError(MyException3):
    def __str__(self):
        if self.kargs[1][1]==1:
          return (
              f"変数 {self.kargs[0]} の shape は {self.kargs[1]} です. zidx は {self.kargs[2]} が指定されており {self.kargs[1][1]-1} である必要があります.\n"+\
              f"The shape of variable {self.kargs[0]} is {self.kargs[1]}. You set zidx = {self.kargs[2]} but the zidx must be {self.kargs[1][1]-1}."
          )
        else:
          return (
              f"変数 {self.kargs[0]} の shape は {self.kargs[1]} です. zidx は {self.kargs[2]} が指定されており {self.kargs[1][1]-1} 以下である必要があります.\n"+\
              f"The shape of variable {self.kargs[0]} is {self.kargs[1]}. You set zidx = {self.kargs[2]} but the zidx must be less than or equal {self.kargs[1][1]-1}."
          )

class InvalidTidxError(MyException3):
    def __str__(self):
      return (
          f"tidx は None, int, list, tuple, np.ndarray のいずれかである必要があります.しかし {self.kargs[0]} となっています.\n"+\
          f"tidx is must be None, int, list, tuple or np.ndarray. However, type(tidx) is now {self.kargs[0]}."
      )

class InvalidZidxError(MyException3):
    def __str__(self):
      return (
          f"zidx は None, int, list, tuple, np.ndarray のいずれかである必要があります.しかし {self.kargs[0]} となっています.\n"+\
          f"zidx is must be None, int, list, tuple or np.ndarray. However, type(zidx) is now {self.kargs[0]}."
      )

class NotHaveSetArgError(MyException3):
    def __str__(self):
        return (
            f"引数 {self.kargs[1]} に値が渡されていません.引数 {self.kargs[0]} を利用するには必要です.\n"+\
            f"The argment {self.kargs[1]} is not set. Need for {self.kargs[0]} option."
        )

class NotMatchTarContentNameError(MyException3):
    def __str__(self):
        return (
            f"tar ファイル {self.kargs[0]} に {self.kargs[1]} という名前のファイルはありません.名前は正しいですか?\n"+\
            f"{self.kargs[1]} was not found in tar file {self.kargs[0]} . Is the name correct?"
        )

class NotSupportedExtentionError(MyException3):
    def __str__(self):
        return (
            f"この関数は拡張子{self.kargs[0]}をサポートしていません.サポートしている拡張子は{self.kargs[1]}です.\n"+\
            f"Extention {self.kargs[0]} is not supported. Extention {self.kargs[1]} is/are suppoerted."
        )

class NotSupportedMeshError(MyException3):
    def __str__(self):
        return (
            f"この関数は{self.kargs[0]}mメッシュをサポートしていません.指定しているメッシュを確認してください.\n"+\
            f"Mesh {self.kargs[0]}m is not supported. Check the mesh value.."
        )

class NotSupportedOlderVersionMSWarning(MyWarning):
    def __str__(self):
        return (
            f"この関数は古いマスターテーブルバージョン番号：{self.kargs[0]}をサポートしていません.{OLDEST_MASTER_TABLE_VERSION}で読込みます.\n"+\
            f"It is not supported older Master Table Version {self.kargs[0]}. Trying on Version {OLDEST_MASTER_TABLE_VERSION}."
        )

class NotSupportedNewerVersionMSWarning(MyWarning):
    def __str__(self):
        return (
            f"この関数は新しいマスターテーブルバージョン番号：{self.kargs[0]}をサポートしていません.{LATEST_MASTER_TABLE_VERSION:02}で読込みます.\n"+\
            f"It is not supported newer Master Table Version {self.kargs[0]}. Trying on Version {LATEST_MASTER_TABLE_VERSION:02}."
        )

class NotSupportedBufrError(MyException3):
    def __str__(self):
        return (
            f"この関数は{self.kargs[0]}を読むことは出来ません.その理由は{self.kargs[1]}のためです.\n"+\
            f"{self.kargs[0]} could not be read using this function :("
        )

class UnexpectedBufrError(MyException3):
    def __str__(self):
        return (
            f"予期せぬエラーが発生しました.補足：{self.kargs[1]}"
        )

class MayNotBeAbleToReadBufrWarning(MyWarning):
    def __str__(self):
        return (
            f"この関数ではこのファイルを正しく読むことが出来ないかもしれません.理由：{self.kargs[0]}\n"+\
            f"It may be able to read this bufr file using nakametpy.bufr. Reason (in Japanese): {self.kargs[0]}"
        )