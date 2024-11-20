"""Generate math model data."""
import random
import csv
from typing import List, Tuple, cast
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm # type: ignore

JIT_STRENGTH = 4.6e-15
RO_PER = 3.69e-9

NB_SAMPLES = 200
CSCMM = (1, 200)

file_name = f'math_model/results/csc_jit{int(JIT_STRENGTH * 1e16)}_per{int(RO_PER * 1e11)}.csv'

def norm_pdf(x: List[float], mu: float, s: float) -> List[float]:
    """Get normal PDF."""
    result_pdf: List[float] = []
    for x_i in x:
        result_pdf.append(1.0 / (s * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((x_i - mu) / s)**2))
    return result_pdf

def h_vs_cs(dt_: float, st_: float, per: float) \
    -> Tuple[float, float, float, float, float, float, float, float]:
    """Generate entropy values."""
    varss = [per, per + dt_, st_, st_]
    pdf_w = dist_wt(varss, 1000)
    a = dist_r(varss, 100000, pdf_w)
    r = a[0]
    mu_r = a[1]
    s_r = a[2]

    # Normal distribution
    mu_r1 = varss[0] / (varss[1] - varss[0])
    s_r1 = np.sqrt(varss[0] / (varss[1] - varss[0])) * np.sqrt(varss[2]**2 + varss[3]**2) \
        / (varss[1] - varss[0])
    x = [0.0] * 1000
    for ii in range(1000):
        x[ii] = len(r) * ii / 999.0
    # r1 = norm_pdf(x, mu_r1, s_r1)

    # Entropy estimation Sim
    nb_bits: int = 1
    bins = [0.0] * (2**nb_bits)
    for ii in range(1, len(r) + 1, 1):
        for j in range(2**nb_bits):
            if ii % (2**nb_bits) == j:
                bins[j] = bins[j] + r[ii-1]
                break
    min_h = -np.log(max(bins)) / np.log(2**nb_bits)
    h = 0
    for ii in range(2**nb_bits):
        if bins[ii] != 0:
            h -= bins[ii] * np.log(bins[ii]) / np.log(2**nb_bits)

    # Entropy estimation Mod
    nb_bits_1 = 1
    bins_1 = [0.0] * (2**nb_bits_1)
    for ii in range(1, int(max(x) + 1), 1):
        for j in range(2**nb_bits_1):
            if ii % (2**nb_bits_1) == j:
                bins_1[j] = bins_1[j] + (norm_cdf(ii + 0.5, mu_r1, s_r1) \
                                         - norm_cdf(ii - 0.5, mu_r1, s_r1))
                break
    min_h_1 = -np.log(max(bins_1)) / np.log(2**nb_bits_1)
    h_1 = 0.0
    for ii in range(2**nb_bits_1):
        if bins_1[ii] != 0:
            h_1 = h_1 - bins_1[ii] * np.log(bins_1[ii]) / np.log(2**nb_bits_1)
    return min_h, h, mu_r, s_r, min_h_1, h_1, mu_r1, s_r1

def norm_cdf(x: float, mu: float, s: float) -> float:
    """Get normal CDF."""
    return norm.cdf((x - mu) / s) # type: ignore

def norm_cdf_list(x: List[float], mu: float, s: float) -> List[float]:
    """Get normal CDF."""
    result_: List[float] = []
    for x_i in x:
        result_.append(norm_cdf(x_i, mu, s))
    return result_

def dist_r(varss: List[float], nb_samples: int, dist_pdf_w: List[float]) \
    -> Tuple[List[float], float, int]:
    """Get R distribution."""
    mu_t1 = varss[0]
    mu_t2 = varss[1]
    s_t1 = varss[2]
    s_t2 = varss[3]
    samples = [0] * nb_samples
    for ii in range(nb_samples):
        r = (get_random_cdf(dist_pdf_w) - 1) / len(dist_pdf_w) * mu_t1 / 2
        t1 = mu_t1 + np.random.normal() * s_t1
        while r < t1:
            r = r + (mu_t2  -mu_t1) + np.random.normal() * np.sqrt(s_t1**2 + s_t2**2)
            if r < 0:
                t1 = 0
            samples[ii] = samples[ii] + 1
    rs = [0.0] * max(samples)
    for ii in range(nb_samples):
        if samples[ii] == 0:
            continue
        rs[samples[ii] - 1] = rs[samples[ii] - 1] + 1
    for ii, r_i in enumerate(rs):
        rs[ii] = r_i / nb_samples
    return rs, cast(float, np.mean(samples)), cast(int, np.std(samples))

def dist_wt(varss: List[float], length: int) -> List[float]:
    """Get WT distribution."""
    mu = abs(varss[1] - varss[0])
    s = np.sqrt(2) * (varss[2] + varss[3]) / 2
    u: List[float] = []
    for ii in range(length):
        u.append(ii * varss[0] / 2 / (length - 1))
    a: List[float] = []
    for ii in range(length):
        a.append(1 - norm_cdf(u[ii], mu, s))
    p: List[float] = [0] * len(u)
    for ii in range(length):
        for j in range(ii):
            p[ii] = p[ii] + 1 / mu * a[j] * max(u) / length
    pdf_wt: List[float] = [0.0] * len(p)
    pdf_wt[0] = p[0]
    for ii in range(1, length, 1):
        pdf_wt[ii] = p[ii] - sum(pdf_wt[0:ii])
    result_ = [x for x in pdf_wt]
    for ii in range(len(pdf_wt)):
        result_[ii] = result_[ii] / sum(pdf_wt)
    return result_

def get_random_cdf(pdf: List[float]) -> int:
    """Get random PDF index."""
    a = random.random()
    for ii in range(len(pdf)):
        if a < sum(pdf[0:ii + 1]):
            ra = ii
            return ra
    return 0

n = [0.0] * NB_SAMPLES
for i in range(NB_SAMPLES):
    n[i] = CSCMM[0] + i * (CSCMM[1] - CSCMM[0]) / (NB_SAMPLES - 1)
st = np.sqrt(JIT_STRENGTH * RO_PER)
dt = [0.0] * NB_SAMPLES
for i in range(NB_SAMPLES):
    dt[i] = RO_PER / n[i]

min_hs = [0.0] * NB_SAMPLES
h_s = [0.0] * NB_SAMPLES
mu_rs = [0.0] * NB_SAMPLES
s_rs = [0.0] * NB_SAMPLES
min_h_1s = [0.0] * NB_SAMPLES
h_1s = [0.0] * NB_SAMPLES
mu_r_1s = [0.0] * NB_SAMPLES
s_r_1s = [0.0] * NB_SAMPLES

with open(file_name, 'w', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',')
    csv_writer.writerow(['CSC', 'minH (sim)', 'H (sim)', 'mean R (sim)', 'std R (sim)',
                         'minH (norm)', 'H (norm)', 'mean R (sim)', 'std R (norm)'])

for i in range(NB_SAMPLES):
    print(i)
    result = h_vs_cs(dt[i], st, RO_PER)
    min_hs[i] = result[0]
    h_s[i] = result[1]
    mu_rs[i] = result[2]
    s_rs[i] = result[3]
    min_h_1s[i] = result[4]
    h_1s[i] = result[5]
    mu_r_1s[i] = result[6]
    s_r_1s[i] = result[7]
    with open(file_name, 'a', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow([n[i], min_hs[i], h_s[i], mu_rs[i], s_rs[i],
                             min_h_1s[i], h_1s[i], mu_r_1s[i], s_r_1s[i]])

plt.plot(n, min_hs) # type: ignore
plt.plot(n, min_h_1s) # type: ignore
plt.show() # type: ignore
