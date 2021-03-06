# This file is part of obs_base.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__all__ = ("PackagesFormatter", )

import os.path

from lsst.daf.butler.formatters.file import FileFormatter


class PackagesFormatter(FileFormatter):
    """Interface for reading and writing objects that support the standard
    afw I/O readFits/writeFits methods.
    """
    supportedWriteParameters = frozenset({"format"})
    supportedExtensions = frozenset({".yaml", ".pickle", ".pkl"})

    @property
    def extension(self) -> str:
        # Default to YAML but allow configuration via write parameter
        format = self.writeParameters.get("format", "yaml")
        if format == "yaml":
            return ".yaml"
        elif format == "pickle":
            return ".pickle"
        raise RuntimeError(f"Requested file format '{format}' is not supported for Packages")

    def _readFile(self, path, pytype):
        """Read a file from the path in FITS format.

        Parameters
        ----------
        path : `str`
            Path to use to open the file.
        pytype : `type`
            Class to use to read the serialized file.

        Returns
        -------
        data : `object`
            Instance of class ``pytype`` read from serialized file. None
            if the file could not be opened.
        """
        if not os.path.exists(path):
            return None

        return pytype.read(path)

    def _fromBytes(self, serializedDataset, pytype=None):
        """Read the bytes object as a python object.

        Parameters
        ----------
        serializedDataset : `bytes`
            Bytes object to unserialize.
        pytype : `type`
            The Python type to be instantiated. Required.

        Returns
        -------
        inMemoryDataset : `object`
            The requested data as an object, or None if the string could
            not be read.
        """
        # The format can not come from the formatter configuration
        # because the current configuration has no connection to how
        # the data were stored.
        format = "yaml" if serializedDataset.startswith(b"!<lsst.base.Packages>") else "pickle"
        return pytype.fromBytes(serializedDataset, format)

    def _writeFile(self, inMemoryDataset):
        """Write the in memory dataset to file on disk.

        Parameters
        ----------
        inMemoryDataset : `object`
            Object to serialize.

        Raises
        ------
        Exception
            The file could not be written.
        """
        inMemoryDataset.write(self.fileDescriptor.location.path)

    def _toBytes(self, inMemoryDataset):
        """Write the in memory dataset to a bytestring.

        Parameters
        ----------
        inMemoryDataset : `object`
            Object to serialize

        Returns
        -------
        serializedDataset : `bytes`
            YAML string encoded to bytes.

        Raises
        ------
        Exception
            The object could not be serialized.
        """
        format = "yaml" if self.extension == ".yaml" else "pickle"
        return inMemoryDataset.toBytes(format)
