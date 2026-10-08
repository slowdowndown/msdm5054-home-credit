"""Checks that protect label alignment and confusion-matrix interpretation."""
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from evaluation import load_predictions, threshold_metrics

class EvaluationTests(unittest.TestCase):
    def test_known_counts(self):
        m=threshold_metrics(np.array([0,0,1,1]),np.array([.1,.8,.3,.9]),.5)
        self.assertEqual([m[x] for x in ['tn','fp','fn','tp']],[1,1,1,1])
        self.assertEqual(m['precision'],.5)
        self.assertEqual(m['recall'],.5)
    def test_inclusive_boundary_and_no_flags(self):
        self.assertEqual(threshold_metrics(np.array([0,1]),np.array([.1,.5]),.5)['tp'],1)
        m=threshold_metrics(np.array([0,1]),np.array([.1,.2]),.5)
        self.assertEqual(m['precision'],0)
        self.assertEqual(m['fn'],1)
    def test_reject_bad_inputs(self):
        valid=pd.DataFrame({'SK_ID_CURR':[1,2], 'TARGET':[0,1], 'PRED_PROB':[.1,.8]})
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'p.csv'
            for col, vals in [('SK_ID_CURR',[1,1]),('TARGET',[0,2]),('TARGET',[0,0]),('PRED_PROB',[.1,1.2]),('PRED_PROB',[.1,np.nan])]:
                bad=valid.copy();bad[col]=vals;bad.to_csv(f,index=False)
                with self.subTest(col=col,vals=vals), self.assertRaises(ValueError):load_predictions(f,2)
            valid.to_csv(f,index=False)
            self.assertEqual(len(load_predictions(f,2)),2)
            with self.assertRaises(ValueError):load_predictions(f,3)

if __name__=='__main__':unittest.main()
