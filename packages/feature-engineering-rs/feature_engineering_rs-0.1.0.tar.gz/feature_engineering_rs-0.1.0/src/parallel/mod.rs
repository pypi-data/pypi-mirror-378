//! Parallel processing modules for different feature sets

pub mod common;
pub mod catch22;
pub mod tsfeatures;
pub mod combined;

// Re-export commonly used items
pub use common::*;
pub use catch22::{compute_catch22_parallel, extract_catch22_features_cumulative_optimized, Catch22Output};
pub use tsfeatures::{compute_tsfeatures_parallel, extract_tsfeatures_cumulative_optimized, TSFeaturesOutput};
pub use combined::{
    compute_combined_parallel, 
    extract_combined_features_cumulative_optimized,
    CombinedOutput,
    CombinedParams
};