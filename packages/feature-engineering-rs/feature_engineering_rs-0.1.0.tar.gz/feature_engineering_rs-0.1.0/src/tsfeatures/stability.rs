use std::collections::HashMap;

use crate::helpers::common::mean_f;

pub fn stability(x: &[f64], freq: Option<usize>) -> f64 {
    let width = if freq == Some(1) { 10 } else { freq.unwrap_or(1) };
    let nr = x.len();
    
    if nr < 2 * width {
        return 0.0;
    }

    let nsegs = nr / width;
    let mut means = Vec::with_capacity(nsegs);

    for i in 0..nsegs {
        let start = i * width;
        let end = (start + width).min(nr);
        let segment = &x[start..end];
        
        // Filter out NaN values and use the stats::mean function
        let valid_values: Vec<f64> = segment.iter()
            .filter(|&&val| !val.is_nan())
            .copied()
            .collect();
        
        let mean_val = if !valid_values.is_empty() {
            mean_f(&valid_values)
        } else {
            f64::NAN
        };
        means.push(mean_val);
    }
    
    let stability = variance(&means);
    
    stability
}

fn variance(data: &[f64]) -> f64 {
    let n = data.len() as f64;
    if n <= 1.0 {
        return 0.0;
    }
    
    let mean_val = mean_f(data);
    let sum_sq_diff: f64 = data.iter()
        .map(|&x| (x - mean_val).powi(2))
        .sum();
    
    sum_sq_diff / (n - 1.0) // ddof=1 equivalent
}