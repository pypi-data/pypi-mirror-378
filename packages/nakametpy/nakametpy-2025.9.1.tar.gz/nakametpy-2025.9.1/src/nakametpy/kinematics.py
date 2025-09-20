# Copyright (c) 2021-2025, NakaMetPy Develoers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause
#
# Original source lisence:
# Copyright (c) 2009,2017,2018,2019 MetPy Developers.
#
# 
#
# そもそものプログラム自体はMetPyのsource codeにあるため、自分はあくまでも
# metpy.unitsを用いないNumPyでの高速な計算を行うプログラムを作成することを目指す
# 入力データの単位に気をつけなければならない
# 単位はPa, K, RHは[0, 1]とする.
# 
# 更新日：2021/01/25 地衡風と非地衡風、相対渦度、気温減率、偽断熱減率、静的安定パラメタを求める関数の実装
#
# To do:
# lapse_rateの鉛直微分は高度ではなく気圧である必要があるかもしれないのでチェックする.
# nclは気圧で計算してある.
# advectionのチェック.移流は次元は1である.
#
#
import numpy as np
from .thermo import mixing_ratio_from_specific_humidity, potential_temperature, mixing_ratio_from_relative_humidity, virtual_temperature, saturation_mixing_ratio
from .constants import sat_pressure_0c, R, Cp, kappa, P0, epsilone, LatHeatC, g0, Re, f0, GammaD, Omega
from ._error import NotAllowedDxShapeError, NotAllowedDyShapeError, InvalidDxValueError, InvalidDyValueError, NotHaveSetArgError
import traceback
import sys
import warnings



def distance(lons, lats, lev_len = None, t_len = None):
    r'''各格子点間の距離を求める関数.
    
    次元は[(時間、鉛直方向)、緯度、経度]である.
    地球半径の値は6371229mを使用.

    Calculate the distance from latitude and longitude

    Parameters
    ----------
    lons: `numpy.ndarray`
        longitude(1d or 2d) in degree
    lats: `numpy.ndarray`
        latitude(1d or 2d) in degree
    
    Returns
    -------
    `numpy.ndarray`
        dx((t_len, lev_len), lats, lons), dy((t_len, lev_len), lats, lons)
    
    '''
    # lons, latsが1次元の場合、2次元に変換する
    if lats.ndim == 1:
        lons, lats = np.meshgrid(lons, lats)
    # 時間、高度、緯度、経度の4次元のデータを計算するために、2次元の緯度経度を4次元にする
    if t_len != None:
        if lev_len != None:
            lons = np.tile(lons, (t_len, lev_len, 1, 1))
            lats = np.tile(lats, (t_len, lev_len, 1, 1))
        else:
            lons = np.tile(lons, (t_len, 1, 1))
            lats = np.tile(lats, (t_len, 1, 1))
    else:
        if lev_len != None:
            lons = np.tile(lons, (lev_len, 1, 1))
            lats = np.tile(lats, (lev_len, 1, 1))
        else:
            pass
    radius = Re # m
    dlats_x = np.radians(np.diff(lats, axis=-1))
    dlats_y = np.radians(np.diff(lats, axis=-2))
    dlons_x = np.radians(np.diff(lons, axis=-1))
    dlons_y = np.radians(np.diff(lons, axis=-2))

    x_deg = np.sin(dlats_x/2) * np.sin(dlats_x/2) + np.cos(np.radians(lats[..., :-1])) \
        * np.cos(np.radians(lats[..., 1:])) * np.sin(dlons_x/2) * np.sin(dlons_x/2)
    x_rad = 2 * np.arctan2(np.sqrt(x_deg), np.sqrt(1-x_deg))
    dx = radius * x_rad
    
    y_deg = np.sin(dlats_y/2) * np.sin(dlats_y/2) + np.cos(np.radians(lats[..., :-1, :])) \
        * np.cos(np.radians(lats[..., 1:, :])) * np.sin(dlons_y/2) * np.sin(dlons_y/2)
    y_rad = 2 * np.arctan2(np.sqrt(y_deg), np.sqrt(1-y_deg))
    dy = radius * y_rad
    
    return dx, dy


def distance_4d(lons, lats, lev_len = 37, t_len = 24):
    r'''各格子点間の距離を求める関数.

    次元は[時間、鉛直方向、緯度、経度]である.
    地球半径の値は6371229mを使用.

    Calculate the distance from latitude and longitude

    Parameters
    ----------
    lons: `numpy.ndarray`
        longitude(1d or 2d) in degree
    lats: `numpy.ndarray`
        latitude(1d or 2d) in degree
    
    Returns
    -------
    `numpy.ndarray`
        dx(t_len, lev_len, lats, lons), dy(t_len, lev_len, lats, lons)
    
    '''
    warnings.warn(f"'{sys._getframe().f_code.co_name}' is deprecated. Please use '{sys._getframe().f_code.co_name[:-3]}'", FutureWarning, stacklevel=2)
    # lons, latsが1次元の場合、2次元に変換する
    if lats.ndim == 1:
        lons, lats = np.meshgrid(lons, lats)
    # 時間、高度、緯度、経度の4次元のデータを計算するために、2次元の緯度経度を4次元にする
    lons = np.tile(lons, (lev_len, t_len, lons.shape[0], lons.shape[1]))
    lats = np.tile(lats, (lev_len, t_len, lats.shape[0], lats.shape[1]))
    radius = Re # m
    dlats_x = np.radians(np.diff(lats, axis=-1))
    dlats_y = np.radians(np.diff(lats, axis=-2))
    dlons_x = np.radians(np.diff(lons, axis=-1))
    dlons_y = np.radians(np.diff(lons, axis=-2))

    x_deg = np.sin(dlats_x/2) * np.sin(dlats_x/2) + np.cos(np.radians(lats[:, :, :, :-1])) \
        * np.cos(np.radians(lats[:, :, :, 1:])) * np.sin(dlons_x/2) * np.sin(dlons_x/2)
    x_rad = 2 * np.arctan2(np.sqrt(x_deg), np.sqrt(1-x_deg))
    dx = radius * x_rad
    
    y_deg = np.sin(dlats_y/2) * np.sin(dlats_y/2) + np.cos(np.radians(lats[:, :, :-1, :])) \
        * np.cos(np.radians(lats[:, :, 1:, :])) * np.sin(dlons_y/2) * np.sin(dlons_y/2)
    y_rad = 2 * np.arctan2(np.sqrt(y_deg), np.sqrt(1-y_deg))
    dy = radius * y_rad
    
    return dx, dy


def distance_3d(lons, lats, len3d = 24):
    r'''各格子点間の距離を求める関数.

    次元は[時間、緯度、経度]である.
    Single Levelの変数を計算する際に用いる.
    
    地球半径の値は6371229mを使用.

    Calculate the distance from latitude and longitude

    Parameters
    ----------
    lons: `numpy.ndarray`
        longitude(1d or 2d) in degree
    lats: `numpy.ndarray`
        latitude(1d or 2d) in degree
    
    Returns
    -------
    `numpy.ndarray`
        dx(t_len, lats, lons), dy(t_len, lats, lons)
    
    '''
    warnings.warn(f"'{sys._getframe().f_code.co_name}' is deprecated. Please use '{sys._getframe().f_code.co_name[:-3]}'", FutureWarning, stacklevel=2)
    # lons, latsが1次元の場合、2次元に変換する
    if lats.ndim == 1:
        lons, lats = np.meshgrid(lons, lats)
    # 時間、高度、緯度、経度の4次元のデータを計算するために、2次元の緯度経度を3次元にする
    # もし特定の時間に関する3次元データを扱う場合、t_lenをERAの場合37にする
    lons = np.tile(lons, (len3d, lons.shape[0], lons.shape[1]))
    lats = np.tile(lats, (len3d, lats.shape[0], lats.shape[1]))
    radius = Re # m
    dlats_x = np.radians(np.diff(lats, axis=-1))
    dlats_y = np.radians(np.diff(lats, axis=-2))
    dlons_x = np.radians(np.diff(lons, axis=-1))
    dlons_y = np.radians(np.diff(lons, axis=-2))

    x_deg = np.sin(dlats_x/2) * np.sin(dlats_x/2) + np.cos(np.radians(lats[:, :, :-1])) \
        * np.cos(np.radians(lats[:, :, 1:])) * np.sin(dlons_x/2) * np.sin(dlons_x/2)
    x_rad = 2 * np.arctan2(np.sqrt(x_deg), np.sqrt(1-x_deg))
    dx = radius * x_rad
    
    y_deg = np.sin(dlats_y/2) * np.sin(dlats_y/2) + np.cos(np.radians(lats[:, :-1, :])) \
        * np.cos(np.radians(lats[:, 1:, :])) * np.sin(dlons_y/2) * np.sin(dlons_y/2)
    y_rad = 2 * np.arctan2(np.sqrt(y_deg), np.sqrt(1-y_deg))
    dy = radius * y_rad
    
    return dx, dy


def distance_2d(lons, lats):
    r'''各格子点間の距離を求める関数.

    次元は[時間、緯度、経度]である.
    地球半径の値は6371229mを使用.

    Calculate the distance from latitude and longitude

    Parameters
    ----------
    lons: `numpy.ndarray`
        longitude(1d or 2d) in degree
    lats: `numpy.ndarray`
        latitude(1d or 2d) in degree
    
    Returns
    -------
    `numpy.ndarray`
        dx(lats, lons), dy(lats, lons)
    
    '''
    warnings.warn(f"'{sys._getframe().f_code.co_name}' is deprecated. Please use '{sys._getframe().f_code.co_name[:-3]}'", FutureWarning, stacklevel=2)
    if lats.ndim == 1:
        lons, lats = np.meshgrid(lons, lats)
    radius = Re # m
    dlats_x = np.radians(np.diff(lats, axis=-1))
    dlats_y = np.radians(np.diff(lats, axis=-2))
    dlons_x = np.radians(np.diff(lons, axis=-1))
    dlons_y = np.radians(np.diff(lons, axis=-2))

    x_deg = np.sin(dlats_x/2) * np.sin(dlats_x/2) + np.cos(np.radians(lats[:, :-1])) \
        * np.cos(np.radians(lats[:, 1:])) * np.sin(dlons_x/2) * np.sin(dlons_x/2)
    x_rad = 2 * np.arctan2(np.sqrt(x_deg), np.sqrt(1-x_deg))
    dx = radius * x_rad
    
    y_deg = np.sin(dlats_y/2) * np.sin(dlats_y/2) + np.cos(np.radians(lats[:-1, :])) \
        * np.cos(np.radians(lats[1:, :])) * np.sin(dlons_y/2) * np.sin(dlons_y/2)
    y_rad = 2 * np.arctan2(np.sqrt(y_deg), np.sqrt(1-y_deg))
    dy = radius * y_rad
    
    return dx, dy


def dis_azi_from_point(lats, lons, *, idx_flag=False, clat=None, clon=None, clat_idx=None, clon_idx=None, lev_len=None, t_len=None):
    r'''ある地点からの距離と方位角を求める関数

    次元は[(時間、鉛直方向)、緯度、経度]である.
    地球半径の値は6371229mを使用.

    Calculate the distance and azimuth from latitude and longitude

    Parameters
    ----------
    lats: `numpy.ndarray`
        latitude(1d or 2d) in degree
    lons: `numpy.ndarray`
        longitude(1d or 2d) in degree
    lat_idx: `int`
    lon_idx: `int`
    
    Returns
    -------
    `numpy.ndarray`
        dr((t_len, lev_len), lats, lons), azimuth((t_len, lev_len), lats, lons)
    
    '''
    if idx_flag:
        if clat_idx==None:
            raise NotHaveSetArgError("idx_flag=True", "clat_idx")
        elif clon_idx==None:
            raise NotHaveSetArgError("idx_flag=True", "clon_idx")
        else:
            center_lat = lats[clat_idx, clon_idx]
            center_lon = lons[clat_idx, clon_idx]
    else:
        if clat==None:
            raise NotHaveSetArgError("idx_flag=False", "clat")
        elif clon==None:
            raise NotHaveSetArgError("idx_flag=False", "clon")
        else:
            center_lat = clat
            center_lon = clon
    # lons, latsが1次元の場合、2次元に変換する
    if lats.ndim == 1:
        lons, lats = np.meshgrid(lons, lats)
    # 時間、高度、緯度、経度の4次元のデータを計算するために、2次元の緯度経度を4次元にする
    radius = Re # m
    dlats = np.radians(lats-center_lat)
    dlons = np.radians(lons-center_lon)
    deg = np.sin(dlats/2) * np.sin(dlats/2) + np.cos(np.radians(center_lat)) \
        * np.cos(np.radians(lats)) * np.sin(dlons/2) * np.sin(dlons/2)
    rad = 2 * np.arctan2(np.sqrt(deg), np.sqrt(1-deg))
    azimuth = np.arctan2(np.sin(dlons), np.cos(np.radians(center_lat))\
        *np.tan(np.radians(lats))-np.sin(np.radians(center_lat))*np.cos(dlons))
    dr = radius * rad
    azimuth = np.deg2rad(90)-azimuth
    if t_len == None:
        if lev_len == None:
            pass
        else:
            dr = np.tile(dr, (lev_len, 1, 1))
            azimuth = np.tile(azimuth, (lev_len, 1, 1))
    else:
        if lev_len == None:
            dr = np.tile(dr, (t_len, 1, 1))
            azimuth = np.tile(azimuth, (t_len, 1, 1))
        else:
            dr = np.tile(dr, (t_len, lev_len, 1, 1))
            azimuth = np.tile(azimuth, (t_len, lev_len, 1, 1))
    
    return dr, azimuth


def gradient_h(var, dx, dy, wrfon=0):
    r'''変数の勾配を求める関数

    dx, dyは`distance_nd`を使って求め、それらをこの関数の引数に渡すと計算できる.
    dx, dyにintまたはfloatを代入した場合、一定値として扱われる.

    Parameters
    ----------
    var: `numpy.ndarray`
        variable

        計算したい変数
    dx: `numpy.ndarray` or `int` or `float`
        var.shape[-1]-1 == dx.shape[-1]

        経度方向の次元はvar.shape[-1]-1でなければならない
    dy: `numpy.ndarray` or `int` or `float`
        var.shape[-2]-1 == dy.shape[-2]

        経度方向の次元はvar.shape[-2]-1でなければならない 
    wrfon: `int`
        Flag whether input data is wrfout or not  

        入力データがwrfoutか否かのフラグ 
    
    Returns
    -------
    `numpy.ndarray`
        grad_x(nd), grad_y(nd)
    
    '''
    if (isinstance(dx, (int, float)))and(isinstance(dy, (int, float))):
        pass
    elif not ((var.shape[-2] == dx.shape[-2])and(var.shape[-1] == dx.shape[-1]+1)):
        raise NotAllowedDxShapeError('var', var, dx)
    elif not ((var.shape[-2] == dy.shape[-2]+1)and(var.shape[-1] == dy.shape[-1])):
        raise NotAllowedDyShapeError('var', var, dy)
    
    if np.any(dx<=0):
        raise InvalidDxValueError()
    if np.any(dy<=0):
        raise InvalidDyValueError()

    grad_shape = list(var.shape)
    grad_shape.insert(0, 2) # grad_xとgrad_yの2つの次元を追加
    grad = np.ma.zeros(grad_shape)
    grad_x_stag = np.diff(var, axis=-1)/dx
    grad_y_stag = (-1)**(wrfon-1)*np.diff(var, axis=-2)/dy
    # 境界条件を代入
    grad[0, ..., 0] = grad_x_stag[..., 0]
    grad[0, ..., -1] = grad_x_stag[..., -1]
    grad[1, ..., 0, :] = grad_y_stag[..., 0, :]
    grad[1, ..., -1, :] = grad_y_stag[..., -1, :]
    grad[0, ..., 1:-1] = (grad_x_stag[..., 1:] + grad_x_stag[..., :-1])/2
    grad[1, ..., 1:-1, :] = (grad_y_stag[..., 1:, :] + grad_y_stag[..., :-1, :])/2
    return grad


def gradient_h_4d(var, dx, dy, wrfon=0):
    r'''変数の勾配を求める関数.

    distance_4dを使ってdx, dyを求め、それらをこの関数の引数に渡すと計算できる

    Parameters
    ----------
    var: `numpy.ndarray`
        variable

        計算したい変数
    dx: `numpy.ndarray` or `int` or `float`
        var.shape[-1]-1 == dx.shape[-1]

        経度方向の次元はvar.shape[-1]-1でなければならない
    dy: `numpy.ndarray` or `int` or `float`
        var.shape[-2]-1 == dy.shape[-2]

        経度方向の次元はvar.shape[-2]-1でなければならない
    wrfon: `int`
        Flag whether input data is wrfout or not

        入力データがwrfoutか否かのフラグ 
    
    Returns
    -------
    `numpy.ndarray`
        grad_x(4d), grad_y(4d)
    
    '''
    warnings.warn(f"'{sys._getframe().f_code.co_name}' is deprecated. Please use '{sys._getframe().f_code.co_name[:-3]}'", FutureWarning, stacklevel=2)
    if (isinstance(dx, (int, float)))and(isinstance(dy, (int, float))):
        pass
    elif not ((var.shape[-2] == dx.shape[-2])and(var.shape[-1] == dx.shape[-1]+1)):
        raise NotAllowedDxShapeError('var', var, dx)
    elif not ((var.shape[-2] == dy.shape[-2]+1)and(var.shape[-1] == dy.shape[-1])):
        raise NotAllowedDyShapeError('var', var, dy)

    if np.any(dx<=0):
        raise InvalidDxValueError()
    if np.any(dy<=0):
        raise InvalidDyValueError()
    
    grad_shape = list(var.shape)
    grad_shape.insert(0, 2) # grad_xとgrad_yの2つの次元を追加
    grad = np.ma.zeros(grad_shape)
    grad_x_stag = np.diff(var, axis=-1)/dx
    grad_y_stag = (-1)**(wrfon-1)*np.diff(var, axis=-2)/dy
    # 境界条件を代入
    grad[0, :, :, :, 0] = grad_x_stag[:, :, :, 0]
    grad[0, :, :, :, -1] = grad_x_stag[:, :, :, -1]
    grad[1, :, :, 0, :] = grad_y_stag[:, :, 0, :]
    grad[1, :, :, -1, :] = grad_y_stag[:, :, -1, :]
    grad[0, :, :, :, 1:-1] = (grad_x_stag[:, :, :, 1:] + grad_x_stag[:, :, :, :-1])/2
    grad[1, :, :, 1:-1, :] = (grad_y_stag[:, :, 1:, :] + grad_y_stag[:, :, :-1, :])/2
    return grad


def gradient_h_3d(var, dx, dy, wrfon=0):
    r'''変数の勾配を求める関数.

    distance_4dを使ってdx, dyを求め、それらをこの関数の引数に渡すと計算できる

    Parameters
    ----------
    var: `numpy.ndarray`
        variable

        計算したい変数 
    dx: `numpy.ndarray` or `int` or `float`
        var.shape[-1]-1 == dx.shape[-1]

        経度方向の次元はvar.shape[-1]-1でなければならない
    dy: `numpy.ndarray` or `int` or `float`
        var.shape[-2]-1 == dy.shape[-2]

        経度方向の次元はvar.shape[-2]-1でなければならない
    wrfon: `int`
        Flag whether input data is wrfout or not

        入力データがwrfoutか否かのフラグ
    
    Returns
    -------
    `numpy.ndarray`
        grad_x(3d), grad_y(3d)
    
    '''
    warnings.warn(f"'{sys._getframe().f_code.co_name}' is deprecated. Please use '{sys._getframe().f_code.co_name[:-3]}'", FutureWarning, stacklevel=2)
    if (isinstance(dx, (int, float)))and(isinstance(dy, (int, float))):
        pass
    elif not ((var.shape[-2] == dx.shape[-2])and(var.shape[-1] == dx.shape[-1]+1)):
        raise NotAllowedDxShapeError('var', var, dx)
    elif not ((var.shape[-2] == dy.shape[-2]+1)and(var.shape[-1] == dy.shape[-1])):
        raise NotAllowedDyShapeError('var', var, dy)

    if np.any(dx<=0):
        raise InvalidDxValueError()
    if np.any(dy<=0):
        raise InvalidDyValueError()
    
    grad_shape = list(var.shape)
    grad_shape.insert(0, 2) # grad_xとgrad_yの2つの次元を追加
    grad = np.ma.zeros(grad_shape)
    grad_x_stag = np.diff(var, axis=-1)/dx
    grad_y_stag = (-1)**(wrfon-1)*np.diff(var, axis=-2)/dy
    # 境界条件を代入
    grad[0, :, :, 0] = grad_x_stag[:, :, 0]
    grad[0, :, :, -1] = grad_x_stag[:, :, -1]
    grad[1, :, 0, :] = grad_y_stag[:, 0, :]
    grad[1, :, -1, :] = grad_y_stag[:, -1, :]
    grad[0, :, :, 1:-1] = (grad_x_stag[:, :, 1:] + grad_x_stag[:, :, :-1])/2
    grad[1, :, 1:-1, :] = (grad_y_stag[:, 1:, :] + grad_y_stag[:, :-1, :])/2
    return grad


def gradient_h_2d(var, dx, dy, wrfon=0):
    r'''変数の勾配を求める関数.

    distance_4dを使ってdx, dyを求め、それらをこの関数の引数に渡すと計算できる

    Parameters
    ----------
    var: `numpy.ndarray`
        variable

        計算したい変数
    dx: `numpy.ndarray` or `int` or `float`
        var.shape[-1]-1 == dx.shape[-1]

        経度方向の次元はvar.shape[-1]-1でなければならない
    dy: `numpy.ndarray` or `int` or `float`
        var.shape[-2]-1 == dy.shape[-2]

        経度方向の次元はvar.shape[-2]-1でなければならない
    wrfon: `int`
        Flag whether input data is wrfout or not

        入力データがwrfoutか否かのフラグ
    
    Returns
    -------
    `numpy.ndarray`
        grad_x(2d), grad_y(2d)
    
    '''
    warnings.warn(f"'{sys._getframe().f_code.co_name}' is deprecated. Please use '{sys._getframe().f_code.co_name[:-3]}'", FutureWarning, stacklevel=1)
    if (isinstance(dx, (int, float)))and(isinstance(dy, (int, float))):
        pass
    elif not ((var.shape[-2] == dx.shape[-2])and(var.shape[-1] == dx.shape[-1]+1)):
        raise NotAllowedDxShapeError('var', var, dx)
    elif not ((var.shape[-2] == dy.shape[-2]+1)and(var.shape[-1] == dy.shape[-1])):
        raise NotAllowedDyShapeError('var', var, dy)

    if np.any(dx<=0):
        raise InvalidDxValueError()
    if np.any(dy<=0):
        raise InvalidDyValueError()
    
    grad_shape = list(var.shape)
    grad_shape.insert(0, 2) # grad_xとgrad_yの2つの次元を追加
    grad = np.ma.zeros(grad_shape)
    grad_x_stag = np.diff(var, axis=-1)/dx
    grad_y_stag = (-1)**(wrfon-1)*np.diff(var, axis=-2)/dy
    # 境界条件を代入
    grad[0, :, 0] = grad_x_stag[:, 0]
    grad[0, :, -1] = grad_x_stag[:, -1]
    grad[1, 0, :] = grad_y_stag[0, :]
    grad[1, -1, :] = grad_y_stag[-1, :]
    grad[0, :, 1:-1] = (grad_x_stag[:, 1:] + grad_x_stag[:, :-1])/2
    grad[1, 1:-1, :] = (grad_y_stag[1:, :] + grad_y_stag[:-1, :])/2
    return grad


def divergence_2d(fx, fy, dx, dy, wrfon=0):
    r'''直交座標系において変数の発散を求める関数.

    distance_2dを使ってdx, dyを求め、それらをこの関数の引数に渡すと計算できる

    Parameters
    ----------
    fx: `numpy.ndarray`
        x-flux

        x(東西)方向のフラックス
    fy: `numpy.ndarray`
        y-flux

        y(南北)方向のフラックス
    dx: `numpy.ndarray`
        var.shape[-1]-1 == dx.shape[-1]

        経度方向の次元はvar.shape[-1]-1でなければならない
    dy: `numpy.ndarray`
        var.shape[-2]-1 == dy.shape[-2]

        経度方向の次元はvar.shape[-2]-1でなければならない
    wrfon: `int`
        Flag whether input data is wrfout or not

        入力データがwrfoutか否かのフラグ
    
    Returns
    -------
    `numpy.ndarray`
        divergence
    
    '''

    if np.any(dx<=0):
        raise InvalidDxValueError()
    if np.any(dy<=0):
        raise InvalidDyValueError()
    
    warnings.warn(f"'{sys._getframe().f_code.co_name}' is deprecated. Please use '{sys._getframe().f_code.co_name[:-3]}'", FutureWarning, stacklevel=2)
    div = np.ma.zeros(fx.shape)
    grad_x_stag = np.diff(fx, axis=-1)/dx
    grad_y_stag = (-1)**(wrfon-1)*np.diff(fy, axis=-2)/dy
    div[:, 0] = grad_x_stag[:, 0]
    div[:, -1] = grad_x_stag[:, -1]
    div[0, :] = grad_y_stag[0, :]
    div[-1, :] = grad_y_stag[-1, :]
    div[:, 1:-1] += (grad_x_stag[:, :-1]+grad_x_stag[:, 1:])/2
    div[1:-1, :] += (grad_y_stag[:-1, :]+grad_y_stag[1:, :])/2
    return div


def divergence(fx, fy, dx, dy, wrfon=0):
    r'''直交座標系において変数の発散を求める関数.

    divergence_2dの拡張で3次元以上の配列に対応している.
    distance_2d, 3d, 4dを使ってdx, dyを求め、それらをこの関数の引数に渡すと計算できる

    Parameters
    ----------
    fx: `numpy.ndarray`
        x-flux

        x(東西)方向のフラックス
    fy: `numpy.ndarray`
        y-flux

        y(南北)方向のフラックス
    dx: `numpy.ndarray` or `int` or `float`
        var.shape[-1]-1 == dx.shape[-1]

        経度方向の次元はvar.shape[-1]-1でなければならない
    dy: `numpy.ndarray` or `int` or `float`
        var.shape[-2]-1 == dy.shape[-2]

        経度方向の次元はvar.shape[-2]-1でなければならない
    wrfon: `int`
        Flag whether input data is wrfout or not

        入力データがwrfoutか否かのフラグ
    
    Returns
    -------
    `numpy.ndarray`
        divergence
    
    '''
    if (isinstance(dx, (int, float)))and(isinstance(dy, (int, float))):
        pass
    elif not ((fx.shape[-2] == dx.shape[-2])and(fx.shape[-1] == dx.shape[-1]+1)):
        raise NotAllowedDxShapeError('fx', fx, dx)
    elif not ((fy.shape[-2] == dy.shape[-2]+1)and(fy.shape[-1] == dy.shape[-1])):
        raise NotAllowedDyShapeError('fy', fy, dy)

    if np.any(dx<=0):
        raise InvalidDxValueError()
    if np.any(dy<=0):
        raise InvalidDyValueError()
    
    div = np.ma.zeros(fx.shape)
    grad_x_stag = np.diff(fx, axis=-1)/dx
    grad_y_stag = (-1)**(wrfon-1)*np.diff(fy, axis=-2)/dy
    div[..., 0] = grad_x_stag[..., 0]
    div[..., -1] = grad_x_stag[..., -1]
    div[..., 0, :] = grad_y_stag[..., 0, :]
    div[..., -1, :] = grad_y_stag[..., -1, :]
    div[..., 1:-1] += (grad_x_stag[..., :-1]+grad_x_stag[..., 1:])/2
    div[..., 1:-1, :] += (grad_y_stag[..., :-1, :]+grad_y_stag[..., 1:, :])/2
    return div


def uv2dv_cfd(fx, fy, lat, lon, boundOpt=4):
    r'''
    Divergence caluculation function from NCL.
    
    Parameters
    ----------
    fx: `numpy.ndarray`
        x-flux

        x(東西)方向のフラックス
    fy: `numpy.ndarray`
        y-flux

        y(南北)方向のフラックス
    lat: `numpy.ndarray`
        latitude
    lon: `numpy.ndarray`
        longitude
    boundOpt: `int`
        boundOpt

        今は4(境界は片方の成分の収束のみで計算)のみ対応

    Returns
    -------
    `numpy.ndarray`
        divergence with latitude parameter

    Note
    -----
    URL: https://www.ncl.ucar.edu/Document/Functions/Built-in/uv2dv_cfd.shtml

    '''
    if boundOpt != 4:
        try:
            raise ValueError('Only boudOpt 4 is available now.')
        except:
            traceback.print_exc()
        # except ValueError as e:
            # print(e)

    dx, dy = distance(lon, lat)

    if lat.ndim == 1:
        lats = np.tile(lat.reshape(-1, 1), (1, fx.shape[-1]))
    else:
        lats = lat

    if (lats[..., 1, 0]-lats[..., 0, 0])>0:
        s2n = True
    else:
        s2n = False

    # if fx.ndim is greater than 4, we must revise below.
    if (fx.ndim > 2) and (lats.ndim==2):
        if fx.ndim == 3:
            lats = np.tile(lats, (fx.shape[0], 1, 1))
            dx = np.tile(dx, (fx.shape[0], 1, 1))
            dy = np.tile(dy, (fx.shape[0], 1, 1))
        elif fx.ndim == 4:
            lats = np.tile(lats, (fx.shape[0], fx.shape[1], 1, 1))
            dx = np.tile(dx, (fx.shape[0], fx.shape[1], 1, 1))
            dy = np.tile(dy, (fx.shape[0], fx.shape[1], 1, 1))
    
    div = np.ma.zeros(fx.shape)
    grad_x_stag = np.diff(fx, axis=-1)/dx
    grad_y_stag = (-1)**(s2n-1)*np.diff(fy, axis=-2)/dy
    lat_factor = (fy / Re) * np.cos(np.deg2rad(lats))
    div[..., 0] = grad_x_stag[..., 0]
    div[..., -1] = grad_x_stag[..., -1]
    div[..., 0, :] = grad_y_stag[..., 0, :]
    div[..., -1, :] = grad_y_stag[..., -1, :]
    div[..., 1:-1] += (grad_x_stag[..., :-1]+grad_x_stag[..., 1:])/2
    div[..., 1:-1, :] += (grad_y_stag[..., :-1, :]+grad_y_stag[..., 1:, :])/2 - lat_factor[..., 1:-1, :]
    div = np.ma.where(np.ma.abs(div)>1E8, np.ma.masked, div)
    return div


def uv2vr_cfd(fx, fy, lat, lon, boundOpt=4):
    r'''
    Relative vorticity caluculation function from NCL.
    
    Parameters
    ----------
    fx: `numpy.ndarray`
        x-flux

        x(東西)方向のフラックス
    fy: `numpy.ndarray`
        y-flux

        y(南北)方向のフラックス
    lat: `numpy.ndarray`
        latitude
    lon: `numpy.ndarray`
        longitude
    boundOpt: `int`
        boundOpt

        今は4(境界は片方の成分の渦度のみで計算)のみ対応

    Returns
    -------
    `numpy.ndarray`
        divergence with latitude parameter

    Note
    -----
    URL: https://www.ncl.ucar.edu/Document/Functions/Built-in/uv2vr_cfd.shtml

    '''
    if boundOpt != 4:
        try:
            raise ValueError('Only boudOpt 4 is available now.')
        except:
            traceback.print_exc()

    dx, dy = distance(lon, lat)

    if lat.ndim == 1:
        lats = np.tile(lat.reshape(-1, 1), (1, fx.shape[-1]))
    else:
        lats = lat

    if (lats[..., 1, 0]-lats[..., 0, 0])>0:
        s2n = True
    else:
        s2n = False
    
    # if fx.ndim is greater than 4, we must revise below.
    if (fx.ndim > 2) and (lats.ndim==2):
        if fx.ndim == 3:
            lats = np.tile(lats, (fx.shape[0], 1, 1))
            dx = np.tile(dx, (fx.shape[0], 1, 1))
            dy = np.tile(dy, (fx.shape[0], 1, 1))
        elif fx.ndim == 4:
            lats = np.tile(lats, (fx.shape[0], fx.shape[1], 1, 1))
            dx = np.tile(dx, (fx.shape[0], fx.shape[1], 1, 1))
            dy = np.tile(dy, (fx.shape[0], fx.shape[1], 1, 1))
    
    vr = np.ma.zeros(fx.shape)
    grad_x_stag = np.diff(fy, axis=-1)/dx
    grad_y_stag = (-1)**(s2n-1)*np.diff(fx, axis=-2)/dy
    lat_factor = (fx / Re) * np.cos(np.deg2rad(lats))
    vr[..., 0] = grad_x_stag[..., 0]
    vr[..., -1] = grad_x_stag[..., -1]
    vr[..., 0, :] = grad_y_stag[..., 0, :]
    vr[..., -1, :] = grad_y_stag[..., -1, :]
    vr[..., 1:-1] += (grad_x_stag[..., :-1]+grad_x_stag[..., 1:])/2
    vr[..., 1:-1, :] += -((grad_y_stag[..., :-1, :]+grad_y_stag[..., 1:, :])/2) + lat_factor[..., 1:-1, :]
    vr = np.ma.where(np.ma.abs(vr)>100, np.ma.masked, vr)
    return vr


def vert_grad_3d(variables, pres_3d, z_dim=0):
    r'''変数の鉛直圧力勾配を求める関数.

    Parameters
    ----------
    variables: `numpy.ndarray`
        variable

        計算したい変数
    pres_3d: `numpy.ndarray`
        pressure(3d). The same shape as var
        Use pressure_3d from 1d pressure array.

        変数と同じ形で無ければならない.
    wrfon: `int`
        Flag whether input data is wrfout or not

        入力データがwrfoutか否かのフラグ
    
    Returns
    -------
    `numpy.ndarray`
        vertical gradient

    Note
    -----
    .. math:: {VerticalGradient}_{n+1/2} &= \frac{-\left(f(p_{n}) - f(p_{n+1})\right)}{-\left(p_{n} - p_{n+1}\right)} \\
        &= \frac{\left(f(p_{n+1}) - f(p_{n})\right)}{\left(p_{n+1} - p_{n}\right)}

    
    '''
    if pres_3d.ndim == 1:
        pres_3d = pressure_nd(pres_3d, lat_dim=variables.shape[-2], lon_dim=variables.shape[-1])
    vertical_grad = np.ma.zeros(variables.shape)
    diff_pres = np.diff(pres_3d, axis=z_dim)
    grad_var = np.diff(variables, axis=z_dim)/diff_pres
    vertical_grad[0] = grad_var[0]
    vertical_grad[-1] = grad_var[-1]
    diff_pres_sum = diff_pres[:-1] + diff_pres[1:]
    vertical_grad[1:-1] = grad_var[1:]/diff_pres_sum*diff_pres[:-1] + grad_var[:-1]/diff_pres_sum*diff_pres[1:]
    return vertical_grad


def vert_grad_4d(variables, pres_4d, z_dim=1):
    r'''変数の鉛直圧力勾配を求める関数.

    Parameters
    ----------
    variables: `numpy.ndarray`
        variable

        計算したい変数
    pres_4d: `numpy.ndarray`
        pressure(4d). The same shape as var
        Use pressure_4d from 1d pressure array.
        変数と同じ形で無ければならない.
    
    Returns
    -------
    `numpy.ndarray`
        vertical gradient

    Note
    -----
    .. math:: {VerticalGradient}_{n+1/2} &= \frac{-\left(f(p_{n}) - f(p_{n+1})\right)}{-\left(p_{n} - p_{n+1}\right)} \\
        &= \frac{\left(f(p_{n+1}) - f(p_{n})\right)}{\left(p_{n+1} - p_{n}\right)}

    '''
    if pres_4d.ndim == 1:
        pres_4d = pressure_nd(pres_4d, time_dim=variables.shape[0], lat_dim=variables.shape[-2], lon_dim=variables.shape[-1])
    vertical_grad = np.ma.zeros(variables.shape)
    diff_pres = np.diff(pres_4d, axis=z_dim)
    grad_var = np.diff(variables, axis=z_dim)/diff_pres
    vertical_grad[:, 0, :, :] = grad_var[:, 0, :, :]
    vertical_grad[:, -1, :, :] = grad_var[:, -1, :, :]
    diff_pres_sum = diff_pres[:, :-1, :, :] + diff_pres[:, 1:, :, :]
    vertical_grad[:, 1:-1, :, :] = grad_var[:, 1:, :, :]/diff_pres_sum*diff_pres[:, :-1, :, :] + \
        grad_var[:, :-1, :, :]/diff_pres_sum*diff_pres[:, 1:, :, :]
    return vertical_grad


def vert_grad(variables, pres_4d, z_dim=-3):
    r'''
    変数の鉛直圧力勾配を求める関数.

    Parameters
    ----------
    variables: `numpy.ndarray`
        variable

        計算したい変数
    pres_nd: `numpy.ndarray`
        pressure(nd). The same shape as var
        Use pressure_nd from 1d pressure array.

        変数と同じ形で無ければならない.
    
    Returns
    -------
    `numpy.ndarray`
        vertical gradient

    Note
    -----
    .. math:: {VerticalGradient}_{n+1/2} &= \frac{-\left(f(p_{n}) - f(p_{n+1})\right)}{-\left(p_{n} - p_{n+1}\right)} \\
        &= \frac{\left(f(p_{n+1}) - f(p_{n})\right)}{\left(p_{n+1} - p_{n}\right)}

    '''
    if pres_4d.ndim == 1:
        pres_4d = np.tile(pres_4d, (variables.shape[0]*variables.shape[-2]*variables.shape[-1])).reshape([variables.shape[-2], \
            variables.shape[-1], variables.shape[-3], variables.shape[0]]).transpose(2, 3, 0, 1)
    vertical_grad = np.ma.zeros(variables.shape)
    diff_pres = np.diff(pres_4d, axis=z_dim)
    grad_var = np.diff(variables, axis=z_dim)/diff_pres
    vertical_grad[..., 0, :, :] = grad_var[..., 0, :, :]
    vertical_grad[..., -1, :, :] = grad_var[..., -1, :, :]
    diff_pres_sum = diff_pres[..., :-1, :, :] + diff_pres[..., 1:, :, :]
    vertical_grad[..., 1:-1, :, :] = grad_var[..., 1:, :, :]/diff_pres_sum*diff_pres[..., :-1, :, :] + \
        grad_var[..., :-1, :, :]/diff_pres_sum*diff_pres[..., 1:, :, :]
    return vertical_grad


def advection_h_3d(var, wind_u, wind_v, dx, dy, wrfon=0):
    r'''変数の移流を求める関数.
    
    distance_3dを使ってdx, dyを求め、それらをこの関数の引数に渡すと計算できる

    Parameters
    ----------
    var: `numpy.ndarray`
        variable

        計算したい変数

    wind_u: `numpy.ndarray`
        eastward wind. The same shape as var.

        変数と同じ形で無ければならない.

    wind_v: `numpy.ndarray`
        northward wind. The same shape as var.

        変数と同じ形で無ければならない.

    dx: `numpy.ndarray`
        var.shape[-1]-1 == dx.shape[-1]

        経度方向の次元はvar.shape[-1]-1でなければならない
    dy: `numpy.ndarray`
        var.shape[-2]-1 == dy.shape[-2]

        経度方向の次元はvar.shape[-2]-1でなければならない
    wrfon: `int`
        Flag whether input data is wrfout or not

        入力データがwrfoutか否かのフラグ
    
    Returns
    -------
    `numpy.ndarray`
        advection
    
    '''
    warnings.warn(f"'{sys._getframe().f_code.co_name}' is deprecated. Please use '{sys._getframe().f_code.co_name[:-3]}'", FutureWarning, stacklevel=2)
    if (isinstance(dx, (int, float)))and(isinstance(dy, (int, float))):
        pass
    elif not ((var.shape[-2] == dx.shape[-2])and(var.shape[-1] == dx.shape[-1]+1)):
        raise NotAllowedDxShapeError('var', var, dx)
    elif not ((var.shape[-2] == dy.shape[-2]+1)and(var.shape[-1] == dy.shape[-1])):
        raise NotAllowedDyShapeError('var', var, dy)

    if np.any(dx<=0):
        raise InvalidDxValueError()
    if np.any(dy<=0):
        raise InvalidDyValueError()
    
    advs_shape = list(wind_u.shape)
    advs_shape.insert(0, 2) # grad_xとgrad_yの2つの次元を追加
    advs = np.ma.zeros(advs_shape)
    var_grad_x, var_grad_y = gradient_h_3d(var, dx, dy, wrfon=wrfon)
    advs[0] = -wind_u * var_grad_x
    advs[1] = -wind_v * var_grad_y
    return advs


def advection_h_4d(var, wind_u, wind_v, dx, dy, wrfon=0):
    r'''変数の移流を求める関数.

    distance_4dを使ってdx, dyを求め、それらをこの関数の引数に渡すと計算できる

    Parameters
    ----------
    var: `numpy.ndarray`
        variable

        計算したい変数
    wind_u: `numpy.ndarray`
        eastward wind. The same shape as var.

        変数と同じ形で無ければならない.
    wind_v: `numpy.ndarray`
        northward wind. The same shape as var.

        変数と同じ形で無ければならない.
    dx: `numpy.ndarray`
        var.shape[-1]-1 == dx.shape[-1]

        経度方向の次元はvar.shape[-1]-1でなければならない
    dy: `numpy.ndarray`
        var.shape[-2]-1 == dy.shape[-2]

        経度方向の次元はvar.shape[-2]-1でなければならない
    wrfon: `int`
        Flag whether input data is wrfout or not.

        入力データがwrfoutか否かのフラグ
    
    Returns
    -------
    `numpy.ndarray`
        advection
    
    '''
    warnings.warn(f"'{sys._getframe().f_code.co_name}' is deprecated. Please use '{sys._getframe().f_code.co_name[:-3]}'", FutureWarning, stacklevel=2)
    if (isinstance(dx, (int, float)))and(isinstance(dy, (int, float))):
        pass
    elif not ((var.shape[-2] == dx.shape[-2])and(var.shape[-1] == dx.shape[-1]+1)):
        raise NotAllowedDxShapeError('var', var, dx)
    elif not ((var.shape[-2] == dy.shape[-2]+1)and(var.shape[-1] == dy.shape[-1])):
        raise NotAllowedDyShapeError('var', var, dy)

    if np.any(dx<=0):
        raise InvalidDxValueError()
    if np.any(dy<=0):
        raise InvalidDyValueError()
    
    advs_shape = list(wind_u.shape)
    advs_shape.insert(0, 2) # grad_xとgrad_yの2つの次元を追加
    advs = np.ma.zeros(advs_shape)
    var_grad_x, var_grad_y = gradient_h_4d(var, dx, dy, wrfon=wrfon)
    advs[0] = -wind_u * var_grad_x
    advs[1] = -wind_v * var_grad_y
    return advs


def advection_h(var, wind_u, wind_v, dx, dy, wrfon=0):
    r'''変数の移流を求める関数.
    
    dx, dyは``distance_4d``を使って求め、それらをこの関数の引数に渡すと計算できる.
    dx, dyにintまたはfloatを代入するとそれが全てのdx, dyとなる.

    Parameters
    ----------
    var: `numpy.ndarray`
        variable

        計算したい変数
    wind_u: `numpy.ndarray`
        eastward wind. The same shape as var.

        変数と同じ形で無ければならない.
    wind_v: `numpy.ndarray`
        northward wind. The same shape as var.

        変数と同じ形で無ければならない.
    dx: `numpy.ndarray`
        var.shape[-1]-1 == dx.shape[-1]

        経度方向の次元はvar.shape[-1]-1でなければならない
    dy: `numpy.ndarray`
        var.shape[-2]-1 == dy.shape[-2]

        経度方向の次元はvar.shape[-2]-1でなければならない
    wrfon: `int`
        Flag whether input data is wrfout or not.

        入力データがwrfoutか否かのフラグ
    
    Returns
    -------
    `numpy.ndarray`
        advection
    
    '''
    if (isinstance(dx, (int, float)))and(isinstance(dy, (int, float))):
        pass
    elif not ((var.shape[-2] == dx.shape[-2])and(var.shape[-1] == dx.shape[-1]+1)):
        raise NotAllowedDxShapeError('var', var, dx)
    elif not ((var.shape[-2] == dy.shape[-2]+1)and(var.shape[-1] == dy.shape[-1])):
        raise NotAllowedDyShapeError('var', var, dy)

    if np.any(dx<=0):
        raise InvalidDxValueError()
    if np.any(dy<=0):
        raise InvalidDyValueError()
    
    advs_shape = list(wind_u.shape)
    advs_shape.insert(0, 2) # grad_xとgrad_yの2つの次元を追加
    advs = np.ma.zeros(advs_shape)
    var_grad_x, var_grad_y = gradient_h(var, dx, dy, wrfon=wrfon)
    advs[0] = -wind_u * var_grad_x
    advs[1] = -wind_v * var_grad_y
    return advs



def q_1(temperature_1, temperature_2, temperature_3, wind_u, wind_v, p_velocity, pressure, dx, dy, time_step=3600, wrfon=0):
    r'''Q1を気温を用いて求める関数.

    この関数は時間発展を計算する項が含まれているため、4次元の配列で計算される.
    temperatureに関しては時間変化は中央差分を用いるため、計算したい時間の気温だけで無く、
    その前後の時間の気温のデータも与える必要がある.

    dx, dyは`distance_4d`を使って求め、それらをこの関数の引数に渡すと計算できる.

    Parameters
    ----------
    temperature_1: `numpy.ndarray`
        temperature

        計算したい時間の前の時間のtemp.
        temperature_2と同じ形で無ければならない.
    temperature_2: `numpy.ndarray`
        temperature

        計算したい時間のtemp.
    temperature_3: `numpy.ndarray`
        temperature

        計算したい時間の後の時間のtemp.
        temperature_2と同じ形で無ければならない.
    wind_u: `numpy.ndarray`
        eastward wind. The same shape as var.

        変数と同じ形で無ければならない.
    wind_v: `numpy.ndarray`
        northward wind. The same shape as var.

        変数と同じ形で無ければならない.
    p_velocity: `numpy.ndarray`
        vertical p velocity. The same shape as var.

        変数と同じ形で無ければならない.
    pressure: `numpy.ndarray`
        pressure. The same shape as var.

        変数と同じ形で無ければならない.
    dx: `numpy.ndarray`
        var.shape[-1]-1 == dx.shape[-1]

        経度方向の次元はvar.shape[-1]-1でなければならない
    dy: `numpy.ndarray`
        var.shape[-2]-1 == dy.shape[-2]

        経度方向の次元はvar.shape[-2]-1でなければならない
    timestep: `float`
        default = 3600 (for ERA5).

        This varies on dataset.

        使用するデータによって変更する必要がある.
    wrfon: `int`
        Flag whether input data is wrfout or not.

        入力データがwrfoutか否かのフラグ
    
    Returns
    -------
    `numpy.ndarray`
        Q1 or Q11, Q12, Q13
    
    '''

    if np.any(dx<=0):
        raise InvalidDxValueError()
    if np.any(dy<=0):
        raise InvalidDyValueError()
    
    terms_shape = list(wind_u.shape)
    terms_shape.insert(0, 3) # grad_xとgrad_yの2つの次元を追加
    terms = np.ma.zeros(terms_shape)
    temperature = np.concatenate([temperature_1[-1:, :], temperature_2[:], temperature_3[:1, :]])
    time_evolv = np.diff(temperature, axis=0)
    terms[0] = Cp * (time_evolv[:-1] + time_evolv[1:]) / (2 * time_step)
    # grad_x_t, grad_y_t = gradient_h_4d(temperature_2, dx, dy)
    # term_2 = Cp * (wind_u * grad_x_t + wind_v * grad_y_t)
    advec_x, advec_y = -advection_h_4d(temperature_2, wind_u, wind_v, dx, dy, wrfon=wrfon)
    terms[1] = Cp * (advec_x + advec_y)
    terms[2] = Cp * ((pressure / P0) ** kappa) * p_velocity * vert_grad_4d(potential_temperature(pressure, temperature_2), pressure)
    return terms



def q_2_rh(temperature_1, temperature_2, temperature_3, rh_1, rh_2, rh_3, wind_u, wind_v, p_velocity, pressure, dx, dy, time_step=3600, wrfon=0):
    r'''Q2を相対湿度と気温を用いて混合比から求める関数.

    この関数は時間発展を計算する項が含まれているため、4次元の配列で計算される. 
    temperatureに関しては時間変化は中央差分を用いるため、計算したい時間の気温だけで無く
    その前後の時間の気温のデータも与える必要がある.

    distance_4dを使ってdx, dyを求め、それらをこの関数の引数に渡すと計算できる.

    Parameters
    ----------
    temperature_1: `numpy.ndarray`
        temperature

        計算したい時間の前の時間のtemp.
        temperature_2と同じ形で無ければならない.
    temperature_2: `numpy.ndarray`
        temperature

        計算したい時間のtemp.
    temperature_3: `numpy.ndarray`
        temperature

        計算したい時間の後の時間のtemp.
        temperature_2と同じ形で無ければならない.
    rh_1: `numpy.ndarray`
        Relative Humidity

        計算したい時間の前の時間の相対湿度.
        rh_2と同じ形で無ければならない.
    rh_2: `numpy.ndarray`
        Relative Humidity

        計算したい時間の相対湿度.
    rh_3: `numpy.ndarray`
        Relative Humidity

        計算したい時間の後の時間の相対湿度.
        rh_2と同じ形で無ければならない.
    wind_u: `numpy.ndarray`
        eastward wind. The same shape as var.

        変数と同じ形で無ければならない.
    wind_v: `numpy.ndarray`
        northward wind. The same shape as var.

        変数と同じ形で無ければならない.
    p_velocity: `numpy.ndarray`
        vertical p velocity. The same shape as var.

        変数と同じ形で無ければならない.
    pressure: `numpy.ndarray`
        pressure. The same shape as var.

        変数と同じ形で無ければならない.
    dx: `numpy.ndarray`
        var.shape[-1]-1 == dx.shape[-1]

        経度方向の次元はvar.shape[-1]-1でなければならない
    dy: `numpy.ndarray`
        var.shape[-2]-1 == dy.shape[-2]

        経度方向の次元はvar.shape[-2]-1でなければならない
    timestep: `float`
        default = 3600 (for ERA5)
        
        This varies on dataset.
        
        使用するデータによって変更する必要がある.
    wrfon: `int`
        Flag whether input data is wrfout or not.

        入力データがwrfoutか否かのフラグ
    
    Returns
    -------
    `numpy.ndarray`
        Q2 or Q21, Q22, Q23
    
    '''

    if np.any(dx<=0):
        raise InvalidDxValueError()
    if np.any(dy<=0):
        raise InvalidDyValueError()
    
    terms_shape = list(wind_u.shape)
    terms_shape.insert(0, 3) # grad_xとgrad_yの2つの次元を追加
    terms = np.ma.zeros(terms_shape)
    temperature = np.concatenate([temperature_1[-1:, :], temperature_2[:], temperature_3[:1, :]])
    rh = np.concatenate([rh_1[-1:, :], rh_2[:], rh_3[:1, :]])
    pres_add = np.concatenate([pressure[0, :], pressure])
    terms[0] = -LatHeatC * np.diff(mixing_ratio_from_relative_humidity(rh, temperature, pres_add), axis=0) / time_step
    mix_2 = mixing_ratio_from_relative_humidity(rh_2, temperature_2, pressure)
    # grad_x_t, grad_y_t = gradient_h_4d(temperature_2, dx, dy)
    # term_2 = Cp * (wind_u * grad_x_t + wind_v * grad_y_t)
    advec_x, advec_y = -advection_h_4d(mix_2, wind_u, wind_v, dx, dy, wrfon=wrfon)
    terms[1] = -LatHeatC * (advec_x + advec_y)
    terms[2] = -LatHeatC * (p_velocity * vert_grad_4d(mix_2, pressure))
    return terms



def q_2_sh_mix(sh_1, sh_2, sh_3, wind_u, wind_v, p_velocity, pressure, dx, dy, time_step=3600, wrfon=0):
    r'''Q2を比湿を用いて混合比から求める関数.

    この関数は時間発展を計算する項が含まれているため、4次元の配列で計算される.
    temperatureに関しては時間変化は中央差分を用いるため、計算したい時間の気温だけで無く
    その前後の時間の気温のデータも与える必要がある.

    dx, dyは`distance_4d`を使って求め、それらをこの関数の引数に渡すと計算できる.

    Parameters
    ----------
    sh_1: `numpy.ndarray`
        Relative Humidity

        計算したい時間の前の時間の比湿.
        sh_2と同じ形で無ければならない.
    sh_2: `numpy.ndarray`
        Relative Humidity

        計算したい時間の比湿
    sh_3: `numpy.ndarray`
        Relative Humidity
        
        計算したい時間の後の時間の比湿.
        sh_2と同じ形で無ければならない.
    wind_u: `numpy.ndarray`
        eastward wind. The same shape as var.
        
        変数と同じ形で無ければならない.
    wind_v: `numpy.ndarray`
        northward wind. The same shape as var.
        
        変数と同じ形で無ければならない.
    p_velocity: `numpy.ndarray`
        vertical p velocity. The same shape as var.
        
        変数と同じ形で無ければならない.
    pressure: `numpy.ndarray`
        pressure. The same shape as var.
        
        変数と同じ形で無ければならない.
    dx: `numpy.ndarray`
        var.shape[-1]-1 == dx.shape[-1]
        
        経度方向の次元はvar.shape[-1]-1でなければならない
    dy: `numpy.ndarray`
        var.shape[-2]-1 == dy.shape[-2]
        
        経度方向の次元はvar.shape[-2]-1でなければならない
    timestep: `float`
        default = 3600 (for ERA5)
        
        This varies on dataset.
        
        使用するデータによって変更する必要がある.
    wrfon: `int`
        Flag whether input data is wrfout or not.
        
        入力データがwrfoutか否かのフラグ
    
    Returns
    -------
    `numpy.ndarray`
        Q2 or Q21, Q22, Q23
    
    '''

    if np.any(dx<=0):
        raise InvalidDxValueError()
    if np.any(dy<=0):
        raise InvalidDyValueError()
    
    terms_shape = list(wind_u.shape)
    terms_shape.insert(0, 3) # grad_xとgrad_yの2つの次元を追加
    terms = np.ma.zeros(terms_shape)
    sh = np.concatenate([sh_1[-1:, :], sh_2[:], sh_3[:1, :]])
    time_evolv = np.diff(mixing_ratio_from_specific_humidity(sh), axis=0)
    terms[0] = -LatHeatC * (time_evolv[:-1] + time_evolv[1:]) / (2 * time_step)
    # terms[0] = -LatHeatC * np.diff(sh, axis=0) / time_step
    mix_2 = mixing_ratio_from_specific_humidity(sh_2)
    advec_x, advec_y = -advection_h_4d(mix_2, wind_u, wind_v, dx, dy, wrfon=wrfon)
    # advec_x, advec_y = -advection_h_4d(sh_2, wind_u, wind_v, dx, dy, wrfon=wrfon)
    terms[1] = -LatHeatC * (advec_x + advec_y)
    terms[2] = -LatHeatC * (p_velocity * vert_grad_4d(mix_2, pressure))
    # terms[2] = -LatHeatC * (p_velocity * vert_grad_4d(sh_2, pressure))
    return terms



def q_2_sh_sh(sh_1, sh_2, sh_3, wind_u, wind_v, p_velocity, pressure, dx, dy, time_step=3600, wrfon=0):
    r'''Q2を比湿を用いて比湿から求める関数.

    この関数は時間発展を計算する項が含まれているため、4次元の配列で計算される.
    temperatureに関しては時間変化は中央差分を用いるため、計算したい時間の気温だけで無く
    その前後の時間の気温のデータも与える必要がある.

    dx, dyは`distance_4d`を使って求め、それらをこの関数の引数に渡すと計算できる.

    Parameters
    ----------
    sh_1: `numpy.ndarray`
        Relative Humidity
        
        計算したい時間の前の時間の比湿.
        sh_2と同じ形で無ければならない.
    sh_2: `numpy.ndarray`
        Relative Humidity
        
        計算したい時間の比湿.
    sh_3: `numpy.ndarray`
        Relative Humidity
        
        計算したい時間の後の時間の比湿.
        sh_2と同じ形で無ければならない.
    wind_u: `numpy.ndarray`
        eastward wind. The same shape as var.
        
        変数と同じ形で無ければならない.
    wind_v: `numpy.ndarray`
        northward wind. The same shape as var.
        
        変数と同じ形で無ければならない.
    p_velocity: `numpy.ndarray`
        vertical p velocity. The same shape as var.
        
        変数と同じ形で無ければならない.
    pressure: `numpy.ndarray`
        pressure. The same shape as var.
        
        変数と同じ形で無ければならない.
    dx: `numpy.ndarray`
        var.shape[-1]-1 == dx.shape[-1]
        
        経度方向の次元はvar.shape[-1]-1でなければならない
    dy: `numpy.ndarray`
        var.shape[-2]-1 == dy.shape[-2]
        
        経度方向の次元はvar.shape[-2]-1でなければならない
    timestep: `float`
        default = 3600 (for ERA5)
        
        This varies on dataset.
        
        使用するデータによって変更する必要がある.
    wrfon: `int`
        Flag whether input data is wrfout or not.
        
        入力データがwrfoutか否かのフラグ
    
    Returns
    -------
    `numpy.ndarray`
        Q2 or Q21, Q22, Q23
    
    '''

    if np.any(dx<=0):
        raise InvalidDxValueError()
    if np.any(dy<=0):
        raise InvalidDyValueError()
    
    terms_shape = list(wind_u.shape)
    terms_shape.insert(0, 3) # grad_xとgrad_yの2つの次元を追加
    terms = np.ma.zeros(terms_shape)
    sh = np.concatenate([sh_1[-1:, :], sh_2[:], sh_3[:1, :]])
    # terms[0] = -LatHeatC * np.diff(mixing_ratio_from_specific_humidity(sh), axis=0) / time_step
    time_evolv = np.diff(sh, axis=0)
    terms[0] = -LatHeatC * (time_evolv[:-1] + time_evolv[1:]) / (2 * time_step)
    # mix_2 = mixing_ratio_from_specific_humidity(sh_2)
    # advec_x, advec_y = -advection_h_4d(mix_2, wind_u, wind_v, dx, dy, wrfon=wrfon)
    advec_x, advec_y = -advection_h_4d(sh_2, wind_u, wind_v, dx, dy, wrfon=wrfon)
    terms[1] = -LatHeatC * (advec_x + advec_y)
    # terms[2] = -LatHeatC * (p_velocity * vert_grad_4d(mix_2, pressure))
    terms[2] = -LatHeatC * (p_velocity * vert_grad_4d(sh_2, pressure))
    return terms


def pressure_4d(pres, *, time_dim=24, lat_dim=201, lon_dim=401):
    r'''1次元の気圧の配列から4次元の気圧の配列を返す関数.
    
    気圧を計算に用いる際に使います.

    Parameters
    ----------
    pres: `numpy.ndarray`
        pressure(1d)
    
    Returns
    -------
    `numpy.ndarray`
        pressure(4d)
    
    '''
    warnings.warn(f"'{sys._getframe().f_code.co_name}' is deprecated. Please use '{sys._getframe().f_code.co_name[:-3]}_nd'", DeprecationWarning, stacklevel=2)
    # return np.tile(pres, time_dim*lat_dim*lon_dim).reshape(lon_dim, lat_dim, time_dim, len(pres)).transpose(2, 3, 1, 0)
    pres = pres.reshape(len(pres), 1, 1)
    return np.tile(pres, (time_dim, 1, lat_dim, lon_dim))


def pressure_3d(pres, *, lat_dim=201, lon_dim=401):
    r'''1次元の気圧の配列から3次元の気圧の配列を返す関数.
    
    気圧を計算に用いる際に使います.

    Parameters
    ----------
    pres: `numpy.ndarray`
        pressure(1d)
    
    Returns
    -------
    `numpy.ndarray`
        pressure(3d)
    
    '''
    warnings.warn(f"'{sys._getframe().f_code.co_name}' is deprecated. Please use '{sys._getframe().f_code.co_name[:-3]}_nd'", DeprecationWarning, stacklevel=2)
    # return np.tile(pres, lat_dim*lon_dim).reshape(lat_dim, lon_dim, len(pres)).transpose(2, 0, 1)
    pres = pres.reshape(len(pres), 1, 1)
    return np.tile(pres, (1, lat_dim, lon_dim))


def pressure_nd(pres, *, time_dim=None, lat_dim=201, lon_dim=401):
    r'''1次元の気圧の配列からn次元の気圧の配列を返す関数.
    
    気圧を計算に用いる際に使います.

    Parameters
    ----------
    pres: `numpy.ndarray`
        pressure(1d)
    
    Returns
    -------
    `numpy.ndarray`
        pressure(nd)
    
    '''
    pres = pres.reshape(len(pres), 1, 1)
    if time_dim==None:
        # return np.tile(pres, time_dim*lat_dim*lon_dim).reshape(lon_dim, lat_dim, time_dim, len(pres)).transpose(2, 3, 1, 0)
        return np.tile(pres, (1, lat_dim, lon_dim))
    else:
        # return np.tile(pres, lat_dim*lon_dim).reshape(lat_dim, lon_dim, len(pres)).transpose(2, 0, 1)
        return np.tile(pres, (time_dim, 1, lat_dim, lon_dim))



def vert_grad_4d_height(variables, height, z_dim=1):
    r'''変数の鉛直高度勾配を求める関数.

    Parameters
    ----------
    variables: `numpy.ndarray`
        variable.
        
        計算したい変数
    height: `numpy.ndarray`
        height(4d). The same shape as var.
        
        ジオポテンシャル高度を用いる.
    
    Returns
    -------
    `numpy.ndarray`
        vertical gradient

    '''
    vertical_grad = np.ma.zeros(variables.shape)
    diff_pres = np.diff(height, axis=z_dim)
    grad_var = np.diff(variables, axis=z_dim)/diff_pres
    vertical_grad[:, 0, :, :] = grad_var[:, 0, :, :]
    vertical_grad[:, -1, :, :] = grad_var[:, -1, :, :]
    diff_pres_sum = diff_pres[:, :-1, :, :] + diff_pres[:, 1:, :, :]
    vertical_grad[:, 1:-1, :, :] = grad_var[:, 1:, :, :]/diff_pres_sum*diff_pres[:, :-1, :, :] + \
        grad_var[:, :-1, :, :]/diff_pres_sum*diff_pres[:, 1:, :, :]
    return vertical_grad


def vert_grad_3d_height(variables, height, z_dim=0):
    r'''変数の鉛直高度勾配を求める関数.

    Parameters
    ----------
    variables: `numpy.ndarray`
        variable
        
        計算したい変数
    height: `numpy.ndarray`
        height(3d). The same shape as var.
        
        ジオポテンシャル高度を用いる.
    
    Returns
    -------
    `numpy.ndarray`
        vertical gradient

    '''
    vertical_grad = np.ma.zeros(variables.shape)
    diff_pres = np.diff(height, axis=z_dim)
    grad_var = np.diff(variables, axis=z_dim)/diff_pres
    vertical_grad[0, :, :] = grad_var[0, :, :]
    vertical_grad[-1, :, :] = grad_var[-1, :, :]
    diff_pres_sum = diff_pres[:-1, :, :] + diff_pres[1:, :, :]
    vertical_grad[1:-1, :, :] = grad_var[1:, :, :]/diff_pres_sum*diff_pres[:-1, :, :] + \
        grad_var[:-1, :, :]/diff_pres_sum*diff_pres[1:, :, :]
    return vertical_grad


def vert_grad_2d_height(variables, height, z_dim=0):
    r'''変数の鉛直高度勾配を求める関数.

    Parameters
    ----------
    variables: `numpy.ndarray`
        variable.
        
        計算したい変数
    height: `numpy.ndarray`
        height(2d). The same shape as var.
        
        ジオポテンシャル高度を用いる.
    
    Returns
    -------
    `numpy.ndarray`
        vertical gradient

    '''
    vertical_grad = np.ma.zeros(variables.shape)
    diff_pres = np.diff(height, axis=z_dim)
    grad_var = np.diff(variables, axis=z_dim)/diff_pres
    vertical_grad[0, :] = grad_var[0, :]
    vertical_grad[-1, :] = grad_var[-1, :]
    diff_pres_sum = diff_pres[:-1, :] + diff_pres[1:, :]
    vertical_grad[1:-1, :] = grad_var[1:, :]/diff_pres_sum*diff_pres[:-1, :] + \
        grad_var[:-1, :]/diff_pres_sum*diff_pres[1:, :]
    return vertical_grad

def richardson_number(temp, rh, height, pres, u, v):
    r'''リチャードソン数を求める関数.
    
    変数はすべて同じ形で無ければならない.
    
    Variables should be the same shape.

    Parameters
    ----------
    temp: `numpy.ndarray`
        Temperature
    rh: `numpy.ndarray`
        Relative Humidity
    height: `numpy.ndarray`
        (Geopotential) Height
    pres: `numpy.ndarray`
        pressure
    u: `numpy.ndarray`
        eastward wind
    v: `numpy.ndarray`
        northward wind

    Returns
    -------
    `numpy.ndarray`
        Richardson Number
    
    '''
    v_pt = potential_temperature(pressure_4d(pres), virtual_temperature(temp, mixing_ratio_from_relative_humidity(rh, temp, pres)))
    return g0/v_pt(vert_grad_4d_height(v_pt, height))/(vert_grad_4d_height(u, height)**2+vert_grad_4d_height(v, height)**2)



def geostrophic_wind(geopotential, dx, dy, f0=f0):
    r'''地衡風を求める関数.
    
    ジオポテンシャルの水平微分を行い、コリオリパラメタで割った後、 
    u成分にマイナスをかける. 

    Parameters
    ----------
    geopotential: `numpy.ndarray`
        Geopotential (Not Geopotential Height)
        
        ジオポテンシャル (ジオポテンシャル高度では無い)
    dx: `numpy.ndarray`
        東西方向の距離
    dy: `numpy.ndarray`
        南北方向の距離

    Returns
    -------
    `numpy.ndarray`
        geostrophic wind
        
        地衡風
    
    '''
    # terms = gradient_h_4d(geopotential, dx, dy)/f0
    terms = gradient_h(geopotential, dx, dy)[::-1]/f0
    terms[0] *= -1
    return terms


def ageostrophic_wind(geopotential, u_wind, v_wind, dx, dy, f0=f0):
    r'''非地衡風成分を求める関数.
    
    実際の風の東西・南北成分から地衡風成分を引く. 

    Parameters
    ----------
    geopotential: `numpy.ndarray`
        Geopotential (Not Geopotential Height)
        
        ジオポテンシャル (ジオポテンシャル高度では無い)
    u_wind: `numpy.ndarray`
        eastward wind
    v_wind: `numpy.ndarray`
        northward wind
    dx: `numpy.ndarray`
        東西方向の距離
    dy: `numpy.ndarray`
        南北方向の距離

    Returns
    -------
    `numpy.ndarray`
        ageostrophic wind
        
        非地衡風
    
    '''
    terms = geostrophic_wind(geopotential, dx, dy, f0)
    terms[0] -= u_wind
    terms[1] -= v_wind
    return terms


def relative_vorticity(u, v, dx, dy):
    r'''相対渦度を求める関数.

    Parameters
    ----------
    u: `numpy.ndarray`
        eastward wind
    v: `numpy.ndarray`
        northward wind
    dx: `numpy.ndarray`
        東西方向の距離
    dy: `numpy.ndarray`
        南北方向の距離

    Returns
    -------
    `numpy.ndarray`
        Relative Vorticity
        
        相対渦度
    
    '''
    # v_x_comp, _ = gradient_h_4d(v, dx, dy)
    # _, u_y_comp = gradient_h_4d(u, dx, dy)
    v_x_comp, _ = gradient_h(v, dx, dy)
    _, u_y_comp = gradient_h(u, dx, dy)
    return v_x_comp - u_y_comp



def lapse_rate(pressure, temperature, height):
    r"""実際の断熱減率などの呼び方がある. 
    
    詳しくはHolton 5th edition pp54 

    変数はすべて同じ形で無ければならない.
    
    Variables should be the same shape.

    Parameters
    ----------
    pressure: `numpy.ndarray`
        Pressure
    temperature: `numpy.ndarray`
        Temperature
    height: `numpy.ndarray`
        (Geopotential) Height

    Returns
    -------
    `numpy.ndarray`
        Lapse Rate
    
    """
    theta = potential_temperature(pressure, temperature)
    return GammaD-temperature/theta*vert_grad_4d_height(theta, height)


def pseudoadiabatic_lapse_rate(pressure, temperature):
    r"""偽断熱減率、湿潤断熱減率などの呼び方がある. 
    
    詳しくはHolton 5th edition pp61 

    変数はすべて同じ形で無ければならない.
    
    Variables should be the same shape.

    Parameters
    ----------
    pressure: `numpy.ndarray`
        Pressure
    temperature: `numpy.ndarray`
        Temperature

    Returns
    -------
    `numpy.ndarray`
        Psuedadiabatic Lapse Rate
    
    Note
    -----

    .. math:: \Gamma_s\equiv-\frac{dT}{dz}=\Gamma_d\frac{[1+L_cq_s/(RT)]}{\left[1+\varepsilon L_c^2q_s/(c_pRT^2)\right]}
    
    """
    qs = saturation_mixing_ratio(pressure, temperature)
    numerator = 1 + LatHeatC*qs/(R*temperature)
    denominator = 1 + (epsilone*LatHeatC**2*qs)/(Cp*R*temperature**2)
    return GammaD*numerator/denominator


def static_stability(pressure, temperature):
    r""" 大気の安定度を求める関数.

    変数はすべて同じ形で無ければならない.
    
    Variables should be the same shape.

    Parameters
    ----------
    pressure: `numpy.ndarray`
        Pressure
    temperature: `numpy.ndarray`
        Temperature

    Returns
    -------
    `numpy.ndarray`
        Static Stability
    
    Note
    -----

    .. math:: -\frac{RT}{p}\left(\frac{\partial \log\theta}{\partial p}\right)
    """
    return -(R*temperature/pressure)*vert_grad_4d(np.log(potential_temperature(pressure, temperature)), pressure)


def coriolis_parameter(lat):
    r"""コリオリパラメタを求める関数.

    Parameters
    ----------
    lat: `numpy.ndarray`
        Pressure

    Returns
    -------
    `numpy.ndarray`
        Corioli's Parameter
    
    Note
    -----

    .. math:: f=2\bg{\Omega}\sin\phi
    """
    return 2*Omega*np.sin(np.deg2rad(lat))


def gravitational_constant(height):
    r"""重力定数を求める関数.

    Parameters
    ----------
    height: `numpy.ndarray`
        height

    Returns
    -------
    `numpy.ndarray`
        Gravitational constant
    
    Note
    -----

    .. math:: g(z) = g0\left(\frac{R_e}{R_e+z}\right)^2
    """
    return g0*(Re/(Re+height))**2


def height_to_geopotential(height):
    r"""高度からジオポテンシャルを求める関数.

    Parameters
    ----------
    height: `numpy.ndarray`
        height

    Returns
    -------
    `numpy.ndarray`
        Geopotential
    
    Note
    -----

    .. math:: \Phi = \frac{g(z)R_ez}{R_e+z}
    """
    return (g0*Re*height)/(Re+height)
    

def geopotential_to_height(geopotential):
    r"""ジオポテンシャルから高度を求める関数.

    Parameters
    ----------
    height: `numpy.ndarray`
        Geopotential

    Returns
    -------
    `numpy.ndarray`
        Height
    
    Note
    -----

    .. math:: z = \frac{\Phi R_e}{gR_e-\Phi}
    """
    return (geopotential*Re)/(g0*Re-geopotential)


def ps2ps_distance(lon1, lat1, lon2, lat2):
  r"""地点間の距離を求める関数.
  
  単一の地点間の距離を求める場合はp2p_distanceの方が処理が早い.

  Parameters
  ----------
  lon1: `numpy.ndarray`
      Longitude of point(s)1
      
  lat1: `numpy.ndarray`
      Latitude of point(s)1

  lon2: `numpy.ndarray` or `int` or `float`
      Longitude of point(s)2

  lat2: `numpy.ndarray` or `int` or `float`
      Latitude of point(s)2

  Returns
  -------
  `numpy.ndarray`
      distance between points1 and points2
  """
  if (isinstance(lon1, (list, tuple)))or(isinstance(lon2, (list, tuple)))\
    or(isinstance(lat1, (list, tuple)))or(isinstance(lat2, (list, tuple))):
    lon1 = np.array(lon1)
    lon2 = np.array(lon2)
    lat1 = np.array(lat1)
    lat2 = np.array(lat2)
    
  if (isinstance(lon2, (int, float)))and(isinstance(lat2, (int, float)))\
    and(isinstance(lat1, (int, float)))and(isinstance(lon1, (int, float))):
    warnings.warn(f"'{sys._getframe().f_code.co_name}' may be slow in calculate distance between a single point and another single point. Please use 'p2p_distance', which may be faster.", DeprecationWarning, stacklevel=2)

  radius =  Re
  
  dlon = lon2 - lon1
  dlat = lat2 - lat1
  
  a = np.sin(np.deg2rad(dlat) / 2)**2 + np.cos(np.deg2rad(lat1)) * np.cos(np.deg2rad(lat2)) * np.sin(np.deg2rad(dlon) / 2)**2
  c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
  
  distance = radius * c
  return distance


def p2p_distance(lon1, lat1, lon2, lat2):
  r"""単一の地点間の距離を求める関数.

  Parameters
  ----------
  lon1: `numpy.ndarray`
      Longitude of point1
      
  lat1: `numpy.ndarray`
      Latitude of point1

  lon2: `numpy.ndarray`
      Longitude of point2

  lat2: `numpy.ndarray`
      Latitude of point2

  Returns
  -------
  `numpy.ndarray`
      distance between point1 and point2
  """
  from math import radians, cos, sin, atan2, sqrt
  radius =  Re
  
  dlon = lon2 - lon1
  dlat = lat2 - lat1
  
  a = sin(radians(dlat) / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(radians(dlon) / 2)**2
  c = 2 * atan2(sqrt(a), sqrt(1 - a))
  
  distance = radius * c
  return distance

