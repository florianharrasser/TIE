.. _contour_detection:

Contour Detection
==================

The opd must be calculated for contour detection (that means the bottom left plot can not be empty). The options for selecting a contour 
are listed here as subsections. The mass of the contour displayed in the plot is calculated by pressing the ``Calculate contour mass`` button;
this process is the same for all contour recognition options.


Generate Contour
~~~~~~~~~~~~~~~~~~~~~~

The contour detection has already taken place and is shown as yellow lines in the graphic. At the beginning, all possible contours are displayed.

Now it is important to set the parameters for contour detection so that one of these contours fits perfectly the cell.
There are two parameters for this. The ``Threshold`` can be seen as a parameter for controlling the sensitivity of contour detection. 
If this parameter is increased, the contour is only drawn if large intensity gaps exist. The lower the threshold value is selected, 
the more sensitive the contour detection is for small intensity gaps.

.. image:: _img/treshold.png
    :width: 500
    :align: center


Once the correct threshold value has been found, the contour can be selected using the ``Contours`` slider. If you move the slider all the
way to the left, all contours are displayed. The contours are displayed individually if you move the slider to the right. A contour must be 
selected for the further calculation steps.

.. image:: _img/contour_selection.png
    :width: 500
    :align: center


If the contour found does not cover the entire cell, the contour can be inflated or deflated.

.. image:: _img/inflate.png
    :width: 500
    :align: center

Once you have found the correct contour, you can calculate the mass within the contour by clicking on the ``Calculate Contour Mass`` button.


Draw Contour Manually
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If no contour can be found when setting the parameter correctly, it is possible to draw the contour manually by selecting the ``Draw contour manually``
button. The created contours are hidden and by clicking with the right mouse button on the image, points can be drawn to set the contour. 
To delete this contour, click on the image again and start drawing. When you release the mouse button, the shape is drawn. When satisfied 
with your drawn contour, click the ``Calculate contour mass`` button. This step calculates the mass of the contour.

Click the ``Generate contour`` button to exit manual contour drawing mode.

.. image:: _img/contour_manually.png
    :width: 500
    :align: center


Store Contour
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contours can also be saved for the time during which no new file is uploaded. To save, click on the 'Save contour' button. 
To retrieve the contour, press ``Retrieve contour``. If the retrieved contour is shown, the button name changes to 
`Hide saved contour` and is highlighted in blue. It can only be saved a single contour. To save a new contour, hit the '``Save Contour`` button again.

.. image:: _img/store_contour.png
    :width: 500
    :align: center
