import pytest
from linkapy.parsing import Linkapy_Parser
import mudata as md
from conftest import mu_to_dense
import numpy as np

class TestAllcools:
    @pytest.mark.parametrize(
        "dynamic_methylation_path,methylation_pattern",
        [
            ("allcools_path", ('*WCGN*tsv.gz', '*GCHN*tsv.gz')),
            ("methyldackel_path", ('*WCGN.bedgraph', '*GCHN.bedgraph')),
            ("bismarkcov_path", ('*WCGN.bismark.cov', '*GCHN.bismark.cov')),
            ("bismarkrep_path", ('*WCGN.bismark.rep.gz', '*GCHN.bismark.rep.gz')),
            ("bedmethyl_path", ('*WCGN*bed.gz', '*GCHN*bed.gz')),
        ],
        indirect=["dynamic_methylation_path"]
    )
    def test_parser_chromsizes(self, tmp_path, bed_path, rna_path, dynamic_methylation_path, methylation_pattern):
        '''
        test chromsizes / binsize mode.
        '''
        lp = Linkapy_Parser(
            methylation_path = str(dynamic_methylation_path),
            transcriptome_path = str(rna_path),
            output = str(tmp_path / 'output'),
            methylation_pattern = methylation_pattern,
            methylation_pattern_names = ('WCGN', 'GCHN'),
            transcriptome_pattern = ('*tsv',),
            NOMe = False,
            threads = 2,
            chromsizes = str(bed_path / 'genome.chromsizes'),
            regions = (),
            blacklist = (),
            binsize = 20,
            project = 'chromsizes_test'
        )
        lp.parse()

        # Output / metadata
        mo = tmp_path / 'output' / 'chromsizes_test.h5mu'
        assert mo.exists(), "muData object not created."
        mu = md.read(mo)
        assert mu.shape == (3,52), f"Expected shape (3, 52), got {mu.shape}."
        assert set(mu.obs.index) == set(['cell1', 'cell2', 'cell3']), f"Obs inferral failed, got {mu.obs.index}."

        # Assert WCGN part.
        _dense = mu_to_dense(mu, 'METH_WCGN')
        assert np.isnan(_dense[0, 0]), f"WCGN cell1 in bin 0-20 should be NAN. Got {_dense[0, 0]}."
        assert _dense[0, 1] == 0.25, f"WCGN cell1 in bin 20-40 should be 0.25. Got {_dense[0, 1]}."
        assert _dense[0, 2] == 0.75, f"WCGN cell1 in bin 40-60 should be 0.75. Got {_dense[0, 2]}."
        
        assert _dense[1, 11] == 0.50, f"WCGN cell2 in bin 220-240 should be 0.50. Got {_dense[1, 11]}."
        assert _dense[1, 12] == 0.75, f"WCGN cell2 in bin 240-260 should be 0.75. Got {_dense[1, 12]}."

        assert _dense[2, 1] == 1.0, f"WCGN cell3 in bin 20-40 should be 1.0. Got {_dense[2, 1]}."
        assert _dense[2, 2] == 1.0, f"WCGN cell3 in bin 40-60 should be 1.0. Got {_dense[2, 2]}."
        
        # Assert GCHN part.
        _dense = mu_to_dense(mu, 'METH_GCHN')
        assert np.isnan(_dense[0, 0]), f"GCHN cell1 in bin 0-20 should be NAN. Got {_dense[0, 0]}."
        assert _dense[0, 1] == 0.25, f"GCHN cell1 in bin 20-40 should be 0.25. Got {_dense[0, 1]}."
        assert _dense[0, 2] == 0.25, f"GCHN cell1 in bin 40-60 should be 0.25. Got {_dense[0, 2]}."
        
        assert _dense[1, 11] == 0.44, f"GCHN cell2 in bin 220-240 should be 0.44. Got {_dense[1, 11]}."

        assert _dense[2, 1] == 1.0, f"GCHN cell3 in bin 20-40 should be 1.0. Got {_dense[2, 1]}."
        assert _dense[2, 2] == 1.0, f"GCHN cell3 in bin 40-60 should be 1.0. Got {_dense[2, 2]}."
        assert _dense[2, 11] == 0.0, f"GCHN cell3 in bin 220-240 should be 0.0. Got {_dense[2, 11]}."


    @pytest.mark.parametrize(
            "bedfiles",
            [
                ('gene1.bed', 'gene2.bed'),
                ('gene1.bed.gz', 'gene2.bed.gz')
            ]
    )
    def test_parser_regions(self, tmp_path, bed_path, dynamic_methylation_path, methylation_pattern, rna_path, bedfiles):
        '''
        test bed files (bed and bed.gz)
        '''
        lp = Linkapy_Parser(
            methylation_path = str(dynamic_methylation_path),
            transcriptome_path = str(rna_path),
            output = str(tmp_path / 'output'),
            methylation_pattern = methylation_pattern,
            methylation_pattern_names = ('WCGN', 'GCHN'),
            transcriptome_pattern = ('*tsv',),
            NOMe = False,
            threads = 2,
            chromsizes = None,
            regions = (str(bed_path / bedfiles[0]), str(bed_path / bedfiles[1])),
            blacklist = (),
            binsize = 20,
            project = 'regions_test'
        )
        lp.parse()

        # Output checks.
        mo = tmp_path / 'output' / 'regions_test.h5mu'
        assert mo.exists(), "muData object not created."
        mu = md.read(mo)
        assert mu.shape == (3,6), f"Expected shape (3, 6), got {mu.shape}."
        assert set(mu.obs.index) == set(['cell1', 'cell2', 'cell3']), f"Obs inferral failed, got {mu.obs.index}."

        # Assert WCGN part.
        dense = mu_to_dense(mu, 'METH_WCGN')
        exp_WCGN = np.array([0.5, np.nan, np.nan, 0.625, 1, 0]).reshape(3,2)
        assert np.allclose(dense, exp_WCGN, equal_nan=True), f"Expected WCGN dense matrix:{exp_WCGN} Got:\n{dense}"
        
        # Assert GCHN part.
        dense = mu_to_dense(mu, 'METH_GCHN')
        exp_GCHN = np.array([0.25, np.nan, np.nan, 0.44, 1, 0]).reshape(3,2)
        assert np.allclose(dense, exp_GCHN, equal_nan=True), f"Expected WCGN dense matrix:{exp_GCHN} Got:\n{dense}"


    def test_parser_blacklist(self, tmp_path, bed_path, allcools_path, rna_path):
        '''
        Test blacklist exclusion.
        '''
        lp = Linkapy_Parser(
            methylation_path = str(allcools_path),
            transcriptome_path = str(rna_path),
            output = str(tmp_path / 'output'),
            methylation_pattern = ('*WCGN*tsv.gz', '*GCHN*tsv.gz'),
            methylation_pattern_names = ('WCGN', 'GCHN'),
            transcriptome_pattern = ('*tsv',),
            NOMe = False,
            threads = 2,
            chromsizes = None,
            regions = (str(bed_path / 'gene1.bed'), str(bed_path / 'gene2.bed.gz')),
            blacklist = (str(bed_path / 'blacklist1.bed'), str(bed_path / 'blacklist2.bed')),
            binsize = 20,
            project = 'blacklist_test'
        )
        lp.parse()

        # Output checks.
        mo = tmp_path / 'output' / 'blacklist_test.h5mu'
        assert mo.exists(), "muData object not created."
        mu = md.read(mo)
        assert mu.shape == (3,6), f"Expected shape (3, 6), got {mu.shape}."
        assert set(mu.obs.index) == set(['cell1', 'cell2', 'cell3']), f"Obs inferral failed, got {mu.obs.index}."

        # Assert WCGN part.
        dense = mu_to_dense(mu, 'METH_WCGN')
        exp_WCGN = np.array([0.25, np.nan, np.nan, 0.5, 1, 0]).reshape(3,2)
        assert np.allclose(dense, exp_WCGN, equal_nan=True), f"Expected WCGN dense matrix:{exp_WCGN}, got {dense}"
        
        # Assert GCHN part.
        dense = mu_to_dense(mu, 'METH_GCHN')
        exp_GCHN = np.array([0.25, np.nan, np.nan, 0.44, 1, 0]).reshape(3,2)
        assert np.allclose(dense, exp_GCHN, equal_nan=True), f"Expected WCGN dense matrix:{exp_GCHN}, got {dense}"

    def test_parser_rnaonly(self, tmp_path, bed_path, rna_path):
        '''
        Test RNA data only. No methylation data.
        '''
        lp = Linkapy_Parser(
            methylation_path = None,
            transcriptome_path = str(rna_path),
            output = str(tmp_path / 'output'),
            transcriptome_pattern = ('*tsv',),
            NOMe = False,
            threads = 2,
            chromsizes = None,
            regions = (str(bed_path / 'gene1.bed'), str(bed_path / 'gene2.bed.gz')),
            blacklist = (str(bed_path / 'blacklist1.bed'), str(bed_path / 'blacklist2.bed')),
            binsize = 20,
            project = 'rna_only_test'
        )
        lp.parse()

        # Output checks.
        mo = tmp_path / 'output' / 'rna_only_test.h5mu'
        assert mo.exists(), "muData object not created."
        mu = md.read(mo)
        assert mu.shape == (3,2), f"Expected shape (3, 2), got {mu.shape}."
        assert set(mu.obs.index) == set(['cell1_rna', 'cell2_rna', 'cell3_rna']), f"Obs inferral failed, got {mu.obs.index}."
        exp_RNA = np.array([[50, 20], [100, 100], [33, 33]])
        assert np.allclose(mu['RNA_tsv'].X.todense(), exp_RNA), f"Expected RNA matrix = {exp_RNA}, got {mu['RNA_tsv'].X.todense()}"
        

    def test_parser_regions(self, tmp_path, bed_path, allcools_path):
        '''
        Test meth data only. Custom pattern names.
        '''
        lp = Linkapy_Parser(
            methylation_path = str(allcools_path),
            transcriptome_path = None,
            output = str(tmp_path / 'output'),
            methylation_pattern = ('*WCGN*tsv.gz', '*GCHN*tsv.gz'),
            methylation_pattern_names = ('My_famous_label', 'whatsinaname'),
            NOMe = False,
            threads = 2,
            chromsizes = None,
            regions = (str(bed_path / 'gene1.bed'), str(bed_path / 'gene2.bed')),
            blacklist = (),
            binsize = 20,
            project = 'meth_only_test'
        )
        lp.parse()

        # Output checks.
        mo = tmp_path / 'output' / 'meth_only_test.h5mu'
        assert mo.exists(), "muData object not created."
        mu = md.read(mo)
        assert mu.shape == (3,4), f"Expected shape (3, 4), got {mu.shape}."
        assert set(mu.obs.index) == set(['cell1', 'cell2', 'cell3']), f"Obs inferral failed, got {mu.obs.index}."

        # Assert WCGN part.
        dense = mu_to_dense(mu, 'METH_My_famous_label')
        exp_WCGN = np.array([0.5, np.nan, np.nan, 0.625, 1, 0]).reshape(3,2)
        assert np.allclose(dense, exp_WCGN, equal_nan=True), f"Expected WCGN dense matrix:{exp_WCGN} Got:\n{dense}"
        
        # Assert GCHN part.
        dense = mu_to_dense(mu, 'METH_whatsinaname')
        exp_GCHN = np.array([0.25, np.nan, np.nan, 0.44, 1, 0]).reshape(3,2)
        assert np.allclose(dense, exp_GCHN, equal_nan=True), f"Expected WCGN dense matrix:{exp_GCHN} Got:\n{dense}"


    def test_parser_nome(self, tmp_path, bed_path, allcools_path):
        '''
        Test meth data only. in NOMe mode.
        '''
        lp = Linkapy_Parser(
            methylation_path = str(allcools_path),
            transcriptome_path = None,
            output = str(tmp_path / 'output'),
            NOMe = True,
            threads = 2,
            chromsizes = None,
            regions = (str(bed_path / 'gene1.bed'), str(bed_path / 'gene2.bed')),
            blacklist = (),
            binsize = 20,
            project = 'meth_only_test'
        )
        lp.parse()

        # Output checks.
        mo = tmp_path / 'output' / 'meth_only_test.h5mu'
        assert mo.exists(), "muData object not created."
        mu = md.read(mo)
        assert mu.shape == (3,4), f"Expected shape (3, 4), got {mu.shape}."
        assert set(mu.obs.index) == set(['cell1', 'cell2', 'cell3']), f"Obs inferral failed, got {mu.obs.index}."

        # Assert WCGN part.
        dense = mu_to_dense(mu, 'METH_Meth')
        exp_WCGN = np.array([0.5, np.nan, np.nan, 0.625, 1, 0]).reshape(3,2)
        assert np.allclose(dense, exp_WCGN, equal_nan=True), f"Expected WCGN dense matrix:{exp_WCGN} Got:\n{dense}"
        
        # Assert GCHN part.
        dense = mu_to_dense(mu, 'METH_Acc')
        exp_GCHN = np.array([0.25, np.nan, np.nan, 0.44, 1, 0]).reshape(3,2)
        assert np.allclose(dense, exp_GCHN, equal_nan=True), f"Expected WCGN dense matrix:{exp_GCHN} Got:\n{dense}"

