/**
 * @file   ptam.c
 * @author Zhu Dengda (zhudengda@mail.iggcas.ac.cn)
 * @date   2024-07-24
 * 
 * 以下代码实现的是 峰谷平均法 ，参考：
 * 
 *         1. 张海明. 2021. 地震学中的Lamb问题（上）. 科学出版社
 *         2. Zhang, H. M., Chen, X. F., & Chang, S. (2003). 
 *               An efficient numerical method for computing synthetic seismograms 
 *               for a layered half-space with sources and receivers at close or same depths. 
 *               Seismic motion, lithospheric structures, earthquake and volcanic sources: 
 *               The Keiiti Aki volume, 467-486.
 * 
 */

#include <stdio.h> 
#include <complex.h>
#include <stdlib.h>

#include "grt/common/ptam.h"
#include "grt/common/quadratic.h"
#include "grt/common/integral.h"
#include "grt/common/iostats.h"
#include "grt/common/const.h"
#include "grt/common/model.h"


/**
 * 处理并确定波峰或波谷                                    
 * 
 * @param[in]           ir        震中距索引                          
 * @param[in]           im        不同震源不同阶数的索引              
 * @param[in]           v         积分形式索引                          
 * @param[in]           k         波数                             
 * @param[in]           dk        波数步长                              
 * @param[in]           J3        存储的积分采样幅值数组                  
 * @param[in,out]       Kpt       积分值峰谷的波数数组     
 * @param[in,out]       Fpt       用于存储波峰/波谷点的幅值数组 
 * @param[in,out]       Ipt       用于存储波峰/波谷点的个数数组 
 * @param[in,out]       Gpt       用于存储等待迭次数的数组    
 * @param[in,out]       iendk0    一个布尔指针，用于指示是否满足结束条件 
 */
static void process_peak_or_trough(
    MYINT ir, MYINT im, MYINT v, MYREAL k, MYREAL dk, 
    MYCOMPLEX (*J3)[GRT_PTAM_WINDOW_SIZE][GRT_SRC_M_NUM][GRT_INTEG_NUM], MYREAL (*Kpt)[GRT_SRC_M_NUM][GRT_INTEG_NUM][GRT_PTAM_PT_MAX], 
    MYCOMPLEX (*Fpt)[GRT_SRC_M_NUM][GRT_INTEG_NUM][GRT_PTAM_PT_MAX], MYINT (*Ipt)[GRT_SRC_M_NUM][GRT_INTEG_NUM], MYINT (*Gpt)[GRT_SRC_M_NUM][GRT_INTEG_NUM], bool *iendk0)
{
    MYCOMPLEX tmp0;
    if (Gpt[ir][im][v] >= GRT_PTAM_WINDOW_SIZE-1 && Ipt[ir][im][v] < GRT_PTAM_PT_MAX) {
        if (grt_cplx_peak_or_trough(im, v, J3[ir], k, dk, &Kpt[ir][im][v][Ipt[ir][im][v]], &tmp0) != 0) {
            Fpt[ir][im][v][Ipt[ir][im][v]++] = tmp0;
            Gpt[ir][im][v] = 0;
        } else if (Gpt[ir][im][v] >= GRT_PTAM_WAITS_MAX) {  // 不再等待，直接取中点作为波峰波谷
            Kpt[ir][im][v][Ipt[ir][im][v]] = k - dk;
            Fpt[ir][im][v][Ipt[ir][im][v]++] = J3[ir][1][im][v];
            Gpt[ir][im][v] = 0;
        }
    }
    *iendk0 = *iendk0 && (Ipt[ir][im][v] == GRT_PTAM_PT_MAX);
}


/**
 * 在输入被积函数的情况下，对不同震源使用峰谷平均法
 * 
 * @param[in]           ir                  震中距索引
 * @param[in]           nr                  震中距个数
 * @param[in]           precoef             积分值系数
 * @param[in]           k                   波数                             
 * @param[in]           dk                  波数步长       
 * @param[in,out]       SUM3                被积函数的幅值数组 
 * @param[in,out]       sum_J               积分值数组 
 * 
 * @param[in,out]       Kpt                 积分值峰谷的波数数组     
 * @param[in,out]       Fpt                 用于存储波峰/波谷点的幅值数组 
 * @param[in,out]       Ipt                 用于存储波峰/波谷点的个数数组 
 * @param[in,out]       Gpt                 用于存储等待迭次数的数组 
 * 
 * @param[in,out]       iendk0              是否收集足够峰谷
 * 
 */
static void ptam_once(
    const MYINT ir, const MYINT nr, const MYREAL precoef, MYREAL k, MYREAL dk, 
    MYCOMPLEX SUM3[nr][GRT_PTAM_WINDOW_SIZE][GRT_SRC_M_NUM][GRT_INTEG_NUM],
    MYCOMPLEX sum_J[nr][GRT_SRC_M_NUM][GRT_INTEG_NUM],
    MYREAL Kpt[nr][GRT_SRC_M_NUM][GRT_INTEG_NUM][GRT_PTAM_PT_MAX],
    MYCOMPLEX Fpt[nr][GRT_SRC_M_NUM][GRT_INTEG_NUM][GRT_PTAM_PT_MAX],
    MYINT Ipt[nr][GRT_SRC_M_NUM][GRT_INTEG_NUM],
    MYINT Gpt[nr][GRT_SRC_M_NUM][GRT_INTEG_NUM],
    bool *iendk0)
{
    *iendk0 = true;
    for(MYINT i=0; i<GRT_SRC_M_NUM; ++i){
        MYINT modr = GRT_SRC_M_ORDERS[i];
        for(MYINT v=0; v<GRT_INTEG_NUM; ++v){
            if(modr == 0 && v!=0 && v!= 2)  continue;

            // 赋更新量
            // SUM3转为求和结果
            sum_J[ir][i][v] += SUM3[ir][GRT_PTAM_WINDOW_SIZE-1][i][v] * precoef;
            SUM3[ir][GRT_PTAM_WINDOW_SIZE-1][i][v] = sum_J[ir][i][v];         
            
            // 3点以上，判断波峰波谷 
            process_peak_or_trough(ir, i, v, k, dk, SUM3, Kpt, Fpt, Ipt, Gpt, iendk0);

            // 左移动点, 
            for(MYINT jj=0; jj<GRT_PTAM_WINDOW_SIZE-1; ++jj){
                SUM3[ir][jj][i][v] = SUM3[ir][jj+1][i][v];
            }

            // 点数+1
            Gpt[ir][i][v]++;
        }
    } 
}


void grt_PTA_method(
    const GRT_MODEL1D *mod1d, MYREAL k0, MYREAL predk, MYCOMPLEX omega, 
    MYINT nr, MYREAL *rs,
    MYCOMPLEX sum_J0[nr][GRT_SRC_M_NUM][GRT_INTEG_NUM],
    bool calc_upar,
    MYCOMPLEX sum_uiz_J0[nr][GRT_SRC_M_NUM][GRT_INTEG_NUM],
    MYCOMPLEX sum_uir_J0[nr][GRT_SRC_M_NUM][GRT_INTEG_NUM],
    FILE *ptam_fstatsnr[nr][2], GRT_KernelFunc kerfunc, MYINT *stats)
{   
    // 需要兼容对正常收敛而不具有规律波峰波谷的序列
    // 有时序列收敛比较好，不表现为规律的波峰波谷，
    // 此时设置最大等待次数，超过直接设置为中间值

    MYREAL k=0.0;

    // 不同震源不同阶数的核函数 F(k, w) 
    MYCOMPLEX QWV[GRT_SRC_M_NUM][GRT_QWV_NUM];
    MYCOMPLEX QWV_uiz[GRT_SRC_M_NUM][GRT_QWV_NUM];

    // 使用宏函数，方便定义
    #define __CALLOC_ARRAY(VAR, TYP, __ARR) \
        TYP (*VAR)__ARR = (TYP (*)__ARR)calloc(nr, sizeof(*VAR));

    // 用于接收F(ki,w)Jm(ki*r)ki
    // 存储采样的值，维度3表示通过连续3个点来判断波峰或波谷
    // 既用于存储被积函数，也最后用于存储求和的结果
    #define __ARR [GRT_PTAM_WINDOW_SIZE][GRT_SRC_M_NUM][GRT_INTEG_NUM]
        __CALLOC_ARRAY(SUM3, MYCOMPLEX, __ARR);
        __CALLOC_ARRAY(SUM3_uiz, MYCOMPLEX, __ARR);
        __CALLOC_ARRAY(SUM3_uir, MYCOMPLEX, __ARR);
    #undef __ARR

    // 之前求和的值
    #define __ARR [GRT_SRC_M_NUM][GRT_INTEG_NUM]
        __CALLOC_ARRAY(sum_J, MYCOMPLEX, __ARR);
        __CALLOC_ARRAY(sum_uiz_J, MYCOMPLEX, __ARR);
        __CALLOC_ARRAY(sum_uir_J, MYCOMPLEX, __ARR);
    #undef __ARR

    // 存储波峰波谷的位置和值
    #define __ARR [GRT_SRC_M_NUM][GRT_INTEG_NUM][GRT_PTAM_PT_MAX]
        __CALLOC_ARRAY(Kpt, MYREAL, __ARR);
        __CALLOC_ARRAY(Fpt, MYCOMPLEX, __ARR);

        __CALLOC_ARRAY(Kpt_uiz, MYREAL, __ARR);
        __CALLOC_ARRAY(Fpt_uiz, MYCOMPLEX, __ARR);

        __CALLOC_ARRAY(Kpt_uir, MYREAL, __ARR);
        __CALLOC_ARRAY(Fpt_uir, MYCOMPLEX, __ARR);
    #undef __ARR

    #define __ARR [GRT_SRC_M_NUM][GRT_INTEG_NUM]
        // 存储波峰波谷的总个数
        __CALLOC_ARRAY(Ipt, MYINT, __ARR);
        __CALLOC_ARRAY(Ipt_uiz, MYINT, __ARR);
        __CALLOC_ARRAY(Ipt_uir, MYINT, __ARR);

        // 记录点数，当峰谷找到后，清零
        __CALLOC_ARRAY(Gpt, MYINT, __ARR);
        __CALLOC_ARRAY(Gpt_uiz, MYINT, __ARR);
        __CALLOC_ARRAY(Gpt_uir, MYINT, __ARR);
    #undef __ARR
    #undef __CALLOC_ARRAY


    for(MYINT ir=0; ir<nr; ++ir){
        for(MYINT i=0; i<GRT_SRC_M_NUM; ++i){
            for(MYINT v=0; v<GRT_INTEG_NUM; ++v){
                sum_J[ir][i][v] = sum_J0[ir][i][v];

                if(calc_upar){
                    sum_uiz_J[ir][i][v] = sum_uiz_J0[ir][i][v];
                    sum_uir_J[ir][i][v] = sum_uir_J0[ir][i][v];
                }

                Ipt[ir][i][v] = Gpt[ir][i][v] = 0;
                Ipt_uiz[ir][i][v] = Gpt_uiz[ir][i][v] = 0;
                Ipt_uir[ir][i][v] = Gpt_uir[ir][i][v] = 0;
            }
        }
    }


    // 对于PTAM，不同震中距使用不同dk
    for(MYINT ir=0; ir<nr; ++ir){
        MYREAL dk = PI/((GRT_PTAM_WAITS_MAX-1)*rs[ir]); 
        MYREAL precoef = dk/predk; // 提前乘dk系数，以抵消格林函数主函数计算时最后乘dk
        // 根据波峰波谷的目标也给出一个kmax，+5以防万一 
        MYREAL kmax = k0 + (GRT_PTAM_PT_MAX+5)*PI/rs[ir];

        bool iendk0=false;

        // 积分过程文件
        FILE *fstatsK = ptam_fstatsnr[ir][0];

        k = k0;
        while(true){
            if(k > kmax) break;
            k += dk;

            // 计算核函数 F(k, w)
            kerfunc(mod1d, omega, k, QWV, calc_upar, QWV_uiz, stats); 
            if(*stats==GRT_INVERSE_FAILURE)  goto BEFORE_RETURN;

            // 记录核函数
            if(fstatsK!=NULL)  grt_write_stats(fstatsK, k, QWV);

            // 计算被积函数一项 F(k,w)Jm(kr)k
            grt_int_Pk(k, rs[ir], QWV, false, SUM3[ir][GRT_PTAM_WINDOW_SIZE-1]);  // [GRT_PTAM_WINDOW_SIZE-1]表示把新点值放在最后
            // 判断和记录波峰波谷
            ptam_once( ir, nr, precoef, k, dk,  SUM3, sum_J, Kpt, Fpt, Ipt, Gpt, &iendk0);
            
            // -------------------------- 位移空间导数 ------------------------------------
            if(calc_upar){
                // ------------------------------- ui_z -----------------------------------
                // 计算被积函数一项 F(k,w)Jm(kr)k
                grt_int_Pk(k, rs[ir], QWV_uiz, false, SUM3_uiz[ir][GRT_PTAM_WINDOW_SIZE-1]);  // [GRT_PTAM_WINDOW_SIZE-1]表示把新点值放在最后
                // 判断和记录波峰波谷
                ptam_once(ir, nr, precoef, k, dk, SUM3_uiz, sum_uiz_J, Kpt_uiz, Fpt_uiz, Ipt_uiz, Gpt_uiz, &iendk0);

                // ------------------------------- ui_r -----------------------------------
                // 计算被积函数一项 F(k,w)Jm(kr)k
                grt_int_Pk(k, rs[ir], QWV, true, SUM3_uir[ir][GRT_PTAM_WINDOW_SIZE-1]);  // [GRT_PTAM_WINDOW_SIZE-1]表示把新点值放在最后
                // 判断和记录波峰波谷
                ptam_once(ir, nr, precoef, k, dk, SUM3_uir, sum_uir_J, Kpt_uir, Fpt_uir, Ipt_uir, Gpt_uir, &iendk0);
            
            } // END if calc_upar


            if(iendk0) break;
        }// end k loop
    }

    // printf("w=%f, ik=%d\n", creal(omega), ik);


    // 做缩减序列，赋值最终解
    for(MYINT ir=0; ir<nr; ++ir){
        FILE *fstatsP = ptam_fstatsnr[ir][1];
        // 记录到文件
        if(fstatsP!=NULL)  grt_write_stats_ptam(fstatsP, Kpt[ir], Fpt[ir]);

        for(MYINT i=0; i<GRT_SRC_M_NUM; ++i){
            for(MYINT v=0; v<GRT_INTEG_NUM; ++v){
                grt_cplx_shrink(Ipt[ir][i][v], Fpt[ir][i][v]);  
                sum_J0[ir][i][v] = Fpt[ir][i][v][0];

                if(calc_upar){
                    grt_cplx_shrink(Ipt_uiz[ir][i][v], Fpt_uiz[ir][i][v]);  
                    sum_uiz_J0[ir][i][v] = Fpt_uiz[ir][i][v][0];
                
                    grt_cplx_shrink(Ipt_uir[ir][i][v], Fpt_uir[ir][i][v]);  
                    sum_uir_J0[ir][i][v] = Fpt_uir[ir][i][v][0];
                }
            }
        }
    }

    BEFORE_RETURN:

    #define __FREE_ALL_ARRAY \
        X(SUM3)    X(SUM3_uiz)    X(SUM3_uir) \
        X(sum_J)   X(sum_uiz_J)   X(sum_uir_J) \
        X(Kpt)     X(Fpt)         X(Ipt)       X(Gpt) \
        X(Kpt_uiz)     X(Fpt_uiz)         X(Ipt_uiz)       X(Gpt_uiz) \
        X(Kpt_uir)     X(Fpt_uir)         X(Ipt_uir)       X(Gpt_uir) \

    #define X(A)  GRT_SAFE_FREE_PTR(A);
        __FREE_ALL_ARRAY
    #undef X
    #undef __FREE_ALL_ARRAY
}




MYINT grt_cplx_peak_or_trough(MYINT idx1, MYINT idx2, const MYCOMPLEX arr[GRT_PTAM_WINDOW_SIZE][GRT_SRC_M_NUM][GRT_INTEG_NUM], MYREAL k, MYREAL dk, MYREAL *pk, MYCOMPLEX *value){
    MYCOMPLEX f1, f2, f3;
    MYREAL rf1, rf2, rf3;
    MYINT stat=0;

    f1 = arr[0][idx1][idx2];
    f2 = arr[1][idx1][idx2];
    f3 = arr[2][idx1][idx2];

    rf1 = creal(f1);
    rf2 = creal(f2);
    rf3 = creal(f3);
    if     ( (rf1 <= rf2) && (rf2 >= rf3) )  stat = 1;
    else if( (rf1 >= rf2) && (rf2 <= rf3) )  stat = -1;
    else                                     stat =  0;

    if(stat==0)  return stat;

    MYREAL x1, x2, x3; 
    x3 = k;
    x2 = x3-dk;
    x1 = x2-dk;

    MYREAL xarr[3] = {x1, x2, x3};
    MYCOMPLEX farr[3] = {f1, f2, f3};

    // 二次多项式
    MYCOMPLEX a, b, c;
    grt_quad_term(xarr, farr, &a, &b, &c);

    MYREAL k0 = x2;
    *pk = k0;
    *value = 0.0;
    if(a != 0.0+0.0*I){
        k0 = - b / (2*a);

        // 拟合二次多项式可能会有各种潜在问题，例如f1,f2,f3几乎相同，此时a,b很小，k0值非常不稳定
        // 这里暂且使用范围来框定，如果在范围外，就直接使用x2的值
        if(k0 < x3 && k0 > x1){
            // printf("a=%f%+fI, b=%f%+fI, c=%f%+fI, xarr=(%f,%f,%f), yarr=(%f%+fI, %f%+fI, %f%+fI)\n", 
            //         creal(a),cimag(a),creal(b),cimag(b),creal(c),cimag(c),x1,x2,x3,creal(f1),cimag(f1),creal(f2),cimag(f2),creal(f3),cimag(f3));
            *pk = k0;
            *value = a*k0*k0 + b*k0;
        }
    } 
    *value += c;
    
    return stat;
}


void grt_cplx_shrink(MYINT n1, MYCOMPLEX *arr){
    for(MYINT n=n1; n>1; --n){
        for(MYINT i=0; i<n-1; ++i){
            arr[i] = 0.5*(arr[i] + arr[i+1]);
        }
    }
}