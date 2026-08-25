# Symbolic checks for
# "Consistency, regularity, and global completion of constant-ell
# rotating-dust galaxy models"
#
# Run from Maple with
#     restart:
#     read "constant_ell_checks.mpl";
#
# The worksheet uses only standard Maple kernel commands.

restart:
interface(prettyprint=0):

canon := proc(expr)
    local res;
    res := simplify(normal(expand(expr)), symbolic);
    return res;
end proc:

assertzero := proc(expr, tag::string)
    local res;
    res := canon(expr);
    if res <> 0 then
        printf("FAIL: %s\nResidual: %a\n", tag, res);
        error "symbolic check failed";
    end if;
    printf("PASS: %s\n", tag);
    return NULL;
end proc:

# ----------------------------------------------------------------------
# 1. Exact and retained-order constant-ell operators.
# ----------------------------------------------------------------------

Eop := (2 + ell0*r*(1/V - V))*(Vrr + Vzz)
     + (2/r + 3*ell0*(1/V - V))*Vr
     - ell0*r*(1/V^2 + 1)*(Vr^2 + Vz^2)
     + 2*ell0/r - 2*V/r^2:

Top := (2 + ell0*r/V)*(Vrr + Vzz)
     + (2/r + 3*ell0/V)*Vr
     - ell0*r*(Vr^2 + Vz^2)/V^2
     + 2*ell0/r - 2*V/r^2:

Remainder := -ell0*(r*V*(Vrr + Vzz) + 3*V*Vr
                     + r*(Vr^2 + Vz^2)):

assertzero(Eop - Top - Remainder,
           "exact-minus-retained identity (Eq. remainder)"):

ConstSub := {V=v0, Vr=0, Vz=0, Vrr=0, Vzz=0}:
ConstResidual := 2*(ell0*r-v0)/r^2:
assertzero(subs(ConstSub, Top) - ConstResidual,
           "retained constant-field residual"):
assertzero(subs(ConstSub, Eop) - ConstResidual,
           "exact constant-field residual"):

# ----------------------------------------------------------------------
# 2. Killing-block determinant.
# ----------------------------------------------------------------------

gphiphi := (r^2-eta^2)/(-H):
gtphi   := eta-Omega*gphiphi:
gtt      := H-2*Omega*eta+Omega^2*gphiphi:
assertzero(gtt*gphiphi-gtphi^2+r^2,
           "Killing-block determinant det(G)=-r^2"):

# ----------------------------------------------------------------------
# 3. Density polynomial, factorization, and roots.
# ----------------------------------------------------------------------

Nv := 4*v0^2-4*v0^3*x-(1-v0^4)*x^2:
NvFactor := (2*v0-(1+v0^2)*x)*(2*v0+(1-v0^2)*x):
xminus := -2*v0/(1-v0^2):
xplus  :=  2*v0/(1+v0^2):

assertzero(Nv-NvFactor, "density factorization"):
assertzero(subs(x=xminus,Nv), "lower density root"):
assertzero(subs(x=xplus,Nv),  "upper density root"):

# ----------------------------------------------------------------------
# 4. Auxiliary-potential identity L Phi(r,r v)=r E[v].
# ----------------------------------------------------------------------

unassign('vf'):
etaField := r*vf(r,z):
Phi := 2*etaField
     + ell0*r^2*ln(etaField/etaStar)
     - ell0*etaField^2/2:

LPhi := diff(Phi,r$2)-diff(Phi,r)/r+diff(Phi,z$2):

Efun := (2 + ell0*r*(1/vf(r,z)-vf(r,z)))
        *(diff(vf(r,z),r$2)+diff(vf(r,z),z$2))
      + (2/r + 3*ell0*(1/vf(r,z)-vf(r,z)))
        *diff(vf(r,z),r)
      - ell0*r*(1/vf(r,z)^2+1)
        *(diff(vf(r,z),r)^2+diff(vf(r,z),z)^2)
      + 2*ell0/r - 2*vf(r,z)/r^2:

assertzero(LPhi-r*Efun,
           "auxiliary-potential identity L(Phi)=r E[v]"):

# ----------------------------------------------------------------------
# 5. Exact logarithmic equatorial identity.
# ----------------------------------------------------------------------

EqSub := {V=u,
          Vr=u*s/r,
          Vz=0,
          Vrr=u*(q+s^2-s)/r^2,
          Vzz=u*Z/r^2,
          ell0=y*u/r}:

EquatorialReduced := canon(r^2*subs(EqSub,Eop)/u):
EquatorialTarget := (2+y*(1-u^2))*(Z+q)
                  + 2*(1-y*u^2)*s^2
                  + 2*y*(1-u^2)*s
                  + 2*y-2:

assertzero(EquatorialReduced-EquatorialTarget,
           "exact logarithmic equatorial identity"):

AZeroRemainder := subs(y=-2/(1-u^2),
                       2*(1-y*u^2)*s^2
                     + 2*y*(1-u^2)*s
                     + 2*y-2):
AZeroFactor := (s+1)*((1+u^2)*s-(3-u^2)):
assertzero((1-u^2)*AZeroRemainder/2-AZeroFactor,
           "A=0 slope factorization"):

# ----------------------------------------------------------------------
# 6. Stationary equation for the optimized positive-ell span bound.
# ----------------------------------------------------------------------

Bplus := eps*(2+alpha)/((1+eps)*(1-eps-alpha))
       + ln(2/((1+vmin^2)*alpha))/(1-eps):
Keps := eps*(3-eps)*(1-eps)/(1+eps):
StationaryPolynomial := (1-eps-alpha)^2-Keps*alpha:
DerivativeForm := StationaryPolynomial/
                  (alpha*(eps-1)*(alpha+eps-1)^2):
assertzero(diff(Bplus,alpha)-DerivativeForm,
           "optimizer stationary equation"):

printf("All symbolic checks passed.\n"):
