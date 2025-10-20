oct2025 beamtime codebase
==========================

Analysis code for beamtime with samples from Francesco, Paola, and Xiaoyu.

Plot signal
-----------

``plot_intensity.py`` reads a text file that contains two-column numeric data
(e.g., ``x y``), optionally preceded by metadata or header lines. It
automatically detects where the numeric data begins and uses the **last
non-numeric line** before it as axis labels.

Typical file example::

    # Some meta data
    10  123
    20  150
    30  180
    40  140

Running ``plot_intensity.py``


Installation
------------

Clone or download this repository, then install necessary packages by running::

    pip install -r requirements.txt

or::

    conda install --file requirements.txt


Usage
-----

Run the script from the command line::

    python plot_intensity.py <filename>

Example::

    python plot_intensity.py data/Ni.gr

The plot will appear in a window showing:

- **X-axis label** = first label in the header line (e.g., ``Angle``)
- **Y-axis label** = second label in the header line (e.g., ``Intensity``)
- **Title** = the name of the file (e.g., ``Ni.gr``)


License
-------

MIT License.  
Feel free to modify and distribute.
