# -*- coding: utf-8 -*-

"""Utilities for integra."""

import os

import matplotlib.pyplot as plt
import pandas as pd
from pybiomart import Dataset
import scipy.stats as stats
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
    scores_df = pd.read_csv(matrix_file, sep='\t')
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
        scores_df.to_csv(output_path, sep='\t', index=False)
    return scores_df


def plot_scores(
    *,
    input_path,
    output_path,
    fig_size=(100, 70),
    x_label,
    y_label,
    font_size,
    x_axis='patient_id',
):
    df = pd.read_csv(input_path, sep='\t', index_col=False)
    plt.figure(figsize=fig_size)
    if x_axis != 'patient_id':
        df_cp = df.set_index('patient_id')
        flipped_df = df_cp.transpose()
        flipped_df = flipped_df.reset_index()
        flipped_df.rename(columns={flipped_df.columns[0]: "genes"}, inplace=True)
        for col in tqdm(flipped_df.columns, desc='Creating scatterplot'):
            if col == 'genes':
                continue
            plt.scatter(flipped_df['genes'], flipped_df[col])
    else:
        for col in tqdm(df.columns, desc='Creating scatterplot'):
            if col == 'patient_id':
                continue
            plt.scatter(df['patient_id'], df[col])
    plt.xlabel(x_label, {'size': '40'})
    plt.ylabel(y_label, {'size': '40'})
    plt.xticks(fontsize=font_size, rotation=90)
    plt.yticks(fontsize=font_size)
    plt.savefig(output_path)
    plt.show()


def find_pvalue(
    *,
    scores_file,
    genotype_file,
    output_file,
    genes=None,
    cases_column,
):
    """
    Calculate the significance of a gene in a population using Mann-Whitney-U test.
    :param scores_file: a tsv file containing the scores of genes across samples.
    :param genotype_file: a file containing the information of the sample.
    :param output_file: a path to save the output file.
    :param genes: a list of the genes to calculate the significance. if None will calculate for all genes.
    :param cases_column: the name of the column containing cases and controls information.
    :return: dataframe with genes and their p_values
    """
    scores_df = pd.read_csv(scores_file, sep='\t', index_col=False)
    genotype_df = pd.read_csv(genotype_file, sep='\t', index_col=False)
    merged_df = pd.merge(genotype_df, scores_df, on='patient_id', how='left')
    df_by_cases = merged_df.groupby(cases_column)
    cases = list(df_by_cases.groups.keys())
    p_values = []
    if genes is None:
        genes = scores_df.columns.tolist()[1:]
    for gene in tqdm(genes, desc='Calculating p_values for genes'):
        case_0 = df_by_cases.get_group(cases[0])[gene].tolist()
        case_1 = df_by_cases.get_group(cases[1])[gene].tolist()
        u_statistic, p_val = stats.mannwhitneyu(case_0, case_1)
        p_values.append([gene, p_val])
    p_values_df = pd.DataFrame(p_values, columns=['genes', 'p_value']).sort_values(by=['p_value'])
    p_values_df.to_csv(output_file, sep='\t', index=False)
    return p_values_df
