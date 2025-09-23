/**
 * @file   travt.h
 * @author Zhu Dengda (zhudengda@mail.iggcas.ac.cn)
 * @date   2024-08
 * 
 *    计算一维均匀半无限层状介质的初至走时
 * 
 */

#pragma once 

#include "grt/common/const.h"

/**
 * 已知每层的厚度和速度，且震源和场点位于（虚拟）界面上,
 * 且不共享层位，即使深度相同，中间也考虑一个厚度为0的层。
 * 故当abs(isrc-ircv)==1时，说明两点位于同一物理层
 * 
 * @param[in]    Thk           每层厚度 
 * @param[in]    Vel0          每层速度
 * @param[in]    nlay          层数
 * @param[in]    isrc          震源所在层位
 * @param[in]    ircv          场点所在层位
 * @param[in]    dist          震中距
 */
MYREAL grt_compute_travt1d(
    const MYREAL *Thk, const MYREAL *Vel0, const int nlay, 
    const int isrc, const int ircv, const MYREAL dist);