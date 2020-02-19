# integra
 A basic tool for handling and normalizing genetic scoring

## Installation
``integra`` can be installed on python3+ from the latest code on [GitHub](https://github.com/AldisiRana/integra) with:

    $ pip install git+https://github.com/AldisiRana/integra.git

## Usage
There are currently 2 functions that can be called in this package.

### Merge matrices
The merge function allows the merging of the output in [GenePy](https://github.com/UoS-HGIG/GenePy). the function merges multiple files in a directory, each file should contain the score of a gene across the samples. These files have to be in the same format. The first column has to be the sample id and the second column has to be the score. Furthermore the filename must contain the name of the gene.

    $ integra merge -d /directory/of/files -o /output/path.tsv

### Normalize scores
This function takes a matrix of scores and normalizes it by gene length. The file should have the genes as columns and samples as rows. A file with gene lengths can be produced from [BioMart](https://www.ensembl.org/biomart/martview/1c08c2c0c4cf030b34d76861a1d2a25e). If genes lengths files is not provided, a file will be produced by the function.

    $ integra normalize -m /path/to/matrix/file.tsv -o /output/path.tsv -g /path/to/genes/lengths/file
