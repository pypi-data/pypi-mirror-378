use pyo3::prelude::*;
use std::collections::HashMap;

pub mod helpers;
pub mod catch22;
pub mod tsfeatures;
pub mod parallel;

// Individual function imports for direct use in Python bindings
use catch22::co_auto_corr::{
    co_embed2_dist_tau_d_expfit_meandiff, co_f1ecac, co_first_min_ac, co_histogramami_even_2_5,
    co_trev_1_num,
};
use catch22::dn_histogrammode_10::dn_histogrammode_10;
use catch22::dn_histogrammode_5::dn_histogrammode_5;
use catch22::dn_mean::dn_mean;
use catch22::dn_outlierinclude::{dn_outlierinclude_n_001_mdrmd, dn_outlierinclude_p_001_mdrmd};
use catch22::dn_spread_std::dn_spread_std;
use catch22::fc_localsimple::{fc_localsimple_mean1_tauresrat, fc_localsimple_mean3_stderr};
use catch22::in_automutualinfostats::in_automutualinfostats_40_gaussian_fmmi;
use catch22::md_hrv::md_hrv_classic_pnn40;
use catch22::pd_periodicitywang::pd_periodicitywang;
use catch22::sb_binarystats::{
    bin_binarystats_diff_longsstretch0, bin_binarystats_mean_longstretch1,
};
use catch22::sb_motifthree::sb_motifthree_quantile_hh;
use catch22::sb_transitionmatrix::sb_transitionmatrix_3ac_sumdiagcov;
use catch22::sc_fluctanal::{
    sc_fluctanal_2_dfa_50_1_2_logi_prop_r1, sc_fluctanal_2_rsrangefit_50_1_2_logi_prop_r1,
};
use catch22::sp_summaries::{sp_summaries_welch_rect_area_5_1, sp_summaries_welch_rect_centroid};
use parallel::catch22::{compute_catch22_parallel, extract_catch22_features_cumulative_optimized};

// Import TSFeatures functions
use tsfeatures::crossing_points::crossing_points;
use tsfeatures::entropy::entropy;
use tsfeatures::flat_spots::flat_spots;
use tsfeatures::lumpiness::lumpiness;
use tsfeatures::stability::stability;
use tsfeatures::hurst::hurst;
use tsfeatures::nonlinearity::nonlinearity;
use tsfeatures::pacf::pacf_features;
use tsfeatures::unitroot_kpss::unitroot_kpss;
use tsfeatures::unitroot_pp::unitroot_pp;
use tsfeatures::arch_stat::arch_stat;

// Import TSFeatures parallel functions
use parallel::tsfeatures::{compute_tsfeatures_parallel, extract_tsfeatures_cumulative_optimized};

// Import combined functions
use parallel::combined::{compute_combined_parallel, extract_combined_features_cumulative_optimized, CombinedParams};
#[pyclass]
pub struct Catch22Result {
    #[pyo3(get)]
    pub names: Vec<String>,
    #[pyo3(get)]
    pub values: Vec<f64>,
}

#[pyclass]
pub struct TSFeaturesResult {
    #[pyo3(get)]
    pub names: Vec<String>,
    #[pyo3(get)]
    pub values: Vec<f64>,
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None, catch24=None))]
fn catch22_all_f(y: Vec<f64>, normalize: Option<bool>, catch24: Option<bool>) -> Catch22Result {
    
    let result = compute_catch22_parallel(y, normalize.unwrap_or(true), catch24.unwrap_or(false));

    Catch22Result {
        names: result.names,
        values: result.values,
    }
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn co_trev_1_num_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    co_trev_1_num(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn co_f1ecac_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    co_f1ecac(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn co_first_min_ac_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    co_first_min_ac(&y, use_normalization) as f64
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn co_histogramami_even_2_5_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    co_histogramami_even_2_5(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn dn_histogrammode_5_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    dn_histogrammode_5(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn dn_histogrammode_10_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    dn_histogrammode_10(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn md_hrv_classic_pnn40_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    md_hrv_classic_pnn40(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn sb_binarystats_diff_longsstretch0_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    bin_binarystats_diff_longsstretch0(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn sb_transitionmatrix_3ac_sumdiagcov_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    sb_transitionmatrix_3ac_sumdiagcov(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn sb_binarystats_mean_longstretch1_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    bin_binarystats_mean_longstretch1(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn pd_periodicitywang_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    pd_periodicitywang(&y, use_normalization) as f64
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn co_embed2_dist_tau_d_expfit_meandiff_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    co_embed2_dist_tau_d_expfit_meandiff(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn in_automutualinfostats_40_gaussian_fmmi_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    in_automutualinfostats_40_gaussian_fmmi(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn fc_localsimple_mean1_tauresrat_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    fc_localsimple_mean1_tauresrat(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn fc_localsimple_mean3_stderr_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    fc_localsimple_mean3_stderr(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn dn_outlierinclude_p_001_mdrmd_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    dn_outlierinclude_p_001_mdrmd(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn dn_outlierinclude_n_001_mdrmd_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    dn_outlierinclude_n_001_mdrmd(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn sp_summaries_welch_rect_area_5_1_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    sp_summaries_welch_rect_area_5_1(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn sp_summaries_welch_rect_centroid_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    sp_summaries_welch_rect_centroid(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn sb_motifthree_quantile_hh_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    sb_motifthree_quantile_hh(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn sc_fluctanal_2_dfa_50_1_2_logi_prop_r1_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    sc_fluctanal_2_dfa_50_1_2_logi_prop_r1(&y, 2, "dfa", use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn sc_fluctanal_2_rsrangefit_50_1_2_logi_prop_r1_f(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    sc_fluctanal_2_rsrangefit_50_1_2_logi_prop_r1(&y, 1, "rsrangefit", use_normalization)
}

#[pyfunction]
fn dn_mean_f(y: Vec<f64>) -> f64 {
    dn_mean(&y)
}

#[pyfunction]
fn dn_spread_std_f(y: Vec<f64>) -> f64 {
    dn_spread_std(&y)
}

// Add this new PyClass for the cumulative result
#[pyclass]
#[derive(Debug, Clone)]
pub struct CumulativeFeatures {
    #[pyo3(get)]
    pub feature_names: Vec<String>,
    #[pyo3(get)]
    pub values: Vec<Vec<f64>>,
}

// Add this Python function
#[pyfunction]
#[pyo3(signature = (series, normalize=None, catch24=None, value_column_name=None))]
fn extract_catch22_features_cumulative_f(
    series: Vec<f64>, 
    normalize: Option<bool>, 
    catch24: Option<bool>,
    value_column_name: Option<String>
) -> CumulativeFeatures {
    let normalize = normalize.unwrap_or(true);
    let catch24 = catch24.unwrap_or(false);
    
    let result = extract_catch22_features_cumulative_optimized(
        &series, 
        normalize, 
        catch24, 
        value_column_name.as_deref()
    );

    // Extract feature names from the first row (they should be consistent)
    let feature_names: Vec<String> = if let Some(first_row) = result.data.first() {
        let mut names: Vec<String> = first_row.keys().cloned().collect();
        names.sort(); // Ensure consistent ordering
        names
    } else {
        Vec::new()
    };
    
    // Extract values in the same order as feature names
    let values: Vec<Vec<f64>> = result.data.iter().map(|row| {
        feature_names.iter().map(|name| {
            row.get(name).copied().unwrap_or(f64::NAN)
        }).collect()
    }).collect();
    
    CumulativeFeatures {
        feature_names,
        values,
    }
}

// TSFeatures Python bindings
#[pyfunction]
fn crossing_points_f(y: Vec<f64>) -> f64 {
    crossing_points(&y)
}

#[pyfunction]
fn entropy_f(y: Vec<f64>) -> f64 {
    entropy(&y)
}

#[pyfunction]
fn flat_spots_f(y: Vec<f64>) -> f64 {
    flat_spots(&y)
}

#[pyfunction]
#[pyo3(signature = (y, freq=1))]
fn lumpiness_f(y: Vec<f64>, freq: Option<usize>) -> f64 {
    lumpiness(&y, freq)
}

#[pyfunction]
#[pyo3(signature = (y, freq=1))]
fn stability_f(y: Vec<f64>, freq: Option<usize>) -> f64 {
    stability(&y, freq)
}

#[pyfunction]
#[pyo3(signature = (y))]
fn hurst_f(y: Vec<f64>) -> f64 {
    hurst(&y)
}

#[pyfunction]
#[pyo3(signature = (y))]
fn nonlinearity_f(y: Vec<f64>) -> f64 {
    nonlinearity(y)
}

#[pyfunction]
#[pyo3(signature = (y, freq=1))]
fn pacf_features_f(y: Vec<f64>, freq: Option<usize>) -> HashMap<String, f64> {
    pacf_features(y, freq)
}

#[pyfunction]
#[pyo3(signature = (y, freq=1))]
fn unitroot_kpss_f(y: Vec<f64>, freq: i32) -> f64 {
    unitroot_kpss(&y, freq)
}

#[pyfunction]
#[pyo3(signature = (y, freq=1))]
fn unitroot_pp_f(y: Vec<f64>, freq: i32) -> f64 {
    unitroot_pp(&y, freq)
}

#[pyfunction]
#[pyo3(signature = (y, lags=12, demean=true))]
fn arch_stat_f(y: Vec<f64>, lags: usize, demean: bool) -> f64 {
    arch_stat(&y, lags, demean)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None, freq=1, lags=12, demean=true))]
fn tsfeatures_all_f(y: Vec<f64>, normalize: Option<bool>, freq: Option<usize>, lags: usize, demean: bool) -> TSFeaturesResult {
    let result = compute_tsfeatures_parallel(y, normalize.unwrap_or(false), freq, lags, demean);
    
    TSFeaturesResult {
        names: result.names,
        values: result.values,
    }
}

#[pyfunction]
#[pyo3(signature = (series, normalize=None, freq=None, lags=12, demean=true, value_column_name=None))]
fn extract_tsfeatures_cumulative_f(
    series: Vec<f64>, 
    normalize: Option<bool>, 
    freq: Option<usize>,
    lags: usize,
    demean: bool,
    value_column_name: Option<String>
) -> CumulativeFeatures {
    let normalize = normalize.unwrap_or(false);
    
    let result = extract_tsfeatures_cumulative_optimized(
        &series, 
        normalize, 
        freq,
        lags,
        demean,
        value_column_name.as_deref()
    );

    let feature_names: Vec<String> = if let Some(first_row) = result.data.first() {
        let mut names: Vec<String> = first_row.keys().cloned().collect();
        names.sort();
        names
    } else {
        Vec::new()
    };
    
    let values: Vec<Vec<f64>> = result.data.iter().map(|row| {
        feature_names.iter().map(|name| {
            row.get(name).copied().unwrap_or(f64::NAN)
        }).collect()
    }).collect();
    
    CumulativeFeatures {
        feature_names,
        values,
    }
}

// Add this new result class after TSFeaturesResult around line 64
#[pyclass]
pub struct CombinedResult {
    #[pyo3(get)]
    pub names: Vec<String>,
    #[pyo3(get)]
    pub values: Vec<f64>,
}

// Add this function after extract_tsfeatures_cumulative_f around line 407
#[pyfunction]
#[pyo3(signature = (y, normalize=None, catch24=None, freq=None, lags=12, demean=true))]
fn combined_all_f(
    y: Vec<f64>, 
    normalize: Option<bool>, 
    catch24: Option<bool>, 
    freq: Option<usize>, 
    lags: usize, 
    demean: bool
) -> CombinedResult {
    let result = compute_combined_parallel(
        y, 
        CombinedParams {
            normalize: normalize.unwrap_or(true),
            catch24: catch24.unwrap_or(false),
            freq,
            lags,
            demean,
        }
    );
    
    CombinedResult {
        names: result.names,
        values: result.values,
    }
}

#[pyfunction]
#[pyo3(signature = (series, normalize=None, catch24=None, freq=None, lags=12, demean=true, value_column_name=None))]
fn extract_combined_features_cumulative_f(
    series: Vec<f64>, 
    normalize: Option<bool>, 
    catch24: Option<bool>,
    freq: Option<usize>,
    lags: usize,
    demean: bool,
    value_column_name: Option<String>
) -> CumulativeFeatures {
    let normalize = normalize.unwrap_or(true);
    let catch24 = catch24.unwrap_or(false);
    
    let result = extract_combined_features_cumulative_optimized(
        &series,
        CombinedParams {
            normalize,
            catch24,
            freq,
            lags,
            demean,
        },
        value_column_name.as_deref()
    );

    let feature_names: Vec<String> = if let Some(first_row) = result.data.first() {
        let mut names: Vec<String> = first_row.keys().cloned().collect();
        names.sort();
        names
    } else {
        Vec::new()
    };
    
    let values: Vec<Vec<f64>> = result.data.iter().map(|row| {
        feature_names.iter().map(|name| {
            row.get(name).copied().unwrap_or(f64::NAN)
        }).collect()
    }).collect();
    
    CumulativeFeatures {
        feature_names,
        values,
    }
}

#[pymodule]
fn feature_engineering_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Catch22 + DNMean + DNSpreadStd
    m.add_class::<Catch22Result>()?;
    m.add_class::<CumulativeFeatures>()?;
    m.add_function(wrap_pyfunction!(catch22_all_f, m)?)?;
    m.add_function(wrap_pyfunction!(co_trev_1_num_f, m)?)?;
    m.add_function(wrap_pyfunction!(dn_histogrammode_10_f, m)?)?;
    m.add_function(wrap_pyfunction!(dn_histogrammode_5_f, m)?)?;
    m.add_function(wrap_pyfunction!(co_f1ecac_f, m)?)?;
    m.add_function(wrap_pyfunction!(co_first_min_ac_f, m)?)?;
    m.add_function(wrap_pyfunction!(co_histogramami_even_2_5_f, m)?)?;
    m.add_function(wrap_pyfunction!(md_hrv_classic_pnn40_f, m)?)?;
    m.add_function(wrap_pyfunction!(dn_mean_f, m)?)?;
    m.add_function(wrap_pyfunction!(dn_spread_std_f, m)?)?;
    m.add_function(wrap_pyfunction!(sb_binarystats_diff_longsstretch0_f, m)?)?;
    m.add_function(wrap_pyfunction!(sb_binarystats_mean_longstretch1_f, m)?)?;
    m.add_function(wrap_pyfunction!(sb_transitionmatrix_3ac_sumdiagcov_f, m)?)?;
    m.add_function(wrap_pyfunction!(pd_periodicitywang_f, m)?)?;
    m.add_function(wrap_pyfunction!(co_embed2_dist_tau_d_expfit_meandiff_f,m)?)?;
    m.add_function(wrap_pyfunction!(in_automutualinfostats_40_gaussian_fmmi_f,m)?)?;
    m.add_function(wrap_pyfunction!(fc_localsimple_mean1_tauresrat_f, m)?)?;
    m.add_function(wrap_pyfunction!(fc_localsimple_mean3_stderr_f, m)?)?;
    m.add_function(wrap_pyfunction!(dn_outlierinclude_p_001_mdrmd_f, m)?)?;
    m.add_function(wrap_pyfunction!(dn_outlierinclude_n_001_mdrmd_f, m)?)?;
    m.add_function(wrap_pyfunction!(sp_summaries_welch_rect_area_5_1_f, m)?)?;
    m.add_function(wrap_pyfunction!(sp_summaries_welch_rect_centroid_f, m)?)?;
    m.add_function(wrap_pyfunction!(sb_motifthree_quantile_hh_f, m)?)?;
    m.add_function(wrap_pyfunction!(sc_fluctanal_2_dfa_50_1_2_logi_prop_r1_f,m)?)?;
    m.add_function(wrap_pyfunction!(sc_fluctanal_2_rsrangefit_50_1_2_logi_prop_r1_f,m)?)?;
    m.add_function(wrap_pyfunction!(extract_catch22_features_cumulative_f, m)?)?;
    
    // TSFeatures
    m.add_class::<TSFeaturesResult>()?;
    m.add_function(wrap_pyfunction!(crossing_points_f, m)?)?;
    m.add_function(wrap_pyfunction!(entropy_f, m)?)?;
    m.add_function(wrap_pyfunction!(flat_spots_f, m)?)?;
    m.add_function(wrap_pyfunction!(lumpiness_f, m)?)?;
    m.add_function(wrap_pyfunction!(stability_f, m)?)?;
    m.add_function(wrap_pyfunction!(hurst_f, m)?)?;
    m.add_function(wrap_pyfunction!(nonlinearity_f, m)?)?;
    m.add_function(wrap_pyfunction!(pacf_features_f, m)?)?;
    m.add_function(wrap_pyfunction!(unitroot_kpss_f, m)?)?;
    m.add_function(wrap_pyfunction!(unitroot_pp_f, m)?)?;
    m.add_function(wrap_pyfunction!(arch_stat_f, m)?)?;
    m.add_function(wrap_pyfunction!(tsfeatures_all_f, m)?)?;
    m.add_function(wrap_pyfunction!(extract_tsfeatures_cumulative_f, m)?)?;

    // Combined Features
    m.add_class::<CombinedResult>()?;
    m.add_function(wrap_pyfunction!(combined_all_f, m)?)?;
    m.add_function(wrap_pyfunction!(extract_combined_features_cumulative_f, m)?)?;
    
    Ok(())
}