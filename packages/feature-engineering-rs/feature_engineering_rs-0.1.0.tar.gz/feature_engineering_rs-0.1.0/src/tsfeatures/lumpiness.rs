use crate::helpers::common::nan_variance_f;

pub fn lumpiness(x: &[f64], freq: Option<usize>) -> f64 {
    // Handle edge cases
    if x.is_empty() {
        return f64::NAN;
    }
    
    // Determine window width
    let width = freq.unwrap_or(1);
    let width = if width == 1 { 10 } else { width };
    
    let nr = x.len();
    
    // If series is too short, return 0
    if nr < 2 * width {
        return 0.0;
    }
    
    // Create windows and calculate their variances
    let mut variances = Vec::new();
    let mut start = 0;
    
    while start + width <= nr {
        let window = &x[start..start + width];
        
        // Calculate variance using nanvar equivalent
        if window.len() > 1 {
            let var = nan_variance_f(window, 1);  
            if !var.is_nan() {
                variances.push(var);
            }
        }
        
        start += width;
    }
    
    // Calculate variance of the variances
    if variances.len() < 2 {
        0.0
    } else {
        nan_variance_f(&variances, 1)
    }
}

