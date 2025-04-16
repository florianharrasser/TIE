---
Author: Florian Harrasser
Date: 05.07.2024
---

# Single Cell Dry Mass Quantification Using the Transport of Intensity Equation

This software provides an easy method to determine the dry mass of a cell. To determine this property the Transport of Intensity Equation (TIE) is used. This method provides an easy access for data retrieved with a widefield microscope with partially coherent illumination.\
To solve the TIE two different different solutions are implemented - Fast Fourier Transform (FFT) and Total Variation (TV) Regularisation.\
To determine the cell mass a contour detection is implemented for the best possible estimate of the cell area.\
The whole code is writen as a GUI and can also converted to a .exe application. So that the software can be used without installing python nor having programming skills.

# Installation
The required version of python is 3.11 or later.\
For installing the software the requirements.txt file can be used. To install the dependencies and libraries used in this project do the following:

- Navigate to your directory containting the 'requirements.txt' file
- Run the installation of the libraries:
    ```
    pip install -r requirements.txt
    ``` 

For running the software you can execute the following line in your terminal after navigating to the directory where the python files are located:

``` 
python main_window.py
```

# Manual
Should you require guidance, the manual can be accessed via the [official website](https://tie-manual.readthedocs.io/).
