"""Part D: reproducible evaluation of existing C predictions, without model fitting.
Run: python src/evaluation.py --root .
"""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import platform
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import (roc_auc_score, average_precision_score, brier_score_loss,
    log_loss, roc_curve, precision_recall_curve, confusion_matrix)

THRESHOLDS = (0.05, 0.10, 0.15, 0.20, 0.30, 0.50)
CONTEXT = ('C fixed-validation predictions; early stopping selected 892 rounds on this '
           'validation set. Descriptive development evaluation, not an untouched test. '
           'The separate 705-round full-data model is not evaluated here.')

def load_predictions(path, expected_rows=61503):
    df = pd.read_csv(path)
    required = ['SK_ID_CURR', 'TARGET', 'PRED_PROB']
    if not set(required).issubset(df.columns):
        raise ValueError(f'Required columns: {required}')
    df = df[required].copy()
    if len(df) != expected_rows:
        raise ValueError(f'Expected {expected_rows} rows, got {len(df)}')
    if df.isna().any().any() or not df.SK_ID_CURR.is_unique:
        raise ValueError('Missing values or duplicate customer IDs')
    if not df.TARGET.isin([0, 1]).all() or df.TARGET.nunique() != 2:
        raise ValueError('TARGET must contain both binary classes')
    p = pd.to_numeric(df.PRED_PROB, errors='raise').to_numpy(dtype=float)
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError('Probabilities must be finite and in [0, 1]')
    df['PRED_PROB'] = p
    return df

def threshold_metrics(y, p, threshold):
    tn, fp, fn, tp = confusion_matrix(y, p >= threshold, labels=[0, 1]).ravel()
    ratio = lambda a, b: float(a / b) if b else 0.0
    return dict(threshold=threshold, tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp),
        precision=ratio(tp, tp+fp), recall=ratio(tp, tp+fn),
        specificity=ratio(tn, tn+fp), false_positive_rate=ratio(fp, fp+tn),
        accuracy=ratio(tp+tn, len(y)), f1=ratio(2*tp, 2*tp+fp+fn),
        flagged_fraction=ratio(tp+fp, len(y)))

def wilson(k, n):
    z = 1.959963984540054
    rate = k/n
    den = 1+z*z/n
    mid = (rate+z*z/(2*n))/den
    half = z*np.sqrt(rate*(1-rate)/n+z*z/(4*n*n))/den
    return mid-half, mid+half

def bootstrap_auc(y, p, n_bootstrap=500, seed=42):
    # Conditional uncertainty for fixed predictions, NOT selection-adjusted uncertainty.
    rng = np.random.default_rng(seed)
    pos = np.flatnonzero(y == 1)
    neg = np.flatnonzero(y == 0)
    scores = []
    for _ in range(n_bootstrap):
        idx = np.r_[rng.choice(pos, len(pos)), rng.choice(neg, len(neg))]
        scores.append(roc_auc_score(y[idx], p[idx]))
    return np.quantile(scores, [0.025, 0.975]).tolist()

def save_plot(fig, out, name):
    fig.savefig(out / 'figures' / f'{name}.png', dpi=180, bbox_inches='tight')
    plt.close(fig)

def run(root, n_bootstrap=500):
    root = Path(root).resolve()
    inp = root/'results/c'
    out = root/'results/d'
    (out/'figures').mkdir(parents=True, exist_ok=True)
    source = inp/'validation_predictions_v1.csv'
    df = load_predictions(source)
    y = df.TARGET.to_numpy(dtype=int)
    p = df.PRED_PROB.to_numpy()
    config = json.loads((inp/'final_model_config.json').read_text())
    auc = roc_auc_score(y, p)
    if abs(auc - config['fixed_validation_auc']) > 1e-10:
        raise ValueError('Recomputed AUC disagrees with C configuration')
    prevalence = float(y.mean())
    metrics = dict(n=len(y), positives=int(y.sum()), negatives=int((y==0).sum()),
        prevalence=prevalence, roc_auc=auc, average_precision=average_precision_score(y,p),
        brier_score=brier_score_loss(y,p), log_loss=log_loss(y,p),
        mean_probability=float(p.mean()), minimum_probability=float(p.min()),
        maximum_probability=float(p.max()), all_negative_accuracy=1-prevalence,
        prevalence_brier=prevalence*(1-prevalence),
        auc_bootstrap_95_ci=bootstrap_auc(y,p,n_bootstrap), bootstrap_replicates=n_bootstrap,
        bootstrap_seed=42, context=CONTEXT)
    table = pd.DataFrame([threshold_metrics(y,p,t) for t in THRESHOLDS])
    table.to_csv(out/'threshold_metrics.csv',index=False)
    pd.DataFrame([{k:v for k,v in metrics.items() if not isinstance(v,list)}]).to_csv(out/'metrics.csv',index=False)
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    # Quantile calibration/risk groups; ties are kept together.
    df['risk_bin'] = pd.qcut(df.PRED_PROB,10,duplicates='drop')
    rows=[]
    for rank, (_,g) in enumerate(df.groupby('risk_bin',observed=True),1):
        lo,hi=wilson(g.TARGET.sum(),len(g))
        rows.append(dict(risk_decile=rank,n=len(g),positives=int(g.TARGET.sum()),
            min_probability=g.PRED_PROB.min(),max_probability=g.PRED_PROB.max(),
            mean_probability=g.PRED_PROB.mean(),observed_rate=g.TARGET.mean(),
            observed_rate_ci_low=lo,observed_rate_ci_high=hi,
            positive_capture=g.TARGET.sum()/y.sum(),lift=g.TARGET.mean()/prevalence))
    bins=pd.DataFrame(rows)
    bins.to_csv(out/'risk_deciles.csv',index=False)
    error_rows=[]
    for t in (0.1,0.5):
        pred=p>=t
        labels=np.select([(y==1)&pred,(y==0)&pred,(y==1)&~pred],['TP','FP','FN'],default='TN')
        for label in ('TP','FP','FN','TN'):
            vals=p[labels==label]
            error_rows.append(dict(threshold=t,error_type=label,n=len(vals),
                mean_probability=float(vals.mean()) if len(vals) else None,
                p10=float(np.quantile(vals,.1)) if len(vals) else None,
                median=float(np.median(vals)) if len(vals) else None,
                p90=float(np.quantile(vals,.9)) if len(vals) else None))
    pd.DataFrame(error_rows).to_csv(out/'error_summary.csv',index=False)
    summary=pd.read_csv(inp/'model_summary.csv')
    summary['source']='C supplied summary; only final prediction AUC recomputed by D'
    summary['caveat']=np.where(summary.experiment.str.startswith('Final'),
        'Validation-selected early stopping: 892 rounds; not the full-data 705-round model',
        'Development result; feature selection fixed before inner CV')
    summary.to_csv(out/'model_comparison.csv',index=False)
    cv=pd.read_csv(inp/'cv_results.csv')
    cv_rows=[]
    for col in ['baseline_v1_auc','regularized_v1_auc','weighted_v1_auc']:
        cv_rows.append(dict(experiment=col,mean=cv[col].mean(),std=cv[col].std(ddof=1),
                            min=cv[col].min(),max=cv[col].max(),n_folds=len(cv)))
    pd.DataFrame(cv_rows).to_csv(out/'cv_summary.csv',index=False)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,
                         'axes.spines.right':False,'figure.facecolor':'white'})
    blue='#176B87'; orange='#C56333'
    fpr,tpr,_=roc_curve(y,p)
    fig,ax=plt.subplots(figsize=(6.5,5))
    ax.plot(fpr,tpr,color=blue,lw=2,label=f'V1 regularized: AUC {auc:.4f}')
    ax.plot([0,1],[0,1],'--',color='gray',label='Random ranking')
    ax.set(xlabel='False positive rate',ylabel='True positive rate (recall)',title='ROC | development validation',xlim=(0,1),ylim=(0,1))
    ax.legend(loc='lower right'); save_plot(fig,out,'01_roc')
    precision,recall,_=precision_recall_curve(y,p)
    fig,ax=plt.subplots(figsize=(6.5,5)); ax.plot(recall,precision,color=blue,label=f'Average precision {metrics["average_precision"]:.4f}')
    ax.axhline(prevalence,color=orange,ls='--',label=f'Prevalence {prevalence:.2%}')
    ax.set(xlabel='Recall',ylabel='Precision',title='Precision–recall | development validation',xlim=(0,1),ylim=(0,1))
    ax.legend(); save_plot(fig,out,'02_precision_recall')
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for ax,t in zip(axes,[.1,.5]):
        m=confusion_matrix(y,p>=t,labels=[0,1]); ax.imshow(m,cmap='Blues')
        for i in range(2):
            for j in range(2): ax.text(j,i,f'{m[i,j]:,}',ha='center',va='center',color='white' if m[i,j]>m.max()/2 else '#152F40',fontsize=14)
        ax.set(xticks=[0,1],yticks=[0,1],xticklabels=['0','1'],yticklabels=['0','1'],xlabel='Predicted label',ylabel='True label',title=f'Illustrative threshold = {t}')
    fig.tight_layout(); save_plot(fig,out,'03_confusion_matrices')
    fig,ax=plt.subplots(figsize=(6.5,5))
    for col,label in [('precision','Precision'),('recall','Recall'),('flagged_fraction','Fraction flagged')]: ax.plot(table.threshold,table[col],marker='o',label=label)
    ax.set(xlabel='Illustrative threshold (not optimized)',ylabel='Fraction',ylim=(0,1),title='Threshold trade-offs');ax.legend();save_plot(fig,out,'04_threshold_tradeoffs')
    fig,ax=plt.subplots(figsize=(6.5,5))
    ax.errorbar(bins.mean_probability,bins.observed_rate,yerr=np.array([bins.observed_rate-bins.observed_rate_ci_low,bins.observed_rate_ci_high-bins.observed_rate]),fmt='o-',color=blue,capsize=3,label='Risk deciles; Wilson 95% intervals')
    upper=max(bins.mean_probability.max(),bins.observed_rate_ci_high.max())*1.1
    ax.plot([0,upper],[0,upper],'--',color='gray',label='Perfect calibration')
    ax.set(xlabel='Mean predicted probability',ylabel='Observed positive rate',title='Calibration | descriptive check');ax.legend(fontsize=9);save_plot(fig,out,'05_calibration')
    fig,ax=plt.subplots(figsize=(6.5,5)); ax.bar(bins.risk_decile,bins.observed_rate,color=blue)
    ax.axhline(prevalence,color=orange,ls='--',label='Overall positive rate')
    ax.set(xlabel='Risk decile (1 = lowest predicted risk)',ylabel='Observed positive rate',title='Risk concentration',xticks=range(1,len(bins)+1));ax.legend();save_plot(fig,out,'06_risk_deciles')
    fig,ax=plt.subplots(figsize=(7.5,4.5))
    for col,label in [('baseline_v1_auc','Baseline'),('regularized_v1_auc','Regularized'),('weighted_v1_auc','Weighted (corrected)')]: ax.plot(cv.fold,cv[col],marker='o',label=label)
    ax.set(xlabel='Fold',ylabel='ROC-AUC',title='Training-partition CV | C supplied results',xticks=range(1,6));ax.legend();save_plot(fig,out,'07_cv_comparison')
    imp=pd.read_csv(inp/'feature_importance.csv').head(15).iloc[::-1]
    fig,ax=plt.subplots(figsize=(8,6));ax.barh(imp.feature,imp.importance,color=blue)
    ax.set(xlabel='Split count (not SHAP or effect size)',title='Full-data 705-round model | feature usage');save_plot(fig,out,'08_feature_importance')
    fig,ax=plt.subplots(figsize=(7,4.5))
    for label,color in [(0,blue),(1,orange)]: ax.hist(p[y==label],bins=np.linspace(0,1,41),density=True,histtype='step',lw=2,color=color,label=f'TARGET = {label}')
    ax.set(xlabel='Predicted probability',ylabel='Within-class density',title='Overlapping score distributions');ax.legend();save_plot(fig,out,'09_score_distributions')
    source_paths=[source,inp/'model_summary.csv',inp/'cv_results.csv',inp/'feature_importance.csv',inp/'final_model_config.json']
    provenance=dict(source_repository='https://github.com/slowdowndown/msdm5054-home-credit',
        source_commit='7dd0957906a3a67b8f8a77f2b0a8188c80944675',
        sha256={str(q.relative_to(root)):hashlib.sha256(q.read_bytes()).hexdigest() for q in source_paths},
        python=platform.python_version(),packages={x:importlib.metadata.version(x) for x in ['numpy','pandas','scikit-learn','matplotlib']},
        id_alignment='Unique IDs verified; canonical split membership and true-label alignment need raw data, absent from archive.',
        evaluation_context=CONTEXT,raw_feature_error_analysis='Not performed: raw application table unavailable.',
        shap='Not performed: optional; serialized model lacks fitted preprocessing and matching input matrix.')
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    return metrics

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--bootstrap',type=int,default=500)
    args=parser.parse_args()
    if args.bootstrap < 100: parser.error('Use at least 100 bootstrap replicates')
    print(json.dumps(run(args.root,args.bootstrap),indent=2))
