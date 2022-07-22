# -*- coding: utf-8 -*-
"""
Cells
=====

Expert cell image processing pipeline.

This module provides the basic routines for processing immmediate eaerely
gene data. 

The routines are used in the :mod:`ClearMap.Scripts.CellMap` pipeline.
"""
import ClearMap.Utils.HierarchicalDict as hdict
import ClearMap.Utils.Timer as tmr
import ClearMap.Analysis.Measurements.MeasureExpression as me
import ClearMap.Analysis.Measurements.ShapeDetection as sd
import ClearMap.Analysis.Measurements.MaximaDetection as md
import ClearMap.ImageProcessing.LocalStatistics as ls
import ClearMap.ImageProcessing.Filter.FilterKernel as fk
import ClearMap.ImageProcessing.Filter.StructureElement as se
import ClearMap.ImageProcessing.IlluminationCorrection as ic
import ClearMap.ParallelProcessing.DataProcessing.ArrayProcessing as ap
import ClearMap.ParallelProcessing.BlockProcessing as bp
import ClearMap.IO.IO as io
import skimage.filters as skif
import scipy.ndimage.filters as ndf
import scipy.ndimage as ndi
import cv2
import numpy as np
__author__ = 'Christoph Kirst <christoph.kirst.ck@gmail.com>'
__license__ = 'GPLv3 - GNU General Pulic License v3 (see LICENSE.txt)'
__copyright__ = 'Copyright © 2020 by Christoph Kirst'
__webpage__ = 'http://idisco.info'
__download__ = 'http://www.github.com/ChristophKirst/ClearMap2'


import tempfile as tmpf
import gc
import os
from statistics import mean, stdev


#import ClearMap.ImageProcessing.Filter.Rank as rnk

#import ClearMap.ImageProcessing.LightsheetCorrection as lc
#import ClearMap.ImageProcessing.Differentiation.Hessian as hes
#import ClearMap.ImageProcessing.Binary.Filling as bf
#import ClearMap.ImageProcessing.Binary.Smoothing as bs


###############################################################################
# Default parameter
###############################################################################

default_cell_detection_parameter = dict(
    # flatfield
    iullumination_correction=dict(flatfield=None,
                                  scaling='mean'),

    # background removal
    background_correction=dict(shape=(10, 10),
                               form='Disk',
                               save=False),

    # equalization
    equalization=None,

    # difference of gaussians filter
    dog_filter=dict(shape=None,
                    sigma=None,
                    sigma2=None),

    # extended maxima detection
    maxima_detection=dict(h_max=None,
                          shape=5,
                          threshold=0,
                          valid=True,
                          save=False),

    # cell shape detection
    shape_detection=dict(threshold=700,
                         save=False),

    # cell intenisty detection
    intensity_detection=dict(method='max',
                             shape=3,
                             measure=['source', 'background']),
)
"""Parameter for the cell detectrion pipeline. 
See :func:`detect_cells` for details."""


default_cell_detection_processing_parameter = dict(
    size_max=100,
    size_min=50,
    overlap=32,
    axes=[2],
    optimization=True,
    optimization_fix='all',
    verbose=None,
    processes=None
)
"""Parallel processing parameter for the cell detection pipeline. 
See :func:`ClearMap.ParallelProcessing.BlockProcessing.process` for details."""


###############################################################################
# Cell detection
###############################################################################

def detect_cells(source, sink=None, cell_detection_parameter=default_cell_detection_parameter, processing_parameter=default_cell_detection_processing_parameter, array_of_means = []):
    """Cell detection pipeline.
    
    Arguments
    ---------
    source : source specification
      The source of the stitched raw data.
    sink : sink specification or None
      The sink to write the result to. If None, an array is returned.
    cell_detection_parameter : dict
      Parameter for the binarization. See below for details.
    processing_parameter : dict
      Parameter for the parallel processing. 
      See :func:`ClearMap.ParallelProcessing.BlockProcesing.process` for 
      description of all the parameter.
    verbose : bool
      If True, print progress output.

    Returns
    -------
    sink : Source
      The result of the cell detection.

    Notes
    -----
    Effectively this function performs the following steps:
      * illumination correction via :func:`~ClearMap.ImageProcessing.IlluminationCorrection.correct_illumination`
      * background removal
      * difference of Gaussians (DoG) filter
      * maxima detection via :func:`~ClearMap.Analysis.Measurements.MaximaDetection.find_extended_maxima`
      * cell shape detection via :func:`~ClearMap.Analysis.Measurements.ShapeDetection.detect_shape`
      * cell intensity and size measurements via: :func:`~ClearMap.ImageProcessing.Measurements.ShapeDetection.find_intensity`,
        :func:`~ClearMap.ImageProcessing.Measurements.ShapeDetection.find_size`. 


    The parameters for each step are passed as sub-dictionaries to the 
      cell_detection_parameter dictionary.

    * If None is passed for one of the steps this step is skipped.

    * Each step also has an additional parameter 'save' that enables saving of 
      the result of that step to a file to inspect the pipeline.


    Illumination correction
    -----------------------
    illumination_correction : dict or None
      Illumination correction step parameter.

      flatfield : array or str 
        The flat field estimate for the image planes.

      background : array or None
        A background level to assume for the flatfield correction.

      scaling : float, 'max', 'mean' or None
        Optional scaling after the flat field correction.

      save : str or None
        Save the result of this step to the specified file if not None.

    See also :func:`ClearMap.ImageProcessing.IlluminationCorrection.correct_illumination`


    Background removal
    ------------------
    background_correction : dict or None
      Background removal step parameter.

      shape : tuple
        The shape of the structure lement to estimate the background.
        This should be larger than the typical cell size.

      form : str
        The form of the structur element (e.g. 'Disk')

      save : str or None
        Save the result of this step to the specified file if not None.

    Equalization
    ------------
    equalization : dict or None
      Equalization step parameter.
      See also :func:`ClearMap.ImageProcessing.LocalStatistics.local_percentile`

      precentile : tuple
        The lower and upper percentiles used to estimate the equalization.
        The lower percentile is used for normalization, the upper to limit the
        maximal boost to a maximal intensity above this percentile.

      max_value : float
        The maximal intensity value in the equalized image.

      selem : tuple
        The structural element size to estimate the percentiles. 
        Should be larger than the larger vessels.

      spacing : tuple
        The spacing used to move the structural elements.
        Larger spacings speed up processing but become locally less precise.

      interpolate : int
        The order of the interpoltation used in constructing the full 
        background estimate in case a non-trivial spacing is used.

      save : str or None
        Save the result of this step to the specified file if not None.


    DoG Filter
    ----------
    dog_filter : dict or None
      Difference of Gaussian filter step parameter.

      shape : tuple
        The shape of the filter.
        This should be near the typical cell size.

      sigma : tuple or None
         The std of the inner Gaussian.
         If None, detemined automatically from shape.

      sigma2 : tuple or None
         The std of the outer Gaussian.
         If None, detemined automatically from shape.

      save : str or None
        Save the result of this step to the specified file if not None.


    Maxima detection
    ----------------
    maxima_detection : dict or None
      Extended maxima detection step parameter.

      h_max : float or None
        The 'height'for the extended maxima.
        If None, simple local maxima detection isused.

      shape : tuple
        The shape of the structural element for extended maxima detection.
        This should be near the typical cell size.

      threshold : float or None
        Only maxima above this threshold are detected. If None, all maxima
        are detected.

      valid : bool
        If True, only detect cell centers in the valid range of the blocks with
        overlap.

      save : str or None
        Save the result of this step to the specified file if not None.


    Shape detection
    ---------------
    shape_detection : dict or None
      Shape detection step parameter.

      threshold : float
        Cell shape is expanded from maxima if pixles are above this threshold
        and not closer to another maxima.

      save : str or None
        Save the result of this step to the specified file if not None.


    Intensity detection
    -------------------
    intensity_detection : dict or None
      Intensity detection step parameter.

      method : {'max'|'min','mean'|'sum'}
        The method to use to measure the intensity of a cell.

      shape : tuple or None
        If no cell shapes are detected a disk of this shape is used to measure
        the cell intensity.

      save : str or None
        Save the result of this step to the specified file if not None.

    References
    ----------
    [1] Renier, Adams, Kirst, Wu et al., "Mapping of Brain Activity by Automated Volume Analysis of Immediate Early Genes.", Cell 165, 1789 (2016)
    [1] Kirst et al., "Mapping the Fine-Scale Organization and Plasticity of the Brain Vasculature", Cell 180, 780 (2020)
    """

    # initialize sink
    # io.shape() converts filename_string to Source class and returns size of dimensions of the array
    shape = io.shape(source)
    # io.order() converts filename_string to Source class and returns order dimensions of the array
    order = io.order(source)

    # Size and order of the sink have been defined

    '''
  Edited by Stefan P. 31.08.21:
  io comes from ClearMap.IO.IO which is connected to ClearMap.IO.Source
  Source class:
  The object of class source has the following parameters: 
      name -- name of the source
      shape -- shape of the source
      dtype -- data type of the source
      order -- contiguous order of the underlying data array
      location -- location where data of the source is stored (filepath?)
  '''

    for key in cell_detection_parameter.keys():
        # keys are iullumination_correction, background_correction etc.
        par = cell_detection_parameter[key]
        # checks whether cell_detection_parameter[key] is a dictionairy itself
        if isinstance(par, dict):
            # par.get() returns value of save or None if save not specified to organiye which array to save and which not
            filename = par.get('save', None)
            if filename:
                # Initialiyes a Source class object, that will be used as output for instances where save is True
                ap.initialize_sink(filename, shape=shape,
                                   order=order, dtype='float')
                # The sink structures above are only used for steps like illumination correction etc, the final sink has a different structure though
    cell_detection_parameter.update(verbose=processing_parameter.get(
        'verbose', False))  # Just to update verbose parameter

    # Below edited by Stefan P.
    mean_file = open("means.txt","w");
    mean_file.write("");
    mean_file.close();
    #Above edited by stefan P.
    
    
    '''
  Edited by Stefan P. 31.08.21:
  Seems to be the most relevant line for the process since detect_cells_block returns results array 
  Results are calculated in separated blocks and finally merged together
  bp.process() creates blocks of an object and processes these blocks with an as argument given input function. It then returns the output of the input function for all merged blocks.  
    '''

    results, blocks = bp.process(detect_cells_block, source, sink=None, function_type='block', return_result=True,
                                 return_blocks=True, parameter=cell_detection_parameter, **processing_parameter)
    
    # merge results
    results = np.vstack([np.hstack(r) for r in results])
    print("Results: ",results)
    mean_file = open("means.txt","r")
    content = mean_file.read()
    mean_array = content.splitlines()
    mean_file.close()



    print("\n")
    print("Cell_detection_paramter.keys(): ", cell_detection_parameter.keys())
    print("Cell_detection_parameter[threshold]: ", cell_detection_parameter['threshold'])
    mean_array = [float(i) for i in mean_array]
    print("Mean Values Array: ", mean_array)
    total_mean = mean(mean_array);
    if len(mean_array) > 1:
        std_total_mean = stdev(mean_array);
    else:
        std_total_mean = 0;
    print("Total mean: ", total_mean)
    print("Standar deviation: ", std_total_mean)
    mean_background_array = [i for i in mean_array if i < (total_mean-(0.5*std_total_mean))]
    print("Background mean values Array", mean_background_array)
    background_mean = mean(mean_background_array);
    print("Background mean: ", background_mean)
    print("\n")
    print("\n")
    #print("Results", results)
    print("\n")

    if len(results) > 0:
        results_tmp = np.ones(len(results),dtype = bool)

        if cell_detection_parameter['threshold'] == "total mean":
            for index,i in enumerate(results):
                #print("comparison: ", i[len(results[0])-1], ":", total_mean,"-->",i[len(results[0])-1] >= total_mean)
                bool_tmp = i[len(results[0])-1] >= total_mean
                results_tmp[index] = np.logical_and(results_tmp[index],bool_tmp)


    
        elif cell_detection_parameter['threshold'] == "background mean":
            for index,i in enumerate(results): 
                #print("comparison: ", i[len(results[0])-1], ":", background_mean,"-->",i[len(results[0])-1] >= background_mean)
                bool_tmp = i[len(results[0])-1] >= background_mean
                results_tmp[index] = np.logical_and(results_tmp[index],bool_tmp)
            
            


        print("Results temp: ", results_tmp)
        results = results[results_tmp];
        print("Results: ",results)
    

    

    '''
  Edited by Stefan P. 31.08.21:
  In this section a new datastructure is prepared to write the sink results into 
  an array that contains coordinates as integers in x,y,z size and intensity measurements. 
    '''
    # create column headers
    header = ['x', 'y', 'z']
    dtypes = [int, int, int]
    if cell_detection_parameter['shape_detection'] is not None:
        header += ['size']
        dtypes += [int]
    # next line was introduced for debugging reasons
    #print('Intensity_detection_measure',
    #     cell_detection_parameter['intensity_detection']['measure'])
    #print('Results: ', results[0, :], type(results))
    # last line introduced for debugging reasons
    measures = cell_detection_parameter['intensity_detection']['measure']
    header += measures
    dtypes += [float] * len(measures)

    '''
  Edited by Stefani P. 31.08.2021:
  The following lines are just conversion of the results object of dtype list
  to an object of datatype ClearMap.IO.MMP.Source.
  Simple modifications or additions here may help us to yield our own datastructure
  Although it is important to keep this structure to keep function of cell annotation
  '''
    dt = {'names': header, 'formats': dtypes}
    cells = np.zeros(len(results), dtype=dt)
    for i, h in enumerate(header):
        cells[h] = results[:, i]
        
    #cell_detection_parameter['array_of_means'] = [];
    if os.path.exists("means.txt"):
        os.remove("means.txt");

    # save results
    # In this case sink is the filename that has been used as input for the detect cells funtcion
    return io.write(sink, cells)


def detect_cells_block(source, parameter=default_cell_detection_parameter):
    """Detect cells in a Block."""

    # initialize parameter and slicings
    # checks if verbose has been set to True
    verbose = parameter.get('verbose', False)
    if verbose:  # If so the following block will give an output on the console about the number of blocks and runtime of the steps
        prefix = 'Block %s: ' % (source.info(),)
        total_time = tmr.Timer(prefix)

    # Still not really sure about the meaning of those variables, they seem to be boundaries though
    base_slicing = source.valid.base_slicing
    valid_slicing = source.valid.slicing
    valid_lower = source.valid.lower
    valid_upper = source.valid.upper
    lower = source.lower

    '''
  Edited by Stefan P. 01.09.21:
  Intensity detection takes place right away and during the whole process of cell detection
  Steps:
  1.Checks whether intensity detection should be performed
  2.Checks whether a measure parameter in the intensity_detection function has been set by the user.
  3.A measure_to_array is initialized that will be filled with all the measures during the processing steps of cell detection. Possible measures are source,illumination,background,equalized,dog
  '''
    parameter_intensity = parameter.get('intensity_detection', None)
    measure_to_array = dict()
    if parameter_intensity:
        parameter_intensity = parameter_intensity.copy()
        measure = parameter_intensity.pop('measure', [])
        if measure is None:
            measure = []
        for m in measure:
            measure_to_array[m] = None

    if 'source' in measure_to_array:  # Source values will be added to the measure_to_array
        measure_to_array['source'] = source

    # correct illumination
    '''
  Edited by Stefan P. 01.09.21:
  Illumination correction steps:
  1.Check whether ilumination correction should be performed.
    If so:
        2.Copy of the illumination parameters
        3.Execution of illumination corrction with a function from ClearMap.ImageProcessing.IlluminationCorrection
        4.corrected = illumiantion_correction
        4.save option -> If so: ilummination correction will be saved as Source object
        5.Check whether illumiantion results should be added to measure to array -> Later the data of this array will be added to the final results
    Else:
        2.corrected = Source (Source array will be passed under the new variable corrected)

    Check whether illumiantion results should be added to measure to array -> Later the data of this array will be added to the final results
  '''

    parameter_illumination = parameter.get('illumination_correction', None)
    if parameter_illumination:
        parameter_illumination = parameter_illumination.copy()
        if verbose:
            timer = tmr.Timer(prefix)
            hdict.pprint(parameter_illumination, head=prefix +
                         'Illumination correction')
        save = parameter_illumination.pop('save', None)

        corrected = ic.correct_illumination(source, **parameter_illumination)

        if save:
            save = io.as_source(save)
            save[base_slicing] = corrected[valid_slicing]

        if verbose:
            timer.print_elapsed_time('Illumination correction')
    else:
        corrected = np.array(source.array)

    if 'illumination' in measure_to_array:
        measure_to_array['illumination'] = corrected

    # background subtraction
    '''
  Edited by Stefan P. 01.09.21
  Background subtraction:
  1.Check whether background_correction should be performed
      If so:
        2.copy of background correction parameters 
        3.Execution of remove_background which is part of this script
        4.background = remove_background
        5. Save option -> if so:  as Source object
      Else:
        2.background = corrected
    Add background_correction data to measure_to_array if user inserts that 
  '''
    parameter_background = parameter.get('background_correction', None)
    if parameter_background:
        parameter_background = parameter_background.copy()
        if verbose:
            timer = tmr.Timer(prefix)
            hdict.pprint(parameter_background,
                         head=prefix + 'Background removal')
        save = parameter_background.pop('save', None)

        background = remove_background(corrected, **parameter_background)

        if save:
            save = io.as_source(save)
            save[base_slicing] = background[valid_slicing]

        if verbose:
            timer.print_elapsed_time('Illumination correction')
    else:
        background = corrected

    del corrected

    if 'background' in measure_to_array:
        measure_to_array['background'] = background

    # equalize
    '''
  Edited by Stefan P. 01.09.21
  Equalization:
  1.Check whether equalization should be performed
      If so:
        2.copy of equalization parameters 
        3.Execution of parameter_equalize which is part of this script
        4.equalized = parameter_equalize
        5.Save option -> if so:  as Source object
      Else:
        2.equalized = background
    Add background_correction data to measure_to_array if user inserts that 
  '''
    parameter_equalize = parameter.get('equalization', None)
    if parameter_equalize:
        parameter_equalize = parameter_equalize.copy()
        if verbose:
            timer = tmr.Timer(prefix)
            hdict.pprint(parameter_equalize, head=prefix + 'Equalization:')

        save = parameter_equalize.pop('save', None)

        equalized = equalize(background, mask=None, **parameter_equalize)
        #print("Equalized Array",equalized)
        if save:
            save = io.as_source(save)
            save[base_slicing] = equalized[valid_slicing]

        if verbose:
            timer.print_elapsed_time('Equalization')

    else:
        equalized = background

    del background

    if 'equalized' in measure_to_array:
        measure_to_array['equalized'] = equalized

    # DoG filter

    '''
  Edited by Stefan P. 01.09.21
  DoG filter:
  1.Check whether dog should be performed
      If so:
        2.copy of dog parameters 
        3.Execution of dog which is part of this script
        4.dog = dog_filter 
        5. Save option -> if so:  as Source object
      Else:
        2.dog = equalized
    Add dog data to measure_to_array if user inserts that 
  '''
    parameter_dog_filter = parameter.get('dog_filter', None)
    if parameter_dog_filter:
        parameter_dog_filter = parameter_dog_filter.copy()
        if verbose:
            timer = tmr.Timer(prefix)
            hdict.pprint(parameter_dog_filter, head=prefix + 'DoG filter:')

        save = parameter_dog_filter.pop('save', None)

        dog = dog_filter(equalized, **parameter_dog_filter)

        if save:
            save = io.as_source(save)
            save[base_slicing] = dog[valid_slicing]

        if verbose:
            timer.print_elapsed_time('DoG filter')

    else:
        dog = equalized

    '''
  Next block is edited by Stefan P on 02.09.21 in order to achieve an elimination of maxima 
  in the background. 
  '''
    #print('Type', type(dog))
    #print('Dog: \n', dog)
    print("Meand dog: ", dog.mean())
    #print("Keys: ", parameter.keys());
    #print("Array of means 1", parameter['array_of_means']);
    #parameter['array_of_means'].append(dog.mean());
    #print("Array of means 2", parameter['array_of_means']);
    mean_file = open("means.txt","a+");
    mean_file.write(str(dog.mean())+"\n");
    
    mean_file.close();
    '''
  Block above edited by Stefan P.
  '''

    del equalized

    if 'dog' in measure_to_array:
        measure_to_array['dog'] = dog

        '''
    Edited by Stefan P. 01.09.21:
    Total mean idea:
      Important is to recognize, that the dog array includes the information,that will be passed on to the maxima detection, we may could introduce a method, that calculates a mean from those
      arrays and stores them in a file. We could then calculate the mean of means after the process is performed and get rid of background issues.

    Background mean idea:
      When the total mean is calculated, we can choose all the mean values memorized in the meanfile having a value lower than the total mean, and calculate the mean of those background mean values 
    '''

    # Maxima detection
    '''
  Edited by Stefan P. 01.09.21:
    This is the most important part of the cell_detection process
    Maxima detection:
    1.Shape detection and intensity detection are only executable when maxima detection is present.
      Thus the first block checks whether shape_detection or intensity_detection is activated without maxima_dtection being activated
    2.Check whether maxima detection should be performed.
      if so:
            3. maxima = md.find_maxima(dog) Execution of maxima detection -> md comes from ClearMap.Analysis.Measurements.MaximaDetection
            4. Save option
            5. !!!Option for h_max that is not understood so far!!!
               A centers array becomes introduced here, that seems to define coordinates:
                The coordinates can result from two options:
                  centers = coord_maxima_after_h_max_correction
            centers = coord_maxima
            6. correct for valid region:
                Seems to be a mechanism to sort out invalid regions
                The centers array is used here:
                  1.ids array created, that contains ones and an array size of len(centers)
                  2.Loop checks for each entry in centers the following (ids (always 1) AND (lower_boundary <= center_value AND center_value < upper_boundary))
                  3. Only entries where the upper properties are true are kept in the centers array, that defines the maxima position
        
  '''
    parameter_maxima = parameter.get('maxima_detection', None)
    parameter_shape = parameter.get('shape_detection', None)

    if parameter_shape or parameter_intensity:
        if not parameter_maxima:
            print(
                prefix + 'Warning: maxima detection needed for shape and intensity detection!')
            parameter_maxima = dict()

    if parameter_maxima:
        parameter_maxima = parameter_maxima.copy()
        if verbose:
            timer = tmr.Timer(prefix)
            hdict.pprint(parameter_maxima, head=prefix + 'Maxima detection:')

        save = parameter_maxima.pop('save', None)
        valid = parameter_maxima.pop('valid', None)

        # extended maxima
        maxima = md.find_maxima(dog, **parameter_maxima, verbose=verbose)

        if save:
            save = io.as_source(save)
            save[base_slicing] = maxima[valid_slicing]

        # center of maxima
        if parameter_maxima['h_max']:
            centers = md.find_center_of_maxima(
                source, maxima=maxima, verbose=verbose)
        else:
            centers = ap.where(maxima).array

        if verbose:
            timer.print_elapsed_time('Maxima detection')

        # correct for valid region

        if valid:
            ids = np.ones(len(centers), dtype=bool)
            for c, l, u in zip(centers.T, valid_lower, valid_upper):
                ids = np.logical_and(ids, np.logical_and(l <= c, c < u))
            centers = centers[ids]
            del ids

    del maxima

    results = (centers,)

    # cell shape detection
    if parameter_shape:
        parameter_shape = parameter_shape.copy()
        if verbose:
            timer = tmr.Timer(prefix)
            hdict.pprint(parameter_shape, head=prefix + 'Shape detection:')

        save = parameter_shape.pop('save', None)

        # shape detection
        shape = sd.detect_shape(
            dog, centers, **parameter_shape, verbose=verbose)

        if save:
            save = io.as_source(save)
            save[base_slicing] = shape[valid_slicing]

        # size detection
        max_label = centers.shape[0]
        sizes = sd.find_size(shape, max_label=max_label)
        valid = sizes > 0

        if verbose:
            timer.print_elapsed_time('Shape detection')

        results += (sizes,)

    else:
        valid = None
        shape = None

    del dog

    # cell intensity detection
    if parameter_intensity:
        parameter_intensity = parameter_intensity.copy()
        if verbose:
            timer = tmr.Timer(prefix)
            hdict.pprint(parameter_intensity, head=prefix +
                         'Intensity detection:')

        if not shape is None:
            r = parameter_intensity.pop('shape', 3)
            if isinstance(r, tuple):
                r = r[0]

        for m in measure:
            if shape is not None:
                intensity = sd.find_intensity(
                    measure_to_array[m], label=shape, max_label=max_label, **parameter_intensity)
            else:
                intensity = me.measure_expression(
                    measure_to_array[m], centers, search_radius=r, **parameter_intensity, processes=1, verbose=False)

            results += (intensity,)

        if verbose:
            timer.print_elapsed_time('Shape detection')

    if valid is not None:
        results = tuple(r[valid] for r in results)

    # correct coordinate offsets of blocks
    results = (results[0] + lower,) + results[1:]

    # correct shapes for merging
    results = tuple(r[:, None] if r.ndim == 1 else r for r in results)

    if verbose:
        total_time.print_elapsed_time('Cell detection')

    gc.collect()

    return results


###############################################################################
# Cell detection processing steps
###############################################################################

def remove_background(source, shape, form='Disk'):
    selem = se.structure_element(shape, form=form, ndim=2).astype('uint8')
    removed = np.empty(source.shape, dtype=source.dtype)
    for z in range(source.shape[2]):
        #img[:,:,z] = img[:,:,z] - grey_opening(img[:,:,z], structure = structureElement('Disk', (30,30)));
        #img[:,:,z] = img[:,:,z] - morph.grey_opening(img[:,:,z], structure = self.structureELement('Disk', (150,150)));
        removed[:, :, z] = source[:, :, z] - np.minimum(
            source[:, :, z], cv2.morphologyEx(source[:, :, z], cv2.MORPH_OPEN, selem))
    return removed


def equalize(source, percentile=(0.5, 0.95), max_value=1.5, selem=(200, 200, 5), spacing=(50, 50, 5), interpolate=1, mask=None):
    equalized = ls.local_percentile(source, percentile=percentile, mask=mask,
                                    dtype=float, selem=selem, spacing=spacing, interpolate=interpolate)
    normalize = 1/np.maximum(equalized[..., 0], 1)
    maxima = equalized[..., 1]
    ids = maxima * normalize > max_value
    normalize[ids] = max_value / maxima[ids]
    equalized = np.array(source, dtype=float) * normalize
    return equalized


def dog_filter(source, shape, sigma=None, sigma2=None):
    if not shape is None:
        fdog = fk.filter_kernel(ftype='dog', shape=shape,
                                sigma=sigma, sigma2=sigma2)
        fdog = fdog.astype('float32')
        filtered = ndf.correlate(source, fdog)
        filtered[filtered < 0] = 0
        return filtered
    else:
        return source


def detect_maxima(source, h_max=None, shape=5, threshold=None, verbose=False):
    # extended maxima
    maxima = md.find_maxima(source, h_max=h_max, shape=shape,
                            threshold=threshold, verbose=verbose)

    # center of maxima
    if h_max:
        centers = md.find_center_of_maxima(
            source, maxima=maxima, verbose=verbose)
    else:
        centers = ap.where(maxima).array

    return centers


###############################################################################
# Cell filtering
###############################################################################


def filter_cells(source, sink, thresholds):
    """Filter a array of detected cells according to the thresholds.

    Arguments
    ---------
    source : str, array or Source
      The source for the cell data.
    sink : str, array or Source
      The sink for the results.
    thresholds : dict
      Dictionary of the form {name : threshold} where name refers to the 
      column in the cell data and threshold can be None, a float 
      indicating a minimal threshold or a tuple (min,max) where min,max can be
      None or a minimal and maximal threshold value.

    Returns
    -------
    sink : str, array or Source
      The thresholded cell data.
    """
    source = io.as_source(source)

    ids = np.ones(source.shape[0], dtype=bool)
    for k, t in thresholds.items():
        if t:
            if not isinstance(t, (tuple, list)):
                t = (t, None)
            if t[0] is not None:
                ids = np.logical_and(ids, t[0] <= source[k])
            if t[1] is not None:
                ids = np.logical_and(ids, t[1] > source[k])
    cells_filtered = source[ids]

    return io.write(sink, cells_filtered)


###############################################################################
# Tests
###############################################################################

def _test():
    """Tests."""
    import numpy as np
    import ClearMap.Visualization.Plot3d as p3d
    import ClearMap.Tests.Files as tsf
    import ClearMap.ImageProcessing.Experts.Cells as cells
