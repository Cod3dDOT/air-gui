import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aircrack-gui",
    version="0.0.3",
    description="Gtk 3 Python gui for Aircrack",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Cod3dDot/aircrack-gui",
    scripts=['aircrack-gui/aircrack-gui.py'],
    packages=['aircrack-gui'],
      install_requires=[
          'pygobject',
      ],
    dependency_links=['https://github.com/aircrack-ng/aircrack-ng'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.2'
)
