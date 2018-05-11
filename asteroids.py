#!/usr/bin/env python
# coding: utf-8
''' asteroids.py
'''

import argparse
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def parse_inputs():
    '''Parse inputs, absolute or optinal'''
    parser = argparse.ArgumentParser()
    parser.add_argument('scan', nargs='?', type=int, default="-1",
                        help="Scan number")
    parser.add_argument("-s", "--scan",
                        help="Scan number")
    args = parser.parse_args()
    return (args.scan)


def main(args=None):
    print('Nothing in main() yet...')
    return


def read_horizons_file(filename):
    endcol = np.array([0, 19, 37, 40, 51, 61, 70, 80, 94, 101, 117, 129, 146,
                       158, 167, 170, 179, 190, 200, 211, 221, 230, 238, 247,
                       255, 263, 271, 279, 287])
    inhead = (' date JD SM  RA DEC dRA*cosD d(DEC)/dt L_Ap_Sid_Time a-mass r '
              'rdot delta deldot S-O-T /r S-T-O GAL_LON GAL_LAT ECL_LON '
              'ECL_LAT CONF100um CONF160um fd200 fd350 fd450 fd850 fd1300 '
              'fd3000').split()
    df = pd.read_fwf(filename, skiprows=73, skipfooter=113, header=None,
                     widths=np.diff(endcol), skipinitialspace=True,
                     names=inhead, parse_dates=[0])
    df['source'] = filename.split('/')[-1].split('.')[0]
    return df


if __name__ == "__main__":
    main()

    year = 2018
    no_bright = 8
    plt.close('all')
    datafiles = glob('data/*.res')
    df = read_horizons_file(datafiles[0])
    for file in datafiles[1:]:
        df = pd.concat([df, read_horizons_file(file)], axis=0)

    dfm = df[['date', 'source', 'fd350', 'fd450',
              'fd850', 'SM', 'RA', 'DEC']]
    dfm.set_index('date', inplace=True)
    dfm = pd.DataFrame(dfm[str(year)])
    bright = dfm.groupby('source').fd350.max().sort_values(
        ascending=False).index[:no_bright]
    dfm = dfm[dfm.source.isin(bright)]

    # fig, axes = plt.subplots(nrows=3, sharex=True)
    # for label, dfs in dfm.groupby('source'):
    #     print(label)
    #     dfs.fd350.plot(ax=axes[0], label=label)
    #     dfs.fd450.plot(ax=axes[1], label=label)
    #     dfs.fd850.plot(ax=axes[2], label=label)
    # axes[0].legend(loc='upper left', bbox_to_anchor=(1, 1))
    # axes[0].set_ylabel(r'Flux 350$\,\mu$m [Jy]')
    # axes[1].set_ylabel(r'Flux 450$\,\mu$m [Jy]')
    # axes[2].set_ylabel(r'Flux 850$\,\mu$m [Jy]')
    # plt.xlabel('')
    # plt.tight_layout()
    # # plt.show()

    fig, ax = plt.subplots(1)
    # for label, dfs in dfm.groupby('source'):
    #     print(label)
    #     dfs.fd350.plot(ax=ax, label=label)
    for source in bright:
        print(source)
        dfm[dfm.source == source].fd350.plot(ax=ax, label=source)

    plt.title('{:d} brightest asteroids {:d}'.format(no_bright, year))
    ax.set_ylabel(r'$S(350\mu}$m) [Jy]')
    plt.xlabel('')
    fig.autofmt_xdate()
    plt.minorticks_off()
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), frameon=False)
    fd450_ratio = (dfm.groupby('source').fd450.sum() /
                   dfm.groupby('source').fd350.sum()).mean()
    fd850_ratio = (dfm.groupby('source').fd850.sum() /
                   dfm.groupby('source').fd350.sum()).mean()
    fig.text(0.95, 0.25, r'$S\,\frac{450}{350}\,\mu$m = ' +
             '{:.2f}'.format(fd450_ratio),
             ha='right')
    fig.text(0.95, 0.18, r'$S\,\frac{850}{350}\,\mu$m = ' +
             '{:.2f}'.format(fd850_ratio),
             ha='right')
    plt.tight_layout()
    plt.show()
    plot_file = 'plots/asteroids_' + str(year) + '.png'
    plt.savefig(plot_file, bbox_inches="tight", dpi=150)
