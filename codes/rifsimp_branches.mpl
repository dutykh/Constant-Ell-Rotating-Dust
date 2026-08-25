# Branch-safe differential-algebra checks for the constant-ell VFE.
#
# Tested with Maple 2022.0. Run from this directory with
#
#     maple -q rifsimp_branches.mpl
#
# The rational VFE is polynomialized only after its excluded denominator
# factors have been recorded. The regular A<>0 and fold A=0 systems are sent
# to rifsimp separately. In particular, no result below is obtained by
# silently dividing by r, eta, v, A, or ell0.

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

isinconsistent := proc(result)
    if not type(result, table) then
        return false;
    end if;
    if not assigned(result['status']) then
        return false;
    end if;
    return evalb(result['status'] = "system is inconsistent");
end proc:

printf("Maple kernel version: %s\n", kernelopts(version)):
printf("Local physical base: r<>0; rational-field denominator: v<>0.\n"):
printf("The sign restrictions r>0 and 0<v<1 are analytical assumptions, not differential-polynomial equations.\n"):

# ----------------------------------------------------------------------
# 1. Polynomial numerator of the rational constant-ell VFE.
# ----------------------------------------------------------------------

V := v(r,z):
Vr := diff(V,r):
Vz := diff(V,z):
Vrr := diff(V,r$2):
Vzz := diff(V,z$2):

# A_v=v*A, where A is the principal coefficient in the rational VFE.
Av := 2*V+ell0*r*(1-V^2):
A := Av/V:

Erat := A*(Vrr+Vzz)
        +(2/r+3*ell0*(1/V-V))*Vr
        -ell0*r*(1/V^2+1)*(Vr^2+Vz^2)
        +2*ell0/r-2*V/r^2:

# Clearing is equivalent only under r<>0 and V<>0.
ClearingFactor := r^2*V^2:
P := expand(ClearingFactor*Erat):
Pexpected := r^2*V*Av*(Vrr+Vzz)
             +r*V*(2*V+3*ell0*r*(1-V^2))*Vr
             -ell0*r^3*(1+V^2)*(Vr^2+Vz^2)
             +2*ell0*r*V^2-2*V^3:

assertzero(P-Pexpected,
           "cleared polynomial is exactly r^2 v^2 times the rational VFE"):
asserttrue(has([r<>0,V<>0],r<>0) and has([r<>0,V<>0],V<>0),
           "both excluded denominator factors are recorded"):

# ----------------------------------------------------------------------
# 2. Polynomial auxiliary system and recovery of the nonlinear VFE.
# ----------------------------------------------------------------------

Eta := eta(r,z):
Y := y(r,z):
FF := F(r,z):

AuxAlgebraic := FF-2*Eta-ell0*r^2*Y+ell0*Eta^2/2:
LogR := Eta*diff(Y,r)-diff(Eta,r):
LogZ := Eta*diff(Y,z)-diff(Eta,z):
Harmonic := r*(diff(FF,r$2)+diff(FF,z$2))-diff(FF,r):
AuxA := 2*Eta+ell0*r^2-ell0*Eta^2:

AuxRegularInput := [AuxAlgebraic=0,LogR=0,LogZ=0,Harmonic=0,
                    r<>0,Eta<>0,AuxA<>0]:

try
    AuxRegular := DEtools:-rifsimp(
        AuxRegularInput,[FF,Y,Eta]):
    asserttrue(not isinconsistent(AuxRegular),
               "rifsimp regular auxiliary branch is consistent"):
    asserttrue(assigned(AuxRegular['Solved'])
               and nops(AuxRegular['Solved'])=4,
               "rifsimp returns the four triangular regular equations"):
    asserttrue(assigned(AuxRegular['Pivots'])
               and member(Eta<>0,AuxRegular['Pivots'])
               and member(AuxA<>0,AuxRegular['Pivots']),
               "rifsimp preserves eta<>0 and A_eta<>0 as pivots"):
    printf("rifsimp regular auxiliary output: %a\n", eval(AuxRegular)):
catch:
    printf("FAIL: rifsimp regular auxiliary branch raised %a\n",
           lastexception):
    Failures := Failures+1:
end try:

# Eliminate F and the first and second derivatives of y without using a
# logarithm. The numerator below is the differential-polynomial consequence
# returned in solved form by rifsimp.
Fexpression := 2*Eta+ell0*r^2*Y-ell0*Eta^2/2:
Hraw := r*(diff(Fexpression,r$2)+diff(Fexpression,z$2))
        -diff(Fexpression,r):
LogJetSub := {
    diff(Y,r)=diff(Eta,r)/Eta,
    diff(Y,z)=diff(Eta,z)/Eta,
    diff(Y,r$2)=diff(Eta,r$2)/Eta-diff(Eta,r)^2/Eta^2,
    diff(Y,z$2)=diff(Eta,z$2)/Eta-diff(Eta,z)^2/Eta^2,
    diff(Y,r,z)=diff(Eta,r,z)/Eta
                -diff(Eta,r)*diff(Eta,z)/Eta^2
}:
HEta := normal(subs(LogJetSub,Hraw)):
AuxNumerator := numer(HEta):

asserttrue(evalb(denom(HEta)=Eta^2),
           "auxiliary elimination records eta^2 as its exact denominator"):
assertzero(subs(Eta=r*V,AuxNumerator)-r^2*P,
           "auxiliary differential polynomial pulls back to r^2 times the cleared VFE"):

if assigned(AuxRegular) and assigned(AuxRegular['Solved']) then
    EtaSolved := select(e -> evalb(lhs(e)=diff(Eta,r$2)),
                        AuxRegular['Solved']):
    asserttrue(nops(EtaSolved)=1,
               "rifsimp solves exactly once for eta_rr on the regular branch"):
    if nops(EtaSolved)=1 then
        assertzero(subs(EtaSolved[1],AuxNumerator),
                   "rifsimp eta_rr equation annihilates the eliminated polynomial"):
    end if:
end if:

# The equality AuxA=0 is imposed as an equation on an open patch here. Its
# differential consequences make that fold-valued patch inconsistent. This
# does not rule out a codimension-one, even-contact crossing of the fold.
try
    AuxFold := DEtools:-rifsimp(
        [AuxAlgebraic=0,LogR=0,LogZ=0,Harmonic=0,
         r<>0,Eta<>0,AuxA=0],[FF,Y,Eta]):
    asserttrue(isinconsistent(AuxFold),
               "no two-dimensional auxiliary solution lies wholly in the physical fold"):
    printf("rifsimp fold-valued auxiliary output: %a\n", eval(AuxFold)):
catch:
    printf("FAIL: rifsimp auxiliary fold branch raised %a\n",
           lastexception):
    Failures := Failures+1:
end try:

# ell0=0 is run explicitly rather than being treated as a generic nonzero
# coefficient. It is a regular component whenever eta<>0.
try
    AuxEllZero := DEtools:-rifsimp(
        [subs(ell0=0,AuxAlgebraic)=0,LogR=0,LogZ=0,Harmonic=0,
         r<>0,Eta<>0],[FF,Y,Eta]):
    asserttrue(not isinconsistent(AuxEllZero),
               "ell0=0 auxiliary component is retained"):
    asserttrue(assigned(AuxEllZero['Pivots'])
               and member(Eta<>0,AuxEllZero['Pivots']),
               "ell0=0 component retains eta<>0"):
    asserttrue(member(FF=2*Eta,AuxEllZero['Solved']),
               "ell0=0 component gives F=2 eta"):
    printf("rifsimp ell0=0 auxiliary output: %a\n", eval(AuxEllZero)):
catch:
    printf("FAIL: rifsimp ell0=0 auxiliary branch raised %a\n",
           lastexception):
    Failures := Failures+1:
end try:

# ----------------------------------------------------------------------
# 3. Direct VFE branches and the first-prolongation obstruction.
# ----------------------------------------------------------------------

try
    VFERegular := DEtools:-rifsimp(
        [P=0,r<>0,V<>0,Av<>0],[V]):
    asserttrue(not isinconsistent(VFERegular),
               "regular polynomial VFE branch is consistent"):
    asserttrue(assigned(VFERegular['Pivots'])
               and member(V<>0,VFERegular['Pivots'])
               and member(expand(Av)<>0,VFERegular['Pivots']),
               "regular VFE output preserves v<>0 and A_v<>0"):
    VrrSolved := select(e -> evalb(lhs(e)=Vrr),VFERegular['Solved']):
    asserttrue(nops(VrrSolved)=1,
               "regular VFE solves exactly once for v_rr"):
    if nops(VrrSolved)=1 then
        assertzero(subs(VrrSolved[1],P),
                   "regular rifsimp solved equation satisfies the cleared VFE"):
    end if:
    printf("rifsimp regular VFE output: %a\n", eval(VFERegular)):
catch:
    printf("FAIL: rifsimp regular VFE branch raised %a\n",
           lastexception):
    Failures := Failures+1:
end try:

try
    VFEFold := DEtools:-rifsimp(
        [P=0,r<>0,V<>0,Av=0],[V]):
    asserttrue(isinconsistent(VFEFold),
               "no two-dimensional VFE solution lies wholly in A_v=0"):
    printf("rifsimp fold-valued VFE output: %a\n", eval(VFEFold)):
catch:
    printf("FAIL: rifsimp VFE fold branch raised %a\n", lastexception):
    Failures := Failures+1:
end try:

ConstJetSub := {Vr=0,Vz=0,Vrr=0,Vzz=0}:
Qconstant := ell0*r-V:
assertzero(subs(ConstJetSub,P)-2*V^2*Qconstant,
           "constant-field polynomial residual factors as 2 v^2 (ell0 r-v)"):
assertzero(subs(Vr=0,diff(Qconstant,r))-ell0,
           "first r-prolongation of ell0 r-v=0 gives ell0=0"):

try
    ConstRegular := DEtools:-rifsimp(
        [P=0,Vr=0,Vz=0,r<>0,V<>0,Av<>0],[V,ell0]):
    asserttrue(isinconsistent(ConstRegular),
               "nonzero constant field is inconsistent on the regular branch"):
catch:
    printf("FAIL: rifsimp constant regular branch raised %a\n",
           lastexception):
    Failures := Failures+1:
end try:

try
    ConstFold := DEtools:-rifsimp(
        [P=0,Vr=0,Vz=0,r<>0,V<>0,Av=0],[V,ell0]):
    asserttrue(isinconsistent(ConstFold),
               "nonzero constant field is inconsistent on the fold branch"):
catch:
    printf("FAIL: rifsimp constant fold branch raised %a\n",
           lastexception):
    Failures := Failures+1:
end try:

# Removing v<>0 exposes the closure introduced by multiplying the rational
# equation by v^2. It must be printed, not mistaken for a VFE solution.
try
    ConstCriticalNonzeroEll := DEtools:-rifsimp(
        [P=0,Vr=0,Vz=0,r<>0,ell0<>0],[V,ell0]):
    asserttrue(not isinconsistent(ConstCriticalNonzeroEll)
               and member(V=0,ConstCriticalNonzeroEll['Solved']),
               "cleared system exposes its v=0, ell0<>0 critical closure"):
    printf("rifsimp denominator-critical ell0<>0 output: %a\n",
           eval(ConstCriticalNonzeroEll)):
catch:
    printf("FAIL: rifsimp critical ell0<>0 branch raised %a\n",
           lastexception):
    Failures := Failures+1:
end try:

try
    ConstCriticalEllZero := DEtools:-rifsimp(
        [P=0,Vr=0,Vz=0,r<>0,ell0=0],[V,ell0]):
    asserttrue(not isinconsistent(ConstCriticalEllZero)
               and member(V=0,ConstCriticalEllZero['Solved'])
               and member(ell0=0,ConstCriticalEllZero['Solved']),
               "cleared system separately exposes its v=0, ell0=0 closure"):
    printf("rifsimp denominator-critical ell0=0 output: %a\n",
           eval(ConstCriticalEllZero)):
catch:
    printf("FAIL: rifsimp critical ell0=0 branch raised %a\n",
           lastexception):
    Failures := Failures+1:
end try:

# ----------------------------------------------------------------------
# 4. Exact quadrature compatibility/Frobenius-torsion identity.
# ----------------------------------------------------------------------

unassign('e','h','o'):
Efield := e(r,z):
hfield := h(Efield):
ofield := o(Efield):

gphiphi := (Efield^2-r^2)/hfield:
gtphi := Efield-ofield*gphiphi:
gtt := hfield-2*ofield*Efield+ofield^2*gphiphi:

Mr := (diff(gtt,r)*diff(gphiphi,r)
       -diff(gtt,z)*diff(gphiphi,z)
       -diff(gtphi,r)^2+diff(gtphi,z)^2)/(2*r):
Mz := (diff(gtt,z)*diff(gphiphi,r)
       +diff(gtt,r)*diff(gphiphi,z)
       -2*diff(gtphi,r)*diff(gtphi,z))/(2*r):

# h_eta/h=ell0 and o_eta=h_eta/(2 eta), with their first prolongations.
ReconstructionRules := {
    D(h)(Efield)=ell0*h(Efield),
    (D@@2)(h)(Efield)=ell0^2*h(Efield),
    D(o)(Efield)=ell0*h(Efield)/(2*Efield),
    (D@@2)(o)(Efield)=ell0^2*h(Efield)/(2*Efield)
                       -ell0*h(Efield)/(2*Efield^2)
}:

Torsion := simplify(subs(ReconstructionRules,
                         diff(Mr,z)-diff(Mz,r)),symbolic):
PhiE := 2*Efield+ell0*r^2*ln(Efield/etaStar)
        -ell0*Efield^2/2:
LFE := diff(PhiE,r$2)-diff(PhiE,r)/r+diff(PhiE,z$2):
AE := 2+ell0*r^2/Efield-ell0*Efield:

assertzero(Torsion-diff(Efield,z)*AE*LFE/(4*r),
           "meridional quadrature torsion equals eta_z A L(F)/(4r)"):

printf("NOTE: r<>0 is an independent-coordinate localization. rifsimp may omit it from Pivots because r cannot vanish identically on an open two-dimensional base.\n"):
printf("NOTE: fold inconsistency concerns a field constrained to A=0 on an open patch; it does not exclude a compatible crossing along a curve.\n"):
printf("NOTE: v=0 and eta=0 closure components are outside the logarithmic/rational physical chart.\n"):

if Failures=0 then
    printf("All branch-safe rifsimp and exact compatibility checks passed.\n"):
else
    printf("rifsimp certificate failed %d check(s).\n", Failures):
    error "branch-safe rifsimp certificate failed";
end if:
