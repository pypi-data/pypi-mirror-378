use super::common::*;
use rayon::prelude::*;
use std::collections::HashMap;

// Import all catch22 feature structs
use super::catch22::{
    DNHistogramMode5, DNHistogramMode10, COF1ecac, COFirstMinAC, COHistogramAMIEven25,
    COTrev1Num, MDHrvClassicPnn40, DNMean, DNSpreadStd, SBBinaryStatsMeanLongstretch1,
    SBBinaryStatsDiffLongsstretch0, SBTransitionMatrix3acSumdiagcov, PDPeriodicityWangTh001,
    COEmbed2DistTauDExpfitMeandiff, INAutoMutualInfoStats40GaussianFmmi,
    FCLocalSimpleMean1StderrTauresrat, FCLocalSimpleMean3Stderr, DNOutlierIncludeNP001Mdrmd,
    DNOutlierIncludeP001Mdrmd, SPSummariesWelchRectArea51, SBMotifThreeQuantileHH,
    SPSummariesWelchRectCentroid, SCFluctanal2Dfa5012LogiPropR1, SCFluctanal2Rsrangefit5012LogiPropR1
};

// Import all tsfeatures feature structs
use super::tsfeatures::{
    CrossingPoints, Entropy, FlatSpots, Lumpiness, Stability, Hurst, Nonlinearity,
    XPacf5, Diff1XPacf5, Diff2XPacf5, SeasPacf, UnitrootKpss, UnitrootPp, ArchStat
};

/// Combined output type
pub type CombinedOutput = FeatureOutput;

// Add this macro at the top of the file
macro_rules! boxed_features {
    ($($feature:expr),* $(,)?) => {
        vec![$(Box::new($feature) as Box<dyn FeatureCompute>),*]
    };
}

/// Parameters for combined feature computation
#[derive(Debug, Clone)]
pub struct CombinedParams {
    pub normalize: bool,
    pub catch24: bool,
    pub freq: Option<usize>,
    pub lags: usize,
    pub demean: bool,
}

impl Default for CombinedParams {
    fn default() -> Self {
        Self {
            normalize: true,
            catch24: false,
            freq: None,
            lags: 12,
            demean: true,
        }
    }
}

/// Compute all features (catch22 + tsfeatures) in parallel
pub fn compute_combined_parallel(y: Vec<f64>, params: CombinedParams) -> CombinedOutput {
    let mut features: Vec<Box<dyn FeatureCompute>> = Vec::new();

    // Add all catch22 features
    features.extend(boxed_features![
        DNHistogramMode5,
        DNHistogramMode10,
        COF1ecac,
        COFirstMinAC,
        COHistogramAMIEven25,
        COTrev1Num,
        MDHrvClassicPnn40,
        SBBinaryStatsMeanLongstretch1,
        SBTransitionMatrix3acSumdiagcov,
        PDPeriodicityWangTh001,
        COEmbed2DistTauDExpfitMeandiff,
        INAutoMutualInfoStats40GaussianFmmi,
        FCLocalSimpleMean1StderrTauresrat,
        DNOutlierIncludeP001Mdrmd,
        DNOutlierIncludeNP001Mdrmd,
        SPSummariesWelchRectArea51,
        SBBinaryStatsDiffLongsstretch0,
        SBMotifThreeQuantileHH,
        SCFluctanal2Rsrangefit5012LogiPropR1,
        SCFluctanal2Dfa5012LogiPropR1,
        SPSummariesWelchRectCentroid,
        FCLocalSimpleMean3Stderr,
    ]);

    // Add catch24 features if requested
    if params.catch24 {
        features.extend(boxed_features![DNMean, DNSpreadStd]);
    }

    // Add all TSFeatures
    features.extend(boxed_features![
        CrossingPoints,
        FlatSpots,
        Lumpiness { freq: params.freq },
        Stability { freq: params.freq },
        XPacf5 { freq: params.freq },
        Diff1XPacf5 { freq: params.freq },
        Diff2XPacf5 { freq: params.freq },
        Hurst,
        UnitrootPp,
        UnitrootKpss,
        Nonlinearity,
        ArchStat { lags: params.lags, demean: params.demean },
        Entropy,
    ]);

    // Add SeasPacf only if freq > 1
    if let Some(f) = params.freq {
        if f > 1 {
            features.extend(boxed_features![SeasPacf { freq: params.freq }]);
        }
    }

    compute_features_parallel_dyn(y, params.normalize, features)
}


/// Extract combined features cumulatively
pub fn extract_combined_features_cumulative_optimized(
    series: &[f64],
    params: CombinedParams,
    value_column_name: Option<&str>,
) -> CumulativeResult {
    extract_features_cumulative_optimized(
        series,
        params.normalize,
        value_column_name,
        |data, norm| {
            let mut combined_params = params.clone();
            combined_params.normalize = norm;
            compute_combined_parallel(data.to_vec(), combined_params)
        },
    )
}
