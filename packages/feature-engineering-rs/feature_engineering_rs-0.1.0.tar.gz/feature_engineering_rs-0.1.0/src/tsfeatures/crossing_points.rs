use crate::helpers::common::median_f;

pub fn crossing_points(series: &[f64]) -> f64 {
    
    if series.len() < 2 {
        return 0.0;
    }
    
    let median = median_f(series, Some(false));
    
    // Count crossings using iterator methods
    let ab: Vec<bool> = series.iter()
        .map(|&x| !x.is_nan() && !median.is_nan() && x <= median)
        .collect();
    
    ab.windows(2)
        .filter(|w| w[0] != w[1])
        .count() as f64
}
