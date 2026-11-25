"""Isolated N3 allocation adapter using the previous dynamic runtime."""
import importlib.util
import types


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def replace(s, old, new):
    if s.count(old)!=1:
        raise ValueError(old)
    return s.replace(old,new)


def run(root, work, runtime, capture, sq, native, prices, fixed, rate, route, authorized=False):
    """Reduce only the modeled cash surplus redemption slice, in a sealed case."""
    ledger = {}
    g_fraction, i_fraction = {"G":(1.,0.),"I":(0.,1.),"MIX":(.5,.5),"HOLD":(0.,0.)}[route]

    def setup(runner, settings):
        settings.update(g_share=g_fraction,pi_share=i_fraction)
        template = runner.resolved_runtime
        start = template.index("  room=max(0.,self.primary[y])")
        end = template.index("g=z['g'];pubI=z['pi'];spend=z['spend'];Y=z['Y'];nom=z['nom'];tax=z['tax'];pb=z['pbpre']-spend",start)
        template = (template[:start]+
                    "  z,room=self.allocate(s,y,evalroom,interest,sfa,assets,debt);"+
                    template[end:])
        template = replace(template,
            "fin=self.fp.finance(debt,assets,pb-cash_cost+self.other_sale,interest,remaining_sfa,s['rollover'])",
            "fin=self.allocate_finance(s,y,debt,assets,pb-cash_cost+self.other_sale,interest,remaining_sfa)")
        namespace = dict(runner.simulate.__func__.__globals__)
        exec(compile(template,"isolated_redemption_allocation","exec"),namespace)
        runner.simulate = types.MethodType(namespace["simulate"],runner)

        def allocate(self,s,y,evaluate,interest,sfa,assets,debt):
            # Unspent assets and SFA cannot authorize a release. The pre-spend
            # calculation uses this case's carried state, excluding its own-year
            # induced tax improvement from the amount available for spending.
            zero = evaluate(0.)
            baseline = fixed[y]
            planned = float(baseline["CL_cash_redemption_trn"])
            live_fin = self.fp.finance(debt,0.,zero["pbpre"]-self.cash_part(s,y,sfa),
                                       interest,sfa-self.cash_part(s,y,sfa),s["rollover"])
            live = min(debt,live_fin["CL_cash_surplus_debt_redemption_candidate_trn"])
            requested = planned*rate
            modeled_eligible = min(planned,max(0.,live))
            amount = min(requested,modeled_eligible*rate)
            if authorized or y==2026:
                amount=0.
            # The inherited G/I evaluator applies domestic shares, I smoothing,
            # supply and nominal tax. Independent spending ceilings are required
            # because each activity owns only its assigned part of the envelope.
            self.authority_cap = lambda ss, yy, k: amount*(g_fraction if k=="G" else i_fraction)
            solved=evaluate(amount)
            solved,room=self.finalize_room(s,y,solved,amount,evaluate,interest,sfa,assets)
            solved["budget"]=amount
            self.ck(f"resource_ceiling:{y}",max(0.,solved["spend"]-amount))
            self.ck(f"G_ceiling:{y}",max(0.,solved["g"]-amount*g_fraction))
            self.ck(f"I_ceiling:{y}",max(0.,solved["pipay"]-amount*i_fraction))
            ledger[y] = dict(year=y,reference_planned_cash_redemption_trn=planned,
                             reference_planned_gross_redemption_trn=float(baseline["CL_assumed_gross_redemption_trn"]),
                             requested_cut_trn=requested,live_no_spend_cash_redemption_trn=live,
                             modeled_slice_trn=modeled_eligible,confirmed_authority_trn=0.,
                             released_hypothetical_cash_trn=amount,spending_G_nominal_trn=solved["g"],
                             spending_I_nominal_trn=solved["pipay"],unallocated_retained_trn=amount-solved["spend"],
                             requested_unavailable_trn=requested-amount,
                             extra_same_year_tax_vs_no_spend_trn=solved["tax"]-zero["tax"],
                             no_spend_cash_borrowing_trn=live_fin["CL_new_cash_borrowing_candidate_trn"],
                             no_spend_tax_trn=zero["tax"])
            return solved,room

        def allocate_finance(self,s,y,debt,assets,pb,interest,sfa):
            frozen = ledger[y]
            held = frozen["unallocated_retained_trn"]
            # Run the existing cash-finance rule over the allocated budget only.
            # Park unused released cash as a separately visible addition inside
            # the same candidate asset account; the sale/transfer assumptions stay off.
            result = self.fp.finance(debt,assets,pb-held,interest,sfa,s["rollover"])
            result["CL_cash_asset_addition_candidate_trn"]+=held
            result["CL_cash_assets_end_candidate_trn"]+=held
            result["CL_PB_candidate_trn"]=pb
            result["CL_balance_candidate_trn"]=pb-interest
            result["CL_cash_financing_need_trn"]=interest-pb
            self.ck(f"allocation_identity:{y}",frozen["released_hypothetical_cash_trn"]-
                    frozen["spending_G_nominal_trn"]-frozen["spending_I_nominal_trn"]-held)
            if frozen["released_hypothetical_cash_trn"]>0:
                self.ck(f"no_spending_funded_by_cash_borrowing:{y}",
                        result["CL_new_cash_borrowing_candidate_trn"])
            frozen["actual_rollover_trn"]=result["CL_scheduled_refinancing_assumption_trn"]
            frozen["actual_cash_redemption_trn"]=result["CL_cash_surplus_debt_redemption_candidate_trn"]
            frozen["gross_redemption_trn"]=result["CL_gross_redemption_with_assumed_refinancing_trn"]
            frozen["gross_issue_trn"]=result["CL_gross_issue_with_assumed_refinancing_trn"]
            frozen["actual_net_redemption_reduction_vs_no_spend_trn"]=(
                frozen["live_no_spend_cash_redemption_trn"]-frozen["actual_cash_redemption_trn"])
            return result

        runner.allocate = types.MethodType(allocate,runner)
        runner.allocate_finance = types.MethodType(allocate_finance,runner)

    # Use the already validated C/D builder. The isolated callback captures
    # its runner immediately before execution and after all fixed inputs are set.
    source = runtime.read_text(encoding="utf-8")
    source = replace(source,"    annual, fiscal, bridge = runner.simulate(settings)",
                     "    _allocation_setup(runner, settings)\n    annual, fiscal, bridge = runner.simulate(settings)")
    ns={"__name__":"dynamic_redemption_basis","_allocation_setup":setup}
    exec(compile(source,str(runtime),"exec"),ns)
    result=ns["run_n3"](root,work,capture,sq,native,prices)
    return (*result,ledger)
