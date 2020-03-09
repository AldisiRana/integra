# -*- coding: utf-8 -*-

"""Utilities for integra."""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pybiomart import Dataset
from tqdm import tqdm


def merge_matrices(
    *,
    directory,
    output_path,
):
    """
    Merges multiple files in a directory, each file should contain the score of a gene across the samples.

    :param directory: the directory that contains files to merge.
    :param output_path: the path for the merged tsv file.
    :return: a dataframe combining all information from files.
    """
    full_data = pd.DataFrame(data=None, columns=['patient_id'])
    for filename in tqdm(os.listdir(directory), desc="merging matrices"):
        data = pd.read_csv(os.path.join(directory, filename), sep='\t',
                           names=['patient_id', filename.split('_')[0], ''])
        data = data.drop(columns=[''])
        full_data = pd.merge(data, full_data, on='patient_id', how='left')
    full_data.to_csv(output_path, sep='\t', index=False)
    return full_data


def normalize_gene_len(
    *,
    genes_lengths_file=None,
    matrix_file,
    output_path,
):
    """
    Normalize matrix by gene length.

    :param genes_lengths_file: a file containing genes, and their start and end bps.
    :param matrix_file: a tsv file containing a matrix of samples and their scores across genes.
    :param output_path: the path to save the normalized matrix.
    :return: a normalized dataframe.
    """
    if genes_lengths_file:
        genes_df = pd.read_csv(genes_lengths_file, sep='\t')
    else:
        gene_dataset = Dataset(name='hsapiens_gene_ensembl', host='http://www.ensembl.org')
        genes_df = gene_dataset.query(
            attributes=['external_gene_name', 'start_position', 'end_position'],
            only_unique=False,
        )
    genes_lengths = {
        row['Gene name']: round((row['Gene end (bp)'] - row['Gene start (bp)']) / 1000, 3)
        for _, row in genes_df.iterrows()
    }
    scores_df = pd.read_csv(matrix_file, sep='\t', index_col=0)
    unnormalized = []
    for (name, data) in tqdm(scores_df.iteritems(), desc="Normalizing genes scores"):
        if name == 'patient_id':
            continue
        if name not in genes_lengths.keys():
            unnormalized.append(name)
            continue
        # normalize genes by length
        scores_df[name] = round(scores_df[name] / genes_lengths[name], 5)
    # drop genes with unknown length
    scores_df = scores_df.drop(unnormalized, axis=1)
    if output_path:
        scores_df.to_csv(output_path, sep='\t')
    return scores_df
