"""Set-independent entry point. Caller supplies demand, policy candidates, payer.
No set identifier influences eligibility, priority, preferences or capacity.
"""
from CommonEndOfLife import calculate

def run_common(year, demand, policy, financing, payer_calculator=None):
 inputs=dict(demand)
 if payer_calculator is not None:inputs['payer_calculator']=payer_calculator
 return calculate(year,inputs,policy,financing)
