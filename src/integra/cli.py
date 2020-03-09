# -*- coding: utf-8 -*-

"""Command line interface for integra."""

import click

from .utils import merge_matrices, normalize_gene_len, find_pvalue


@click.group()
def main():
    """Pipeline for handling and normalizing scores"""


@main.command()
@click.option('-d', '--directory', required=True, help="The directory that contains the matrices to merge.")
@click.option('-o', '--output-path', required=True, help="The path to output the merged matrix.")
def merge(
    *,
    directory,
    output_path
):
    """This command merges all matrices in a directory into one big matrix"""
    click.echo("Starting the merging process")
    merge_matrices(
        directory=directory,
        output_path=output_path,
    )
    click.echo("Merging is done.")


@main.command()
@click.option('-m', '--matrix-file', required=True, help="The scoring matrix to normalize.")
@click.option('-g', '--genes-lengths-file',
              help="The file containing the lengths of genes. If not provided it will be produced.")
@click.option('-o', '--output-path', required=True, help="The path to output the normalized matrix.")
def normalize(
    *,
    matrix_file,
    genes_lengths_file=None,
    output_path=None
):
    """This command normalizes the scoring matrix by gene length."""
    click.echo("Normalization in process.")
    normalize_gene_len(
        matrix_file=matrix_file,
        genes_lengths_file=genes_lengths_file,
        output_path=output_path,
    )


@main.command()
@click.option('-s', '--scores-file', required=True, help="The scoring file of genes across a population.")
@click.option('-i', '--genotype-file', required=True, help="File containing information about the cohort.")
@click.option('-o', '--output-file', required=True, help="The path to output the pvalues of genes.")
@click.option('-g', '--genes',
              help="a list containing the genes to calculate. if not provided all genes will be used.")
@click.option('-c', '--cases-column', required=True, help="the name of the column that contains the case/control type.")
def calculate_pval(
    *,
    scores_file,
    genotype_file,
    output_file,
    genes,
    cases_column,
):
    click.echo("The process for calculating the p_values will start now.")
    df = find_pvalue(
        scores_file=scores_file,
        output_file=output_file,
        genotype_file=genotype_file,
        genes=genes,
        cases_column=cases_column,
    )
    click.echo('Process is complete.')
    click.echo(df.info())


if __name__ == "__main__":
    main()
