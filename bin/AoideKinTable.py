#!/usr/bin/env python

import os
import time

from astropy.io import fits
import numpy as np

import argparse

def main():

    args = parse_args()

    stellar_table = args.stellar_table
    voronoi_pixtabl = args.voronoi_pixtab
    prefix = stellar_table.split(".")[0]

    hdu = fits.open(stellar_table)
    tab = hdu[1].data
    fiber = tab.field('fiber')
    vel_fit = tab.field('vel_fit')
    vel_fit_err = tab.field('vel_fit_err')
    disp_fit = tab.field('disp_fit')
    disp_fit_err = tab.field('disp_fit_err')

    input_pixel_file = args.voronoi_pixtab
    output_kin_table = '{}.kin_table.fits'.format(prefix)

    print("Creating stellar kinematics table from _stellar_table.fits")
    create_kin_tab(input_pixel_file, output_kin_table, fiber, vel_fit, vel_fit_err, disp_fit, disp_fit_err)
    print("Done.")
    print("Your product is {}".format(output_kin_table))
    print("Use this as the fixed stellar component for your Emission Line Fitting.")


def create_kin_tab(voronoi_pixel,out_table,fiber,vel_fit,vel_fit_err,disp_fit,disp_fit_err):

  ascii_in = open(voronoi_pixel,'r')
  lines = ascii_in.readlines()
  x = np.arange(len(lines)-1,dtype=np.int16)
  y = np.arange(len(lines)-1,dtype=np.int16)
  binNr = np.arange(len(lines)-1,dtype=np.int16)
  for i in range(1,len(lines)):
    line = lines[i].split()
    x[i-1]=int(line[0])
    y[i-1]=int(line[1])
    binNr[i-1]=int(line[2])
  x_cor = x
  y_cor = y
  vel_out = np.zeros(len(x),dtype=np.float32)
  vel_err_out = np.zeros(len(x),dtype=np.float32)
  disp_out = np.zeros(len(x),dtype=np.float32)
  disp_err_out = np.zeros(len(x),dtype=np.float32)
  for i in range(max(fiber)): # THIS USED TO SAY range(max(fiber))
     select = fiber[i]+1 == binNr
     vel_out[select] = vel_fit[i]
     vel_err_out[select] = vel_fit_err[i]
     disp_out[select] = disp_fit[i]
     disp_err_out[select] = disp_fit_err[i]

  columns = []
  columns.append(fits.Column(name='x_cor',format='J', array=x_cor))
  columns.append(fits.Column(name='y_cor',format='J', array=y_cor))
  columns.append(fits.Column(name='vel_fit',format='E', array=vel_out))
  columns.append(fits.Column(name='vel_fit_err',format='E', array=vel_err_out))
  columns.append(fits.Column(name='disp_fit',format='E', array=disp_out))
  columns.append(fits.Column(name='disp_fit_err',format='E', array=disp_err_out))

  new_table = fits.TableHDU.from_columns(columns)
  new_table.writeto(out_table, overwrite=True)


def parse_args():

    parser = argparse.ArgumentParser(
        description="PCA sky subtraction, galactic extinction correction, and preparation for MUSE cubes that are to be analyzed with Paradise")


    parser.add_argument('stellar_table', metavar='stellar_table', type=str, nargs='?',
                        help='Name of galaxy (used for Prefix).')



    parser.add_argument('voronoi_pixtab', metavar='voronoi_table', type=str, nargs='?',
                        help='Name of Vornonoi Pixel Table.')

    args = parser.parse_args()

    return args


if __name__ == '__main__':

    start_time = time.time()
    main()
    runtime = round((time.time() - start_time), 3)
    print("\n=================    Aoide | Stellar Kin Table Created   ================\n")
    print("Finished in {} minutes.".format(round(runtime / 60, 3)))
    print("Use this as a partial input to your Emission Line Fitting.")
