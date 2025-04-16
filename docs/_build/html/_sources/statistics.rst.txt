Statistics
========================
The statistics function is a tool for calculating the cell mass with various parameters; therefore, all calculation steps and contour detection
steps previously mentioned have to be done before. The image size can be changed (in +x, -x, +y, -y direction). In addition, the axial distance
for the FFT calculation and the parameters for the TV regularisation can be set. Separated with whitespace, it is possible to define multiple
parameters in one step. To execute the calculation, the checkbox next to the input fields has to be checked.

A separate directory is created in the path for each “statistic” performed. This directory has the same name as the file uploaded in the 
application. A metadata file is saved in this directory, which contains the `names` of the calculated cells, the opd plot, and the ``.csv`` file,
which are also saved in directories. This allows easy access for further analysis with other tools, making it easier to upload there.