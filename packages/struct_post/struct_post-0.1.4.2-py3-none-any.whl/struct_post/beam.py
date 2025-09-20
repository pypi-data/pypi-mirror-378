import pandas as pd
def four_point_bending (data: pd.DataFrame, 
                        width: float, 
                        depth: float, 
                        beam_span: float):
    import pandas as pd
    import numpy as np

    #geo
    sample_name = data[1]
    force = data[0]['Moog Force_kN'] * 1000
    delta_1 = abs(data[0]['LVDT 1_mm'])
    delta_2 = abs(data[0]['LVDT 2_mm'])
    delta_3 = abs(data[0]['LVDT 3_mm'])
    delta_4 = abs(data[0]['LVDT 4_mm'])
    delta_5 = abs(data[0]['LVDT 5_mm'])
    delta_6 = abs(data[0]['LVDT 6_mm'])

    F_ult = force.max()
    f_b = (F_ult * beam_span) / (width * depth **2) #MPa

    
    delta_ms = (delta_3 + delta_4)/2
    delta_rel = delta_ms - (delta_1 + delta_2 + delta_5 + delta_6) / 4
    
    
    lower_bound = 0.1 * F_ult
    upper_bound = 0.4 * F_ult

    calcs_reg = (lower_bound <= force) & (force <= upper_bound)
    
    F_ms = force[calcs_reg]
    delta_ms_calcs = delta_ms[calcs_reg]
    delat_rel_calcs = delta_rel[calcs_reg]
    
    Delta_ms, intercept_ms = np.polyfit(delta_ms_calcs,F_ms,1)
    Delta_rel, intercept_rel = np.polyfit(delat_rel_calcs,F_ms,1)
    
    E_app = (23/108) * (beam_span/depth)**3 * Delta_ms * (1/width)
    E_true = (1/36) *  (beam_span/depth)**3 * Delta_rel * (1/width)
    
    results = {
        "E_app": E_app,
        "E_true": E_true,
    }

    print(f"Sample Name: {sample_name}")
    print('-' * 40)
    return sample_name, results
