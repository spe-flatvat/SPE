"""Read-only policy-review indicators; no admission or fiscal decisions."""
def population_band(ratio):
 return 'BELOW_3' if ratio<.03 else 'ABOVE_5' if ratio>.05 else 'WITHIN_3_TO_5'
def below_population_threshold(population):return population<100000000
def observe(year,foreign,population,reference,policy_delta,foreign_effective,foreign_jobs,program_base_trn,nominal_reference_trn,price_reference,VA_yen,labor_cost_yen,state):
 ratio=foreign/population;band=population_band(ratio);outside=band!='WITHIN_3_TO_5';low=below_population_threshold(population)
 state['outside_streak']=state.get('outside_streak',0)+1 if outside else 0
 state['band_streak']=state.get('band_streak',0)+1 if state.get('last_band')==band else 1;state['last_band']=band
 state['below100_streak']=state.get('below100_streak',0)+1 if low else 0
 if outside:state.setdefault('first_population_deviation_year',year)
 if low:state.setdefault('first_below100_year',year)
 state['outside_total']=state.get('outside_total',0)+int(outside)
 # These are inherited reference diagnostics, never the undefined formal GDP ratio.
 va_trn=foreign_effective*VA_yen*price_reference/1e12
 labor_trn=foreign_jobs*labor_cost_yen*price_reference/1e12
 program_trn=program_base_trn*price_reference
 return dict(year=year,foreign_resident_numerator=foreign,total_population_denominator=population,population_ratio=ratio,population_ratio_scope='all model foreign residents, not just F target workforce',population_band=band,population_review_flag=outside,population_first_deviation_year=state.get('first_population_deviation_year'),consecutive_outside_years=state['outside_streak'],consecutive_band_years=state['band_streak'],cumulative_outside_years=state['outside_total'],below100_review_flag=low,below100_first_year=state.get('first_below100_year'),below100_consecutive_years=state['below100_streak'],relaxation_candidate_pct=20 if low else None,actual_admission_adjustment=0,actual_relaxation_multiplier=1.0,actual_fiscal_savings_trn=0.,gdp_formal_ratio=None,gdp_formal_review_flag=None,gdp_formal_status='N/A_UNDEFINED_NUMERATOR_DENOMINATOR_TIME_SCOPE',proxy_reference_GDP_trn=nominal_reference_trn,proxy_reference_price_factor=price_reference,proxy_GDP_definition='pinned prior FTE F nominal GDP, lagged one year; 2026 uses initial anchor; not current-year warning-F GDP',proxy_VA_numerator_trn=va_trn,proxy_VA_ratio=va_trn/nominal_reference_trn,proxy_VA_above5_reference_only=va_trn/nominal_reference_trn>.05,proxy_labor_numerator_trn=labor_trn,proxy_labor_ratio=labor_trn/nominal_reference_trn,proxy_labor_above5_reference_only=labor_trn/nominal_reference_trn>.05,proxy_program_numerator_trn=program_trn,proxy_program_ratio=program_trn/nominal_reference_trn,proxy_program_above5_reference_only=program_trn/nominal_reference_trn>.05,proxy_status='NON_ADOPTED_REFERENCE_ONLY; national VA/labor-cost assumptions, limited targeted-program costs',foreign_reference_stock=reference,foreign_F_policy_stock_delta=policy_delta,reference_stock_contribution_ratio=reference/population,F_policy_stock_contribution_ratio=policy_delta/population,post2030_review_candidate=year>=2030 and (outside or low),review_candidate_categories='受入支援制度等の妥当性・公平性・費用対効果の検討候補（制度の存在・優遇性・効果は未認定）' if outside or low else '',policy_change_adopted=False)
