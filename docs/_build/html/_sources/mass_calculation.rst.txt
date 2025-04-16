Dry Mass Calculation
=========================


\section{Dry Mass Calculation}
The button and thus the dry mass calculation can only be carried out if an area is correctly defined, see section~\ref{sec:cell-selection}.

Two options are available for calculating the optical path delay (opd). The Fast Fourier Transform :ref:`ref_FFT` and the 
Total Variation (TV) Regularization :ref:`_ref_TV`. For both calculation methods, it is important that there are no cells or other artifacts 
(dust, noise, air bubbles, etc.) at the boundaries of the selected area.


.. warning:: 
    ATTENTION:
    Here are now more possibilities for the calculation. Add them!



.. _ref_FFT:
FFT
~~~~~~~~~~~~~~~~~~~~~~~

It is important to enter an axis distance for the calculation. This parameter is used to define the axial distance for the derivative 
calculation. The axial distance can only be selected so that the stack is not exceeded during addition with the focused image and cannot 
be less than 0 during subtraction. A larger axial distance leads to a blurred effect in the reconstruction. In order to obtain the best 
possible solution, a small axial distance should be tried. If the image is noisy or the reconstruction does not work properly, the axial 
separation can be set to larger distances, which results in less influence of the noise on the reconstruction.

The axial distance can be entered as an index and refers to the distance between the indices in the stack.
After setting the axial distance, the optical path length can be calculated by clicking the ``Calculate Optical Path Length (FFT)`` button.
If the axial distance is within the range, the optical path delay is calculated and displayed in the lower left-hand graphic.


.. image:: _img/axial_separation.png
    :width: 500
    :align: center

.. _ref_TV:
TV Regularization
~~~~~~~~~~~~~~~~~~~~~~~

For the calculation with TV regularization, it is important to set the parameter in the Settings Window~\ref{sec:settingWindow} 
(the entry for the axial separation has no influence on this method).

This method is useful if the reconstruction with the FFT method~\ref{subsec:FFT} does not work. It is better suited to processing noisy images. 
The penalty factor is crucial here. Penalty factors that are too large lead to a flattening effect, which results in a falsification of 
the dry mass. This factor is a compromise between flattening the cell mass and poor reconstruction. The best choice must be tried out manually. Iterations can also be set in the Settings Window~\ref{sec:settingWindow}, high iterations take a lot of time to reconstruct, a good estimate here is about 50 iterations, but this can vary for different images.
In general, with this method, it is important to minimize the penalty factor to avoid falsifications in the dry mass. In addition, too few
iterations lead to a poor reconstruction, while too many iterations do not influence the result.

After setting the parameters, the reconstruction can be executed by clicking the ``Calculate Optical Path Length (TV Regularization)`` button.


.. list-table::
   :widths: 50 50
   :align: center
   :header-rows: 0

   * - .. image:: _img/TV_parameters.png
         :width: 300
     - .. image:: _img/tv_button.png
         :width: 300

         
.. .. image:: _img/TV_parameters.png
..     :width: 500
..     :align: center


.. .. image:: _img/tv_button.png
..     :width: 500
..     :align: center
    


