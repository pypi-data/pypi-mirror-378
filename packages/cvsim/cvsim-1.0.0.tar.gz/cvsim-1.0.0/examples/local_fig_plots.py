# keep local

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FormatStrFormatter, MultipleLocator
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import sys
sys.path.append(r'C:\Users\erico\Desktop\PyCharmProjects\cv_simulation\CVsim')

from scipy.optimize import curve_fit
from scipy import signal
from scipy.signal import savgol_filter
from src.cvsim.mechanisms import E_rev, E_q, EE
from src.cvsim.fit_curve import FitE_rev, FitE_q, FitEE

### plotting params
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.serif": ['Helvetica'],
})
plt.rc('axes', linewidth=1.2, labelsize=10)   # fontsize of the x and y labels (words)
plt.rc('xtick', labelsize=9)                  # fontsize of the tick labels (numbers) #labelsize=MEDIUM
plt.rc('ytick', labelsize=9)                  # fontsize of the tick labels
plt.rc('legend', fontsize=8)                  # legend fontsize
###############################################################################

x_ticks = { "top" : True, "direction" : "in", "minor.visible" : True,
            "major.size" : 4, "major.width" :  1.2, "minor.size" : 2, "minor.width" : 0.5}
y_ticks = x_ticks.copy()
y_ticks["right"] = y_ticks.pop("top")
plt.rc('xtick', **x_ticks)
plt.rc('ytick', **y_ticks)

save_loc = r'C:\Users\erico\Desktop\manuscripts\cvsim_chem_edu\figures\plots\\'
cv_data_loc = r'C:\Users\erico\Desktop\manuscripts\cvsim_chem_edu\cv_exp_data\\'
double_width = 7.0  # inches

####################################################################################

# fig 1
"""
# a) get small panel triangle wave annotated,
# b) small panel with just rev CV i vs E (just label both with E_start, E_switch..redox potential E^not prime _1,2)


fig = plt.figure(figsize=(double_width, double_width*0.6)) #layout="constrained",

gs = gridspec.GridSpec(2, 3, figure=fig)
ax1 = fig.add_subplot(gs[0, :2])
ax2 = fig.add_subplot(gs[1, :2], sharex=ax1)
ax3 = fig.add_subplot(gs[:, 2])

e_start = -0.4
e_rev = 0.4
step = 0.001
e_not = 0.0
n = int((e_rev - e_start)*2/step)

half_span = [e_start + (x*step) for x in range(int(n/2))]
neg_span = [e_rev - (x*step) for x in range(int(n/2)+1)]
#print(half_span[0],half_span[-1], neg_span[0], neg_span[-1])
tri_wave = half_span + neg_span

ax1.plot(np.arange(n+1), tri_wave, color="k", linewidth=2.5)

# make reversible CV
x_vals = np.arange(n)
v, i = E_rev(e_start, e_rev, e_not, 0.1, 1, 1e-6, 1e-6).simulate()
ax2.plot(x_vals, [y*1e6 for y in i], color="b", linewidth=2.5)

# dotted lines

# E_rev
alp = 0.3 # alpha
half_x = x_vals[int(len(x_vals)/2)]
ax1.plot((x_vals[0], half_x), (e_rev, e_rev), 'k--', linewidth=1.5, zorder=1, alpha=alp)
ax1.plot((half_x, half_x), (e_rev, -1), 'k--', linewidth=1.5, zorder=1, alpha=alp)

ax2.plot((half_x, half_x), (10, -10), 'k--', linewidth=1.5, zorder=1, alpha=alp)

# E_not
first_third_x = x_vals[int(len(x_vals)/4)]
sec_third_x = x_vals[int(len(x_vals)*(3/4))]
ax1.plot((x_vals[0], sec_third_x), (e_not, e_not), 'k--', linewidth=1.5, zorder=1, alpha=alp)
ax1.plot((sec_third_x, sec_third_x), (e_not, -1), 'k--', linewidth=1.5, zorder=1, alpha=alp)
ax1.plot((first_third_x, first_third_x), (e_not, -1), 'k--', linewidth=1.5, zorder=1, alpha=alp)

ax2.plot((sec_third_x, sec_third_x), (10, -10), 'k--', linewidth=1.5, zorder=1, alpha=alp)
ax2.plot((first_third_x, first_third_x), (10, -10), 'k--', linewidth=1.5, zorder=1, alpha=alp)


# zero current
ax2.plot((0, x_vals[-1]), (0,0), 'k:', linewidth=0.5, zorder=1, alpha=0.5)

# handle ticks and labels
ax1.tick_params(labelbottom=False)

# remove ticks
ax1.set_xticks([], minor=False)
#ax1.set_yticks([], minor=False)
ax2.set_xticks([], minor=False)
#ax2.set_yticks([], minor=False)

y1 = [-0.4, 0.0, 0.4]
labs = [r"$E_{start}$", r"$E^{o'}$", r"$E_{rev}$"]

ax1.set_yticks(y1)
ax1.set_yticklabels(labs, minor=False)
ax1.tick_params(axis='y', which='minor', length=0)

y2 = [0.0]
labs2 = ["0"]
ax2.set_yticks(y2)
ax2.set_yticklabels(labs2, minor=False)
ax2.tick_params(axis='y', which='minor', length=0)


# remove tick labels
ax2.set_xticklabels([])
#ax2.set_yticklabels([])

ax1.set_ylabel("Potential")# (V vs ref.)")
ax2.set_ylabel("Current", labelpad=18)
ax2.set_xlabel("Time")

ax3.axis('off')

ax1.set_ylim(e_start*1.1, e_rev*1.1)
ax2.set_xlim(x_vals[0], x_vals[-1])
ax2.set_ylim(-8, 8)

ax1.text(-0.1, 1.15, 'a.', transform=ax1.transAxes, fontsize=13, fontweight='bold', va='top', ha='right')
ax2.text(-0.1, 0.95, 'b.', transform=ax2.transAxes, fontsize=13, fontweight='bold', va='top', ha='right')

# &&#&**&%* adjust height still
ax3.text(-0.05, 1.075, 'c.', transform=ax3.transAxes, fontsize=13, fontweight='bold', va='top', ha='right')
fig.subplots_adjust(hspace=0)

# add latex for scan rate

#ax1.text(0.6, 0.75, r'Scan rate, $v$ = $\frac{dE}{dt}$', transform=ax1.transAxes, fontsize=9)
ax1.text(0.65, 0.75, r'Scan rate, $v$ =', transform=ax1.transAxes, fontsize=9)
ax1.text(0.925, 0.75, r'$\frac{dE}{dt}$', transform=ax1.transAxes, fontsize=12)

#plt.savefig(save_loc + 'fig_1.pdf', dpi = 300, bbox_inches = 'tight')
plt.show()

"""



"""
######################################################################################
# fig 2
fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(double_width, double_width*0.8))
ax = ax.flat

# a) reversible 1e, vary concentration
# colors = []
c_map1 = plt.cm.Greens([0.3, 0.5, 0.9])
cols1 = [c_map1[0], 'k', c_map1[1], c_map1[2]]
concs = [10, 5, 2, 1]
space = ['', '  ', '  ', '  ']
for idx,c in enumerate(concs):
    v, i = E_rev(-0.3, 0.3, 0.0, 0.1, c, 1e-6, 1e-6).simulate()
    ax[0].plot(v, [y*1e6 for y in i], color=cols1[idx], label="C = " + str(space[idx]) + str(c) + ' mM')

# b) reversible 1e, vary D
# colors = []
diff_coef = [5e-5, 1e-5, 5e-6, 1e-6]
d1 = [5, 1, 5, 1]
d2 = [-5, -5, -6, -6]

c_map2 = plt.cm.Oranges([0.4, 0.6, 0.8])
cols2 = [c_map2[0], c_map2[1], c_map2[2], 'k']
for idx,d in enumerate(diff_coef):
    v, i = E_rev(-0.3, 0.3, 0.0, 0.1, 5, d, d).simulate()
    #ax[1].plot(v, [y*1e6 for y in i], label=f"D = {d:.0e} $\mathrm{{cm^{{2}}s^{{-1}}}}$")
    ax[1].plot(v, [y * 1e6 for y in i], color=cols2[idx], label=f"D = {d1[idx]}x$10^{{{d2[idx]}}}$ $\mathrm{{cm^{{2}}s^{{-1}}}}$")

# c) rev and then quasi rev
k_nots = [1e-3, 5e-4, 1e-4]
f1 = [1, 5, 1]
f2 = [-3, -4, -4]
v, i = E_rev(-0.3, 0.3, 0.0, 0.1, 5, 1e-6, 1e-6).simulate()
ax[2].plot(v, [y*1e6 for y in i], color='k', label='Reversible')

c_map3 = plt.cm.RdPu([0.4, 0.6, 0.8])
cols3 = [c_map3[0], c_map3[1], c_map3[2]]
for idx,k in enumerate(k_nots):
    v, i = E_q(-0.3, 0.3, 0.0, 0.1, 5, 1e-6, 1e-6, 0.5, k).simulate()
    #k_num = np.format_float_scientific(k, precision=0, exp_digits=1)
    #new_num =
    ax[2].plot(v, [y * 1e6 for y in i], color=cols3[idx], label=f"$\mathrm{{k^{{o'}}}}$ = {f1[idx]}x$10^{{{f2[idx]}}}$ cm $\mathrm{{s^{{-1}}}}$")
    #ax[2].plot(v, [y*1e6 for y in i], label=f"$\mathrm{{k^{{o'}}}}$ = {k:.0e} cm $\mathrm{{s^{{-1}}}}$")


# d) 2e with various separations between EE
delta_e = [5, 25, 50, 150]
space = ['    ', '  ', '  ', '']

c_map4 = plt.cm.Purples([0.3, 0.5, 0.7, 0.9])
cols4 = [c_map4[0], c_map4[1], c_map4[2], c_map4[3]]
for idx,ee in enumerate(delta_e):
    sep = 0.0 + (ee / 1000)
    v, i = EE(-0.3, 0.3, 0.0, sep,0.1, 5, 1e-6, 1e-6, 1e-6, 0.5, 0.5, 1e6, 1e6).simulate()
    ax[3].plot(v, [y*1e6 for y in i], color=cols4[idx], label=f"$\Delta$$E_{{1,2}}$ ={space[idx]} {ee} mV")


# add arrows and text
#ax[0].arrow(-0.2, 10, 0, 30, head_width=0.01, head_length=1)
ylocs1 = [10, 40, 5]#, 10]
ylocs2 = [50, 175, 25]#, 58]
labs = ["C", "D", f"$\mathrm{{k^{{o'}}}}$"]#, f"$\Delta$$E_{{1,2}}$"]
for idx,(y1,y2,l) in enumerate(zip(ylocs1, ylocs2, labs)):
    arr = mpatches.FancyArrowPatch((-0.1, y1), (-0.1, y2), arrowstyle='->,head_width=.15', mutation_scale=20)
    ax[idx].add_patch(arr)
    ax[idx].annotate("Increasing\n" + "      " + l, (-8.8, .2), xycoords=arr, ha='left', va='bottom')


# ax labels
for a in ax:
    a.set_xlabel("Potential (V vs reference)")
    a.set_ylabel("Current (uA)")
    a.set_xlim(-0.3, 0.3)
    a.legend(frameon=False, handletextpad=0.6, handlelength=1, fontsize=7)

fig.tight_layout()
#add figure labels
ax[0].text(-0.1, 1.15, 'a.', transform=ax[0].transAxes, fontsize=13, fontweight='bold', va='top', ha='right')
ax[1].text(-0.1, 1.15, 'b.', transform=ax[1].transAxes, fontsize=13, fontweight='bold', va='top', ha='right')
ax[2].text(-0.1, 1.15, 'c.', transform=ax[2].transAxes, fontsize=13, fontweight='bold', va='top', ha='right')
ax[3].text(-0.1, 1.15, 'd.', transform=ax[3].transAxes, fontsize=13, fontweight='bold', va='top', ha='right')
#plt.savefig(save_loc + 'fig_2x.pdf', dpi = 300, bbox_inches = 'tight')
plt.show()

"""

#############################################################
"""
# fig 3
# 3 subpanels horizontal, a) Erev and vary scan rate (randles sevcik)
# b) quasi rev, vary scan rate
# c) randles sevcik slopes

fig, ax = plt.subplots(nrows=1, ncols=3, sharey=True, figsize=(double_width, double_width*0.4))

scan_rates = [900, 400, 100, 25]  # mV
sqr_rates = [30, 20, 10, 5]
c_map_3 = plt.cm.cool([0.3, 0.5, 0.7, 0.9])
cols_3 = [c_map_3[0], c_map_3[1], c_map_3[2], c_map_3[3]]
spaces = ["", "", "", "  "]

max_i1 = []
max_i2 = []
min_i1 = []
min_i2 = []
k_not = 1e-4
for idx,rate in enumerate(scan_rates):
    r = rate/1000
    # E rev
    v, i = E_rev(-0.35, 0.35, 0.0, r, 5, 1e-6, 1e-6).simulate()
    curr1 = [y * 1e6 for y in i]
    max_i1.append(np.max(curr1))
    min_i1.append(np.min(curr1))
    ax[0].plot(v, curr1, color=cols_3[idx], label=f"v = {spaces[idx]}{rate} $\mathrm{{mV~s^{{-1}}}}$")

    # E quasirev
    v2, i2 = E_q(-0.35, 0.35, 0.0, r, 5, 1e-6, 1e-6, 0.5, k_not).simulate()
    curr2 = [y * 1e6 for y in i2]
    max_i2.append(np.max(curr2))
    min_i2.append(np.min(curr2))
    ax[1].plot(v2, curr2, "--", color=cols_3[idx], label=f"$v$ = {spaces[idx]}{rate} $\mathrm{{mV~s^{{-1}}}}$")

# r-sev constant @ 298 K, area (cm2), conc, D
r_sev_const = 269135*(7.06858/100)*5*((1e-6)**0.5)

# randles sevcick
fill = ["full", "full", "none", "none"]
for j,i in enumerate([max_i1, min_i1, max_i2, min_i2]):
    for idx,(x,y) in enumerate(zip(sqr_rates, i)):
        ax[2].plot(x, y, "o", color=cols_3[idx], fillstyle=fill[j])
# plot randles-sevcik line for reversible
line_val = [r_sev_const*((v/1000)**0.5) for v in scan_rates]
ax[2].plot(sqr_rates, line_val, 'k:', zorder=1, alpha=0.5)

# ax labels
ax[0].set_xlabel("Potential (V vs reference)")
ax[0].set_ylabel("Current (uA)")
ax[0].set_xlim(-0.35, 0.35)
#ax[0].set_xlim(-0.3, 0.3)
ax[1].legend(frameon=False, handletextpad=0.6, handlelength=1, fontsize=7)


ax[1].set_xlabel("Potential (V vs reference)")
ax[1].set_xlim(-0.35, 0.35)
ax[2].set_xlabel("$\mathrm{v^{1/2}~(mV~s^{-1})^{1/2}}$")
ax[2].set_ylabel("Peak Current (uA)")

#add figure labels
ax[0].text(-0.1, 1.15, 'a.', transform=ax[0].transAxes, fontsize=13, fontweight='bold', va='top', ha='right')
ax[1].text(-0.05, 1.15, 'b.', transform=ax[1].transAxes, fontsize=13, fontweight='bold', va='top', ha='right')
ax[2].text(-0.05, 1.15, 'c.', transform=ax[2].transAxes, fontsize=13, fontweight='bold', va='top', ha='right')
#plt.savefig(save_loc + 'fig_3.pdf', dpi = 300, bbox_inches = 'tight')
plt.show()
"""
###############################################


# fig 4 (email from TYG to EMF July 29, 2024 with CV data)
# 2 subplots stacked, (acid plot, base plot) like in rfb papers with two MC CVs on single plot.
# # arrow dashed line from each reduction potential showing OCV of cell "open circuit voltage" MUST SPELL IT OUT

# all run at 25 mV/s, 1 mM, disk radius is 1.5 mm

files = ["alizarinreds-corrected.txt", "hq-corrected.txt", "dhaq-corrected.txt", "k4fecn6-corrected.txt"]
SHE_correct = 0.222  # V
disk = 1.5  # mm
scan = 0.025  # V/s
bulk = 1.0  # mM
step = 1  # mV
temp = 298  # K


def data_gen(filepath):
    data = np.genfromtxt(fname=filepath, skip_header=2)
    volt_data = data[:, 0]
    current_data = data[:, 1]
    return volt_data, current_data


"""
# DHAQ simulate
delta_e = 0.065
v_start = -0.620 #+ SHE_correct
v_rev = -1.221 #+ SHE_correct
# really will sim this
#v2, i2 = EE(v_start, v_rev, -0.9, -0.9 - delta_e, 0.025, 1, 1e-6, 1e-6, 1e-6, 0.5, 0.5, 1e6, 1e6, disk_radius=disk).simulate()


#v2, i2 = E_q(-0.5, 0.5, 0.0, scan_rate, bulk_conc, 1e-6, 1e-6, 0.5, 1e-5, disk_radius=disk).simulate()
#ax[2].plot([i + SHE_correct for i in v2], [y*1e6 for y in i2], "--")
"""


##################################################################################


# Figure 4

# all run at 25 mV/s, 1 mM, disk radius is 3 mm

fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(double_width, double_width*0.8))

# for picture of rfb
ax[0].axis('off')

snip_vals = [30, 20, 40, 30]

#test_k = [5e-4, 1.05e-4, 3e-4, 8e-4]

#for idx, (f, snips, k_guess) in enumerate(zip(files, snip_vals, test_k)):
for idx, (f, snips) in enumerate(zip(files, snip_vals)):
    print(f"file: {f}")
    v, i = data_gen(cv_data_loc + f)

    # if idx < 3:
    #
    #     fitted_voltage, fitted_current = FitEE(
    #         v[snips:-1*snips],
    #         i[snips:-1*snips],
    #         scan_rate=scan,
    #         c_bulk=bulk,
    #         step_size=step,
    #         disk_radius=disk,
    #         temperature=temp,
    #     ).fit(
    #         diffusion_reactant=(1e-6, 9e-7, 5e-6),
    #         diffusion_intermediate=(1e-6, 9e-7, 5e-6),
    #         diffusion_product=(1e-6, 9e-7, 5e-6),
    #         alpha=(0.5, 0.4, 0.6),
    #         second_alpha=(0.5, 0.4, 0.6),
    #         k_0=(k_guess, 1e-4, 1e-3),
    #         second_k_0=(k_guess, 1e-4, 1e-3),
    #     )
    # else:  # ferriferro
    #     fitted_voltage, fitted_current = FitE_q(
    #         v[snips:-1*snips],
    #         i[snips:-1*snips],
    #         scan_rate=scan,
    #         c_bulk=bulk,
    #         step_size=step,
    #         disk_radius=disk,
    #         temperature=temp,
    #     ).fit(
    #         diffusion_reactant=(5e-6, 1e-6, 9e-6),
    #         diffusion_product=(5e-6, 1e-6, 9e-6),
    #         alpha=(0.5, 0.4, 0.6),
    #         k_0=(k_guess, 5e-4, 1e-3),
    #     )


    if idx == 0:  # alizarin
        fitted_voltage, fitted_current = EE(v[31], min(v), -0.198, -0.203, scan, bulk, 3e-6, 3e-6, 3e-6, 0.4, 0.4, 1e-2, 1e-2, disk_radius=disk).simulate()
        colcol = "b"
        redpot = -0.2
    elif idx == 1:  # HQ
        fitted_voltage, fitted_current = EE(v[22], max(v), 0.4, 0.415, scan, bulk, 20e-6, 5e-6, 5e-6, 0.8, 0.45, 4e-4, 4e-4, disk_radius=disk).simulate()
        colcol = "r"
        redpot = 0.408
    elif idx == 2:  # DHAQ
        fitted_voltage, fitted_current = EE(v[41], min(v), -0.899, -0.959, scan, bulk, 4.6e-6, 6.0e-6, 6.5e-6, 0.3, 0.5, 6e-3, 7e-3, disk_radius=disk).simulate()
        colcol = "b"
        redpot = -0.929
    elif idx == 3:  # ferriferro
        fitted_voltage, fitted_current = E_q(v[31], max(v), 0.27, scan, bulk, 5.5e-6, 6.5e-6, 0.4, 3.6e-3, disk_radius=disk).simulate()
        colcol = "r"
        redpot = 0.27

    if idx < 2:
        ax[1].plot(v[snips:-1*snips] + SHE_correct, i[snips:-1*snips]*1e6, color=colcol, alpha=0.5)
        ax[1].plot([x + SHE_correct for x in fitted_voltage], [x * 1e6 for x in fitted_current], 'k--', label='Fit')

        ax[1].axvline(redpot+SHE_correct, color="k", linestyle=":", alpha=0.7)

    else:
        ax[2].plot(v[snips:-1*snips] + SHE_correct, i[snips:-1*snips] * 1e6, color=colcol, alpha=0.5)
        ax[2].plot([x + SHE_correct for x in fitted_voltage], [x * 1e6 for x in fitted_current],"k--") #color="mediumaquamarine", linestyle='--', label='Fit')

        ax[2].axvline(redpot + SHE_correct, color="k", linestyle=":", alpha=0.7)

p1 = mpatches.FancyArrowPatch((-0.2+SHE_correct, 15), (0.408+SHE_correct, 15), arrowstyle='<->', mutation_scale=10)
ax[1].add_patch(p1)
ax[1].annotate("OCV = 0.6 V", (0.2, 17))


p2 = mpatches.FancyArrowPatch((-0.929+SHE_correct, 15), (0.27+SHE_correct, 15), arrowstyle='<->', mutation_scale=10)

ax[2].add_patch(p2)
ax[2].annotate("OCV = 1.2 V", (-0.26, 17))
#
ax[1].set_xlabel("Potential (V vs SHE)")
ax[1].set_ylabel("Current (uA)")

ax[2].set_xlabel("Potential (V vs SHE)")
ax[2].set_ylabel("Current (uA)")

ax[1].text(0.93, 16, '1M $\mathrm{H_2SO_4}$')
ax[2].text(0.53, 16, '1M KOH')
fig.tight_layout()


ax[1].set_xlim(-0.6, 1.2) # spans 1.8 volts
ax[2].set_xlim(-1.05, 0.75) # spans 1.8 volts

ax[1].set_ylim(-15, 26)
ax[2].set_ylim(-15, 26)

ax[1].set_yticks([-10, 0, 10, 20])
ax[2].set_yticks([-10, 0, 10, 20])

fig.tight_layout()
#add figure labels
ax[0].text(-0.05, 1.15, 'a.', transform=ax[0].transAxes, fontsize=13, fontweight='bold', va='top', ha='right')
ax[1].text(-0.05, 1.15, 'b.', transform=ax[1].transAxes, fontsize=13, fontweight='bold', va='top', ha='right')
ax[2].text(-0.05, 1.15, 'c.', transform=ax[2].transAxes, fontsize=13, fontweight='bold', va='top', ha='right')

#plt.savefig(save_loc + 'fig_4.pdf', dpi = 300, bbox_inches = 'tight')
plt.show()


### TEST ALIZARIN  **DONE**
"""
fig,ax = plt.subplots()
v, i = data_gen(cv_data_loc + "alizarinreds-corrected.txt")
v2, i2 = EE(v[31], min(v), -0.198, -0.203, scan, bulk, 3e-6, 3e-6, 3e-6, 0.4, 0.4, 1e-2, 1e-2, disk_radius=disk).simulate()  # good
# fitted_voltage, fitted_current = FitEE(
#             v[30:-30],
#             i[30:-30],
#             scan_rate=scan,
#             c_bulk=0.8,
#             step_size=step,
#             disk_radius=disk,
#             temperature=temp,
#     alpha=0.5,
#     second_alpha=0.5,
#         ).fit(
#             reduction_potential=(-0.25, -0.15),
#             second_reduction_potential=(-0.25, -0.15),
#             diffusion_reactant=(1e-6, 9e-7, 5e-6),
#             diffusion_intermediate=(1e-6, 9e-7, 5e-6),
#             diffusion_product=(1e-6, 9e-7, 5e-6),
#             #alpha=(0.5, 0.4, 0.6),
#             #second_alpha=(0.5, 0.4, 0.6),
#             k_0=(7e-3, 5e-3, 1e-2),
#             second_k_0=(7e-3, 5e-3, 1e-2),)

ax.plot(v[30:-30], i[30:-30]*1e6,)
#ax.plot([x for x in fitted_voltage], [x * 1e6 for x in fitted_current], '--')
ax.plot(v2, i2*1e6, "--")
plt.show()
"""

### TEST Hydroquinone  **DONE**
"""
fig,ax = plt.subplots()
v, i = data_gen(cv_data_loc + "hq-corrected.txt")

v2, i2 = EE(v[31], max(v), 0.4, 0.415, scan, bulk, 20e-6, 5e-6, 5e-6, 0.8, 0.45, 4e-4, 4e-4, disk_radius=disk).simulate()  # sure it's fine...
# fitted_voltage, fitted_current = FitEE(
#             v[30:-30],
#             i[30:-30],
#             scan_rate=scan,
#             c_bulk=bulk,
#             step_size=step,
#             disk_radius=disk,
#             temperature=temp,
# diffusion_reactant=6.4e-6,  # vals from TYG size/charge effects paper
#     #alpha=0.5,
#     #second_alpha=0.5,
#         ).fit(
#             reduction_potential=(0.34, 0.44),
#             second_reduction_potential=(0.34, 0.44),
#             #diffusion_reactant=(6.4e-6, 5e-6, 8e-6),
#             diffusion_intermediate=(6.4e-6, 5e-6, 8e-6),
#             diffusion_product=(6.4e-6, 5e-6, 8e-6),
#             alpha=(0.5, 0.4, 0.6),
#             second_alpha=(0.5, 0.4, 0.6),
#             k_0=(6e-4, 1e-4, 8e-4),
#             second_k_0=(6e-4, 1e-4, 8e-4),)
#
ax.plot(v[30:-30], i[30:-30]*1e6,)
#ax.plot([x for x in fitted_voltage], [x * 1e6 for x in fitted_current], '--')
ax.plot(v2, i2*1e6, "--")
plt.show()
"""

### TEST DHAQ **DONE**
"""
fig,ax = plt.subplots()
v, i = data_gen(cv_data_loc + "dhaq-corrected.txt")
delta = 0.06
e1 = -0.899
e2 = e1 - delta
v2, i2 = EE(v[21], min(v), e1, e2, scan, bulk, 4.6e-6, 6.0e-6, 6.5e-6, 0.3, 0.5, 6e-3, 7e-3, disk_radius=disk).simulate() # its ok

fitted_voltage, fitted_current = FitEE(
            v[30:-30],
            i[30:-30],
            scan_rate=scan,
            c_bulk=bulk,
            step_size=step,
            disk_radius=disk,
            temperature=temp,
        ).fit(
            reduction_potential=(-0.899, -0.91, -0.89),
            second_reduction_potential=(-0.959, -0.975, -0.945),
            diffusion_reactant=(4.8e-6, 4e-6, 6e-6),
            diffusion_intermediate=(5e-6, 4e-6, 6e-6),
            diffusion_product=(5e-6, 4e-6, 6e-6),
            alpha=(0.5, 0.45, 0.55),
            second_alpha=(0.5, 0.45, 0.55),
            k_0=(7e-3, 3e-3, 8e-3),
            second_k_0=(7e-3, 3e-3, 8e-3),)


ax.plot(v[30:-30], i[30:-30]*1e6, 'k')
ax.plot([x for x in fitted_voltage], [x * 1e6 for x in fitted_current], 'b--')
ax.plot(v2, i2*1e6, "r--")
plt.show()
"""


"""
### TEST FerriFerro  **DONE
fig,ax = plt.subplots()
v, i = data_gen(cv_data_loc + "k4fecn6-corrected.txt")
#ff=0.02
v2, i2 = E_q(v[21], max(v), 0.27, scan, bulk, 5.5e-6, 6.5e-6, 0.4, 3.6e-3, disk_radius=disk).simulate()  # GOOD TO GO

fitted_voltage, fitted_current = FitE_q(
            v[30:-30],
            i[30:-30],
            scan_rate=scan,
            c_bulk=bulk,
            step_size=step,
            disk_radius=disk,
            temperature=temp,
        ).fit(
            reduction_potential=(0.27, 0.25, 0.3),
            diffusion_reactant=(5e-6, 4e-6, 6e-6),
            diffusion_product=(5e-6, 4e-6, 6e-6),
            alpha=(0.5, 0.45, 0.55),
            k_0=(5e-3, 9e-4, 8e-3),)

ax.plot(v[30:-30], i[30:-30]*1e6, 'k')
ax.plot([x for x in fitted_voltage], [x * 1e6 for x in fitted_current], 'b--')
ax.plot(v2, i2*1e6, "r--")
plt.show()
"""

#