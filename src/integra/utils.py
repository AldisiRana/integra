# -*- coding: utf-8 -*-

"""Utilities for integra."""

import os

from pybiomart import Dataset
import pandas as pd
from tqdm import tqdm


def merge_matrices(
        *,
        directory,
        output_path,
):
    full_data = pd.DataFrame(data=None, columns=['patient_id'])
    for filename in tqdm(os.listdir(directory), desc="merging matrices"):
        data = pd.read_csv(os.path.join(directory, filename), sep='\t',
                           names=['patient_id', filename.split('_')[0], ''])
        data = data.drop(columns=[''])
        full_data = pd.merge(data, full_data, on='patient_id', how='left')
    full_data.to_csv(output_path, sep='\t')
    return full_data


def normalize_gene_len(
        *,
        genes_lengths_file=None,
        matrix_file,
        output_path,
):
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
