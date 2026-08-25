# Differential Thomas certificates for the polynomial auxiliary system and
# the prolonged constant-field VFE.
#
# Tested with Maple 2022.0. Run from this directory with
#
#     maple -q thomas_certificates.mpl
#
# ell is represented by the dependent field L(r,z), together with L_r=L_z=0.
# This prevents the differential-algebra engine from silently treating ell as
# a generic nonzero coefficient. The complete polynomial closure is decomposed
# before the physical inequations are imposed.

restart:
interface(prettyprint=0):

Failures := 0:

canon := proc(expr)
    return simplify(normal(expand(expr)), symbolic);
end proc:

assertzero := proc(expr, tag::string)
    local res;
    global Failures;
    res := canon(expr);
    if res <> 0 then
        printf("FAIL: %s\nResidual: %a\n", tag, res);
        Failures := Failures+1;
        return NULL;
    end if;
    printf("PASS: %s\n", tag);
    return NULL;
end proc:

asserttrue := proc(condition, tag::string)
    global Failures;
    if not evalb(condition) then
        printf("FAIL: %s\n", tag);
        Failures := Failures+1;
        return NULL;
    end if;
    printf("PASS: %s\n", tag);
    return NULL;
end proc:

try
    with(DifferentialThomas):
    printf("PASS: DifferentialThomas package loaded\n"):
catch:
    printf("FAIL: DifferentialThomas package unavailable: %a\n",
           lastexception):
    error "DifferentialThomas is required for this certificate";
end try:

printf("Maple kernel version: %s\n", kernelopts(version)):

# ----------------------------------------------------------------------
# 1. Complete Thomas decomposition of the polynomial auxiliary closure.
# ----------------------------------------------------------------------

Ranking([r,z],[[F,y,eta],[L]]):

Eta := eta(r,z):
Y := y(r,z):
FF := F(r,z):
LL := L(r,z):

AuxAlgebraic := FF-2*Eta-LL*r^2*Y+LL*Eta^2/2:
LogR := Eta*diff(Y,r)-diff(Eta,r):
LogZ := Eta*diff(Y,z)-diff(Eta,z):
Harmonic := r*(diff(FF,r$2)+diff(FF,z$2))-diff(FF,r):
AuxA := 2*Eta+LL*r^2-LL*Eta^2:

AuxBase := [AuxAlgebraic=0,LogR=0,LogZ=0,Harmonic=0,
            diff(LL,r)=0,diff(LL,z)=0,r<>0]:

asserttrue(member(r<>0,AuxBase),
           "auxiliary input explicitly records the r<>0 base localization"):

try
    AuxAll := ThomasDecomposition(AuxBase):
catch:
    printf("FAIL: complete auxiliary Thomas decomposition raised %a\n",
           lastexception):
    error "auxiliary Thomas decomposition failed";
end try:

asserttrue(nops(AuxAll)=4,
           "complete auxiliary polynomial closure has four disjoint components"):

GenericCount := 0:
EllZeroCount := 0:
EtaZeroCount := 0:

for i to nops(AuxAll) do
    Eqs := Equations(AuxAll[i]):
    Ineqs := Inequations(AuxAll[i]):
    printf("AUXILIARY COMPONENT %d\n  equations: %a\n  inequations: %a\n",
           i,Eqs,Ineqs):

    if member(Eta<>0,Ineqs) and member(LL<>0,Ineqs)
       and member(AuxA<>0,Ineqs) then
        GenericCount := GenericCount+1:
        printf("  classification: nonzero-ell regular sheet\n"):
    elif member(LL=0,Eqs) and member(Eta<>0,Ineqs) then
        EllZeroCount := EllZeroCount+1:
        printf("  classification: ell=0 regular sheet\n"):
    elif member(Eta=0,Eqs) then
        EtaZeroCount := EtaZeroCount+1:
        printf("  classification: eta=0 polynomial closure (not the logarithmic chart)\n"):
    else
        printf("  classification: UNRECOGNIZED\n"):
    end if:
end do:

asserttrue(GenericCount=1,
           "exactly one nonzero-ell regular auxiliary component is present"):
asserttrue(EllZeroCount=1,
           "ell=0 is retained as its own regular auxiliary component"):
asserttrue(EtaZeroCount=2,
           "both eta=0 polynomial-closure components are retained"):

# Restrict the same input to each significant stratum. A fold equality on an
# open patch is stronger than meeting the fold along a curve.
AuxRegular := ThomasDecomposition(
    [op(AuxBase),Eta<>0,AuxA<>0]):
AuxFold := ThomasDecomposition(
    [op(AuxBase),Eta<>0,AuxA=0]):
AuxEtaZero := ThomasDecomposition(
    [op(AuxBase),Eta=0]):
AuxEllZero := ThomasDecomposition(
    [op(AuxBase),LL=0,Eta<>0]):

asserttrue(nops(AuxRegular)=2,
           "regular A<>0 restriction contains ell<>0 and ell=0 components"):
asserttrue(nops(AuxFold)=0,
           "physical eta<>0 fold-valued open system is inconsistent"):
asserttrue(nops(AuxEtaZero)=2,
           "eta=0 restriction reproduces both closure components"):
asserttrue(nops(AuxEllZero)=1,
           "explicit ell=0, eta<>0 restriction is consistent and unique"):

# The nonzero-ell regular component has the expected principal denominator.
for i to nops(AuxRegular) do
    Eqs := Equations(AuxRegular[i]):
    Ineqs := Inequations(AuxRegular[i]):
    if member(LL<>0,Ineqs) then
        EtaSolved := select(e -> evalb(lhs(e)=diff(Eta,r$2)),Eqs):
        asserttrue(nops(EtaSolved)=1,
                   "regular nonzero-ell Thomas component solves once for eta_rr"):
        if nops(EtaSolved)=1 then
            assertzero(denom(rhs(EtaSolved[1]))^2-(r*Eta*AuxA)^2,
                       "regular eta_rr denominator is r eta A_eta up to a nonzero constant unit"):
        end if:
    end if:
end do:

# ----------------------------------------------------------------------
# 2. Independent Thomas proof of the constant-field obstruction.
# ----------------------------------------------------------------------

Ranking([r,z],[[v],[Lc]]):

V := v(r,z):
LC := Lc(r,z):
Vr := diff(V,r):
Vz := diff(V,z):
Vrr := diff(V,r$2):
Vzz := diff(V,z$2):
Av := 2*V+LC*r*(1-V^2):

P := r^2*V*Av*(Vrr+Vzz)
     +r*V*(2*V+3*LC*r*(1-V^2))*Vr
     -LC*r^3*(1+V^2)*(Vr^2+Vz^2)
     +2*LC*r*V^2-2*V^3:

ConstBase := [P=0,Vr=0,Vz=0,
              diff(LC,r)=0,diff(LC,z)=0,r<>0]:

# This finite identity displays the compatibility calculation that the Thomas
# algorithm performs: the residual gives Q=0 under v<>0, and its first
# r-prolongation gives Lc=0, hence v=0.
ConstJetSub := {Vr=0,Vz=0,Vrr=0,Vzz=0,
                diff(LC,r)=0,diff(LC,z)=0}:
Qconstant := LC*r-V:
assertzero(subs(ConstJetSub,P)-2*V^2*Qconstant,
           "constant-field residual is 2 v^2 (Lc r-v)"):
assertzero(subs(ConstJetSub,diff(Qconstant,r))-LC,
           "first r-prolongation of Lc r-v gives Lc"):

ConstClosure := ThomasDecomposition(ConstBase):
printf("CONSTANT-FIELD POLYNOMIAL CLOSURE\n"):
for i to nops(ConstClosure) do
    printf("  component %d equations: %a\n",i,Equations(ConstClosure[i])):
    printf("  component %d inequations: %a\n",i,Inequations(ConstClosure[i])):
end do:

asserttrue(nops(ConstClosure)=2,
           "cleared constant-field closure has two ell branches"):

ConstZeroEllCount := 0:
ConstNonzeroEllCount := 0:
for i to nops(ConstClosure) do
    Eqs := Equations(ConstClosure[i]):
    Ineqs := Inequations(ConstClosure[i]):
    asserttrue(member(V=0,Eqs),
               sprintf("constant-field closure component %d has v=0",i)):
    if member(LC=0,Eqs) then
        ConstZeroEllCount := ConstZeroEllCount+1:
    elif member(LC<>0,Ineqs) then
        ConstNonzeroEllCount := ConstNonzeroEllCount+1:
    end if:
end do:

asserttrue(ConstZeroEllCount=1,
           "one denominator-critical component has ell=0 and v=0"):
asserttrue(ConstNonzeroEllCount=1,
           "one denominator-critical component has ell<>0 and v=0"):

ConstPhysical := ThomasDecomposition([op(ConstBase),V<>0]):
ConstRegular := ThomasDecomposition([op(ConstBase),V<>0,Av<>0]):
ConstFold := ThomasDecomposition([op(ConstBase),V<>0,Av=0]):
ConstEllZeroPhysical := ThomasDecomposition(
    [op(ConstBase),LC=0,V<>0]):

asserttrue(nops(ConstPhysical)=0,
           "physical nonzero constant-field system is inconsistent"):
asserttrue(nops(ConstRegular)=0,
           "physical regular constant-field branch is inconsistent"):
asserttrue(nops(ConstFold)=0,
           "physical fold constant-field branch is inconsistent"):
asserttrue(nops(ConstEllZeroPhysical)=0,
           "ell=0 does not rescue a nonzero constant field"):

# ----------------------------------------------------------------------
# 3. Symbol/rank certificate for the regular and fold jet strata.
# ----------------------------------------------------------------------

Principal := r^2*V*Av:
assertzero(coeff(P,Vrr)-Principal,
           "v_rr principal coefficient is r^2 v A_v"):
assertzero(coeff(P,Vzz)-Principal,
           "v_zz principal coefficient is r^2 v A_v"):
assertzero(coeff(P,diff(V,r,z)),
           "mixed v_rz principal coefficient vanishes"):

printf("SYMBOL INTERPRETATION: under r<>0 and v<>0, A_v<>0 gives the single trace equation h_rr+h_zz=0, so dim(g_2)=2; A_v=0 annihilates all three second-order coefficients, so dim(g_2)=3.\n"):
printf("REALITY NOTE: the generic Thomas component also prints 1+r^2 L^2<>0. This separant is automatic for real r and L, but it is retained because DifferentialThomas performs algebraic case splitting without imposing an ordered real field.\n"):
printf("BASE-STRATUM NOTE: r=0 is a codimension-one singular locus of the independent-coordinate chart, not an open two-variable differential component. It is retained in the audit as an excluded base stratum and is not divided into a fictitious PDE solution.\n"):
printf("FOLD NOTE: nops(AuxFold)=0 excludes only solutions whose image lies in A=0 on an open patch. It does not exclude a specially compatible crossing along a curve.\n"):
printf("CLOSURE NOTE: eta=0 and v=0 components solve polynomialized closures only; the original logarithmic/rational chart excludes them.\n"):

if Failures=0 then
    printf("All DifferentialThomas branch and compatibility checks passed.\n"):
else
    printf("DifferentialThomas certificate failed %d check(s).\n",Failures):
    error "DifferentialThomas certificate failed";
end if:
